import s from "./Chars.module.css";

/** Una línea del titular partida en un span por carácter, para la entrada letra por letra. */
export default function Chars({ text, line, className }: { text: string; line: number; className?: string }) {
  return (
    <span className={`${s.line} ${className ?? ""}`} data-line={line} aria-hidden="true">
      {Array.from(text).map((c, i) => (
        <span key={i} className={s.char} data-char="">
          {c}
        </span>
      ))}
    </span>
  );
}
