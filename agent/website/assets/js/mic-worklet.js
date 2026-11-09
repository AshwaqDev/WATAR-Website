// Captures mic audio, resamples to 16 kHz mono PCM16, posts ~100 ms chunks.
class MicCapture extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.target = options.processorOptions?.targetRate || 16000;
    this.ratio = sampleRate / this.target;
    this.pos = 0;
    this.chunk = new Int16Array(this.target / 10);
    this.n = 0;
  }
  process(inputs) {
    const ch = inputs[0]?.[0];
    if (!ch) return true;
    // Linear-interpolation resampler (index -1 = last sample of previous block)
    const at = (k) => (k < 0 ? this.last || 0 : ch[k]);
    while (this.pos < ch.length - 1) {
      const i = Math.floor(this.pos), f = this.pos - i;
      const s = at(i) * (1 - f) + at(i + 1) * f;
      this.chunk[this.n++] = Math.max(-1, Math.min(1, s)) * 0x7fff;
      if (this.n === this.chunk.length) {
        this.port.postMessage(this.chunk.buffer, [this.chunk.buffer]);
        this.chunk = new Int16Array(this.target / 10);
        this.n = 0;
      }
      this.pos += this.ratio;
    }
    this.pos -= ch.length;
    this.last = ch[ch.length - 1];
    return true;
  }
}
registerProcessor("mic-capture", MicCapture);
