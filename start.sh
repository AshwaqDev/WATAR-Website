#!/bin/sh
# Starts the clinic adapter (private, inside the container) and then the
# public agent server: website + browser calls (/ws/web) + Twilio line (/twiml/pt).
set -e

: "${CLINIC_ADAPTER_KEY:=clinic-demo-key-2026}"
export CLINIC_ADAPTER_KEY
export CLINIC_ADAPTER_URL="http://127.0.0.1:3003"

# 1) clinic adapter — only reachable from inside the container
(cd clinic-adapter && HOST=127.0.0.1 PORT=3003 WATAR_KEY="$CLINIC_ADAPTER_KEY" \
    CLINIC_DB="${CLINIC_DB:-/app/clinic-adapter/clinic_demo.db}" python main.py) &

i=0
until python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3003/health')" 2>/dev/null; do
  i=$((i+1)); [ "$i" -ge 30 ] && { echo "clinic adapter did not start"; exit 1; }
  sleep 1
done
echo "clinic adapter ready"

# 2) keep-awake: Render's free plan sleeps after 15 min without visits.
#    Ping our own public address every 10 min (Render sets RENDER_EXTERNAL_URL).
#    Turn off with KEEP_AWAKE=0 (e.g. after upgrading to a paid instance).
if [ -n "$RENDER_EXTERNAL_URL" ] && [ "${KEEP_AWAKE:-1}" != "0" ]; then
  (
    while true; do
      sleep "${KEEP_AWAKE_SECONDS:-600}"
      python -c "import urllib.request; urllib.request.urlopen('$RENDER_EXTERNAL_URL/health', timeout=30)" \
        >/dev/null 2>&1 && echo "keep-awake ping ok" || echo "keep-awake ping failed"
    done
  ) &
  echo "keep-awake: pinging $RENDER_EXTERNAL_URL/health every ${KEEP_AWAKE_SECONDS:-600}s"
fi

# 3) agent server on Render's public port
cd agent
exec python -m uvicorn web_bridge:app --host 0.0.0.0 --port "${PORT:-8080}" --proxy-headers --forwarded-allow-ips="*"
