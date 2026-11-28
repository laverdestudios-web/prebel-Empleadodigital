// Conversación por voz con SARHA usando la Gemini Live API.
// El navegador pide un token efímero a /api/live-token (la API key nunca llega al navegador),
// manda el micrófono en PCM 16 kHz y reproduce la voz de SARHA (PCM 24 kHz).
import { GoogleGenAI, Modality, type LiveServerMessage, type Session } from "@google/genai";

export const LIVE_MODEL = "gemini-2.5-flash-native-audio-latest";
const TOKEN_URL = import.meta.env.VITE_TOKEN_URL ?? `${import.meta.env.BASE_URL}api/live-token`;
const GREETING =
  "(La persona acaba de activar tu voz en la página web de SARHA. Salúdala, preséntate en dos frases y pregúntale en qué le puedes ayudar.)";
/** Mientras SARHA habla, el micrófono solo pasa si la persona habla fuerte (para interrumpirla sin eco). */
const BARGE_IN_RMS = 0.06;

export type VoiceStatus = "idle" | "connecting" | "listening" | "speaking" | "error";
export type Caption = { who: "user" | "sarha"; text: string };

type Handlers = {
  onStatus: (s: VoiceStatus, detail?: string) => void;
  onCaption: (c: Caption) => void;
};

const CAPTURE_WORKLET = `
class SarhaCapture extends AudioWorkletProcessor {
  process(inputs) { const ch = inputs[0] && inputs[0][0]; if (ch) this.port.postMessage(ch.slice(0)); return true; }
}
registerProcessor("sarha-capture", SarhaCapture);`;

function toBase64(bytes: Uint8Array) {
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(s);
}

function downsample(input: Float32Array, from: number, to: number) {
  if (from === to) return input;
  const ratio = from / to;
  const out = new Float32Array(Math.floor(input.length / ratio));
  for (let i = 0; i < out.length; i++) out[i] = input[Math.floor(i * ratio)];
  return out;
}

export class LiveVoice {
  private session: Session | null = null;
  private stream: MediaStream | null = null;
  private inCtx: AudioContext | null = null;
  private outCtx: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private outGain: GainNode | null = null;
  private sources = new Set<AudioBufferSourceNode>();
  private nextTime = 0;
  private pending: Float32Array[] = [];
  private pendingLen = 0;
  private speakingUntil = 0;
  private turnText: Caption | null = null;
  private level = new Float32Array(512);
  status: VoiceStatus = "idle";
  micBlocked = false;

  private h: Handlers;
  constructor(h: Handlers) {
    this.h = h;
  }

  private set(s: VoiceStatus, detail?: string) {
    this.status = s;
    this.h.onStatus(s, detail);
  }

  /** Nivel de la voz de SARHA (0..1) para animar su cara y el aro. */
  outputLevel() {
    if (!this.analyser) return 0;
    this.analyser.getFloatTimeDomainData(this.level);
    let sum = 0;
    for (const v of this.level) sum += v * v;
    return Math.min(1, Math.sqrt(sum / this.level.length) * 4);
  }

  isSpeaking() {
    return this.outCtx ? this.outCtx.currentTime < this.speakingUntil : false;
  }

