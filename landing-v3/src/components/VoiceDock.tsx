import { useEffect, useRef, useState } from "react";
import type { Caption, LiveVoice, VoiceStatus } from "../voice/liveVoice";
import ChatPanel from "./ChatPanel";
import s from "./VoiceDock.module.css";

/** Abre la voz desde cualquier botón de la página: window.dispatchEvent(new Event(TALK_EVENT)) */
export const TALK_EVENT = "sarha:talk";
/** Abre el chat escrito (el mismo bot de WhatsApp): window.dispatchEvent(new Event(CHAT_EVENT)) */
export const CHAT_EVENT = "sarha:chat";

const LABEL: Record<VoiceStatus, string> = {
  idle: "Toca para hablar con SARHA",
  connecting: "Conectando…",
  listening: "Te escucho",
  speaking: "SARHA está hablando",
  error: "No pude conectarme",
};


export default function VoiceDock() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<VoiceStatus>("idle");
  const [detail, setDetail] = useState("");
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [text, setText] = useState("");
  const [tab, setTab] = useState<"voz" | "chat">("voz");
  const [chatOpened, setChatOpened] = useState(false);
  const voiceRef = useRef<LiveVoice | null>(null);
  const ringRef = useRef<HTMLDivElement>(null);

  // El SDK de Google (~500 KB) se carga solo al activar la voz
  const start = async () => {
    setOpen(true);
    setTab("voz");
    setCaptions([]);
    if (!voiceRef.current) {
      setStatus("connecting");
      const { LiveVoice } = await import("../voice/liveVoice");
      voiceRef.current = new LiveVoice({
        onStatus: (st, d) => {
          setStatus(st);
          setDetail(d ?? "");
        },
        onCaption: (c) =>
          setCaptions((prev) => {
            const last = prev[prev.length - 1];
            const next = last && last.who === c.who ? [...prev.slice(0, -1), c] : [...prev, c];
            return next.slice(-4);
          }),
      });
    }
    voiceRef.current.start();
  };
  const stop = () => voiceRef.current?.stop();
  const openChat = () => {
    setOpen(true);
    setTab("chat");
    setChatOpened(true);
  };

  useEffect(() => {
    const onTalk = () => start();
    window.addEventListener(TALK_EVENT, onTalk);
    window.addEventListener(CHAT_EVENT, openChat);
    return () => {
      window.removeEventListener(TALK_EVENT, onTalk);
      window.removeEventListener(CHAT_EVENT, openChat);
      voiceRef.current?.stop();
    };
  }, []);

  // Aro que late con la voz de SARHA
  useEffect(() => {
    let raf = 0;
    let last = "";
    const tick = () => {
      raf = requestAnimationFrame(tick);
      const v = voiceRef.current;
      const lvl = v && v.status !== "idle" ? v.outputLevel() : 0;
      const val = lvl.toFixed(2);
      if (val !== last) {
        last = val;
        ringRef.current?.style.setProperty("--lvl", val);
      }
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  const live = status === "listening" || status === "speaking" || status === "connecting";

  return (
    <div className={s.dock} data-open={open} data-status={status}>
      {open && (
        <div className={s.panel} role="dialog" aria-label="Conversación con SARHA">
          <div className={s.head}>
            <div>
              <strong>SARHA</strong>
              <span className={s.state} aria-live="polite">
                {tab === "chat"
                  ? "Chat escrito · el mismo de WhatsApp"
                  : status === "error"
                    ? detail || LABEL.error
                    : detail || LABEL[status]}
              </span>
            </div>
            <button
              className={s.close}
              onClick={() => {
                stop();
                setOpen(false);
              }}
              aria-label="Cerrar"
            >
              ×
            </button>
          </div>
          <div className={s.tabs} role="tablist">
            <button role="tab" aria-selected={tab === "voz"} data-on={tab === "voz"} onClick={() => setTab("voz")}>
              Voz
            </button>
            <button role="tab" aria-selected={tab === "chat"} data-on={tab === "chat"} onClick={openChat}>
              Chat
            </button>
          </div>
          {chatOpened && (
            <div hidden={tab !== "chat"}>
              <ChatPanel />
            </div>
          )}
          {tab === "voz" && (
          <>
          <div className={s.captions} aria-live="polite">
            {captions.length === 0 && (
              <p className={s.hint}>
                {status === "connecting" ? "Preparando a SARHA con los documentos oficiales…" : "Pregúntale quién es, qué hace o cualquier duda de Gestión Humana."}
              </p>
            )}
            {captions.map((c, i) => (
              <p key={i} className={c.who === "sarha" ? s.sarha : s.user}>
                {c.text}
              </p>
            ))}
          </div>
          {(status === "listening" || status === "speaking") && (
            <form
              className={s.ask}
              onSubmit={(e) => {
                e.preventDefault();
                voiceRef.current?.sendText(text);
                setText("");
              }}
            >
              <input value={text} onChange={(e) => setText(e.target.value)} placeholder="O escríbele aquí…" aria-label="Escríbele a SARHA" />
              <button type="submit" aria-label="Enviar">
                ↑
              </button>
            </form>
          )}
          <div className={s.actions}>
            {live ? (
              <button className={s.stop} onClick={stop}>
                Terminar
              </button>
            ) : (
              <button className={s.go} onClick={start}>
                {status === "error" ? "Intentar de nuevo" : "Hablar"}
              </button>
            )}
          </div>
          <p className={s.note}>
            Responde solo con los documentos oficiales de Gestión Humana y puede equivocarse: valida con Gestión Humana. No guarda la
            conversación.
          </p>
          </>
          )}
        </div>
      )}
      <button className={s.launch} onClick={live ? stop : start} aria-label={live ? "Terminar conversación" : "Hablar con SARHA"}>
        <span className={s.ring} ref={ringRef} aria-hidden="true">
          <img src={`${import.meta.env.BASE_URL}sarha/avatar.webp`} width={240} height={240} alt="" className={s.face} />
          <span className={s.dot} />
        </span>
        <span className={s.launchText}>{live ? LABEL[status] : "Hablar con SARHA"}</span>
        <svg className={s.mic} viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 15a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3Zm5-3a5 5 0 0 1-10 0M12 17v4m-3 0h6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        </svg>
      </button>
    </div>
  );
}
