# Python 3.11: the phone bridge uses `audioop`, which was removed in Python 3.13.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Riyadh

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY agent/ agent/
COPY clinic-adapter/ clinic-adapter/
COPY start.sh .
RUN chmod +x start.sh

# Render sets $PORT; 8080 is the local default.
ENV PORT=8080
EXPOSE 8080
CMD ["./start.sh"]
