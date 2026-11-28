import { Fragment, useEffect, useRef, useState, type ReactNode } from "react";
import { askSarha, type MenuOption } from "../chat/sarhaApi";
import { WHATSAPP_URL } from "../config";
import s from "./ChatPanel.module.css";

type Msg = { who: "user" | "sarha"; text: string; options?: MenuOption[]; chips?: string[] };

/** Markdown mínimo y seguro: **negrita** y saltos de línea (React escapa el resto). */
function render(text: string): ReactNode {
  return text.split("\n").map((line, i, all) => (
    <Fragment key={i}>
      {line.split(/(\*\*[^*]+\*\*)/g).map((part, j) =>
        part.startsWith("**") && part.endsWith("**") ? <strong key={j}>{part.slice(2, -2)}</strong> : <Fragment key={j}>{part}</Fragment>,
      )}
      {i < all.length - 1 && <br />}
    </Fragment>
  ));
}

/** Chat escrito con el mismo motor que responde en WhatsApp: menú numérico con botones + pregunta libre. */
export default function ChatPanel() {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  const started = useRef(false);

  const send = async (message: string, show = true) => {
    const m = message.trim();
    if (!m || busy) return;
    setError("");
    if (show) setMsgs((p) => [...p, { who: "user", text: m }]);
    setBusy(true);
    try {
      const r = await askSarha(m);
      setMsgs((p) => [...p, { who: "sarha", text: r.answer, options: r.menu_options, chips: r.suggested_questions?.slice(0, 3) }]);
    } catch {
      setError("No pude conectarme con el chatbot de SARHA. Revisa que el servidor esté encendido o escríbele por WhatsApp.");
    } finally {
      setBusy(false);
    }
  };

  // Al abrir: saludo con el menú principal (igual que en WhatsApp)
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    send("hola", false);
  }, []);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [msgs, busy]);

  const last = msgs[msgs.length - 1];

  return (
    <div className={s.chat}>
      <div className={s.list} ref={listRef} aria-live="polite">
        {msgs.map((m, i) => (
          <div key={i} className={m.who === "sarha" ? s.sarha : s.user}>
            {render(m.text)}
          </div>
        ))}
        {busy && <div className={`${s.sarha} ${s.typing}`}>SARHA está escribiendo…</div>}
        {error && (
          <div className={s.error}>
            {error}{" "}
            <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer">
              Abrir WhatsApp
            </a>
          </div>
        )}
      </div>

      {!busy && last?.who === "sarha" && (last.options?.length || last.chips?.length) ? (
        <div className={s.options}>
          {last.options?.map((o) => (
            <button key={o.number} onClick={() => send(o.number)}>
              <b>{o.number}</b> {o.label}
            </button>
          ))}
          {!last.options?.length &&
            last.chips?.map((c) => (
              <button key={c} onClick={() => send(c)}>
                {c}
              </button>
            ))}
        </div>
      ) : null}

      <form
        className={s.ask}
        onSubmit={(e) => {
          e.preventDefault();
          send(text);
          setText("");
        }}
      >
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Escribe tu pregunta o un número…" aria-label="Escríbele a SARHA" maxLength={2000} />
        <button type="submit" aria-label="Enviar" disabled={busy}>
          ↑
        </button>
      </form>
      <p className={s.note}>
        Por tu seguridad, no compartas cédula, salarios, desprendibles ni historias clínicas (Ley 1581 de 2012). Mismo asistente que en{" "}
        <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer">
          WhatsApp
        </a>
        .
      </p>
    </div>
  );
}