  async start() {
    if (this.status !== "idle" && this.status !== "error") return;
    this.set("connecting");
    try {
      // Micrófono y audio primero (necesitan el clic del usuario). Sin micrófono, igual se le puede escribir.
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 },
        });
      } catch {
        this.stream = null;
        this.micBlocked = true;
      }
      this.outCtx = new AudioContext({ sampleRate: 24000 });
      this.outGain = this.outCtx.createGain();
      this.analyser = this.outCtx.createAnalyser();
      this.analyser.fftSize = 512;
      this.outGain.connect(this.analyser).connect(this.outCtx.destination);
      this.inCtx = new AudioContext();
      const url = URL.createObjectURL(new Blob([CAPTURE_WORKLET], { type: "application/javascript" }));
      await this.inCtx.audioWorklet.addModule(url);
      URL.revokeObjectURL(url);

      const r = await fetch(TOKEN_URL, { method: "POST" });
      if (!r.ok) throw new Error(`No se pudo obtener el permiso de voz (${r.status})`);
      const { token } = (await r.json()) as { token: string };

      const ai = new GoogleGenAI({ apiKey: token, httpOptions: { apiVersion: "v1alpha" } });
      this.session = await ai.live.connect({
        model: LIVE_MODEL,
        config: { responseModalities: [Modality.AUDIO] },
        callbacks: {
          onmessage: (m) => this.onMessage(m),
          onerror: (e) => this.fail(e.message || "Error de conexión"),
          onclose: (e) => {
            if (this.status !== "idle") e.code === 1000 ? this.stop() : this.fail(e.reason || "Se cerró la conexión");
          },
        },
      });

      if (this.stream) {
        const src = this.inCtx.createMediaStreamSource(this.stream);
        const node = new AudioWorkletNode(this.inCtx, "sarha-capture");
        const rate = this.inCtx.sampleRate;
        node.port.onmessage = (e: MessageEvent<Float32Array>) => this.onMic(downsample(e.data, rate, 16000));
        src.connect(node);
      }

      this.set("listening", this.micBlocked ? "Sin micrófono: escríbele abajo y te responde con su voz." : undefined);
      this.session.sendClientContent({ turns: [{ role: "user", parts: [{ text: GREETING }] }], turnComplete: true });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      this.fail(msg);
    }
  }

  /** Pregunta escrita (respaldo si no hay micrófono). */
  sendText(text: string) {
    if (!this.session || !text.trim()) return;
    this.flush();
    this.turnText = null;
    this.caption("user", text.trim());
    this.turnText = null;
    this.session.sendClientContent({ turns: [{ role: "user", parts: [{ text: text.trim() }] }], turnComplete: true });
  }

  private onMic(chunk: Float32Array) {
    if (!this.session) return;
    this.pending.push(chunk);
    this.pendingLen += chunk.length;
    if (this.pendingLen < 1600) return; // ~100 ms
    const all = new Float32Array(this.pendingLen);
    let o = 0;
    for (const c of this.pending) {
      all.set(c, o);
      o += c.length;
    }
    this.pending = [];
    this.pendingLen = 0;
    let rms = 0;
    for (const v of all) rms += v * v;
    rms = Math.sqrt(rms / all.length);
    const pcm = new Int16Array(all.length);
    const mute = this.isSpeaking() && rms < BARGE_IN_RMS;
    if (!mute) for (let i = 0; i < all.length; i++) pcm[i] = Math.max(-1, Math.min(1, all[i])) * 0x7fff;
    this.session.sendRealtimeInput({ audio: { data: toBase64(new Uint8Array(pcm.buffer)), mimeType: "audio/pcm;rate=16000" } });
  }

  private onMessage(m: LiveServerMessage) {
    const sc = m.serverContent;
    if (!sc) return;
    if (sc.interrupted) this.flush();
    for (const p of sc.modelTurn?.parts ?? []) if (p.inlineData?.data) this.play(p.inlineData.data);
    if (sc.inputTranscription?.text) this.caption("user", sc.inputTranscription.text);
    if (sc.outputTranscription?.text) this.caption("sarha", sc.outputTranscription.text);
    if (sc.turnComplete) this.turnText = null;
  }

  private caption(who: Caption["who"], text: string) {
    if (!this.turnText || this.turnText.who !== who) this.turnText = { who, text: "" };
    this.turnText.text += text;
    this.h.onCaption({ ...this.turnText });
  }

  private play(b64: string) {
    if (!this.outCtx || !this.outGain) return;
    const bin = atob(b64);
    const n = bin.length >> 1;
    const buf = this.outCtx.createBuffer(1, n, 24000);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < n; i++) {
      const v = (bin.charCodeAt(2 * i) | (bin.charCodeAt(2 * i + 1) << 8)) << 16 >> 16;
      ch[i] = v / 0x8000;
    }
    const src = this.outCtx.createBufferSource();
    src.buffer = buf;
    src.connect(this.outGain);
    const t = Math.max(this.nextTime, this.outCtx.currentTime + 0.04);
    src.start(t);
    this.nextTime = t + buf.duration;
    this.speakingUntil = this.nextTime;
    this.sources.add(src);
    src.onended = () => this.sources.delete(src);
    if (this.status !== "speaking") this.set("speaking");
    window.clearTimeout(this.backTimer);
    this.backTimer = window.setTimeout(() => this.status === "speaking" && this.set("listening"), (this.nextTime - this.outCtx.currentTime) * 1000 + 300);
  }
  private backTimer = 0;

  private flush() {
    for (const s of this.sources) s.stop();
    this.sources.clear();
    this.nextTime = 0;
    this.speakingUntil = 0;
    if (this.status === "speaking") this.set("listening");
  }

  private fail(msg: string) {
    this.cleanup();
    this.set("error", msg);
  }

  stop() {
    this.cleanup();
    this.set("idle");
  }

  private cleanup() {
    window.clearTimeout(this.backTimer);
    try {
      this.session?.close();
    } catch {
      /* ya cerrada */
    }
    this.session = null;
    this.flush();
    this.stream?.getTracks().forEach((t) => t.stop());
    this.stream = null;
    this.inCtx?.close();
    this.outCtx?.close();
    this.inCtx = this.outCtx = null;
    this.analyser = this.outGain = null;
  }
}
