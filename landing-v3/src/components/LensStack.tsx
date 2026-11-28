import type { CSSProperties } from "react";
import { FEATURES } from "./Features";
import s from "./LensStack.module.css";

/** Color de cada capa (paleta Prebel), en el orden de las tarjetas. */
const TINTS = ["#5A84AC", "#6EA190", "#85BFD3", "#E39581"];
const OFFSETS = [-1.5, -0.5, 0.5, 1.5];
/** Nombre corto en cada hoja: las hojas se montan unas sobre otras y solo se ve su borde izquierdo. */
const SHORT = ["Nómina", "Créditos", "Auxilios", "Partner"];

/**
 * Las 4 fuentes oficiales como hojas de vidrio dibujadas por código.
 * Juntas (--spread: 0) se leen como una sola pieza: la fuente única; al abrirse muestran sus 4 capas.
 */
export default function LensStack({ active }: { active: number | null }) {
  return (
    <div className={s.box} data-scene="lens" aria-hidden="true">
      {FEATURES.map((f, i) => (
        <div key={f.title} className={s.layer} style={{ "--i": OFFSETS[i] } as CSSProperties}>
          <Sheet tint={TINTS[i]} index={i} label={SHORT[i]} />
          <span className={s.dot} data-on={active === i} />
        </div>
      ))}
    </div>
  );
}

function Sheet({ tint, index, label }: { tint: string; index: number; label: string }) {
  const id = `sheet-${index}`;
  const lines = [0, 1, 2, 3, 4, 5].map((n) => ({ y: 172 + n * 34, w: n % 3 === 2 ? 150 : n === 5 ? 110 : 214 }));
  return (
    <svg viewBox="0 0 250 360" className={s.sheet}>
      <defs>
        <linearGradient id={`${id}-fill`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#ffffff" stopOpacity="0.92" />
          <stop offset="1" stopColor={tint} stopOpacity="0.28" />
        </linearGradient>
        <linearGradient id={`${id}-edge`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#ffffff" stopOpacity="1" />
          <stop offset="1" stopColor={tint} stopOpacity="0.7" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="248" height="358" rx="26" fill={`url(#${id}-fill)`} stroke={`url(#${id}-edge)`} strokeWidth="1.5" />
      <rect x="18" y="18" width="214" height="96" rx="16" fill={tint} fillOpacity="0.9" />
      <text x="34" y="54" fill="#fff" fontSize="15" fontFamily="var(--font)" fontWeight="500">
        {String(index + 1).padStart(2, "0")}
      </text>
      <text x="34" y="92" fill="#fff" fontSize="17" fontFamily="var(--font)" fontWeight="500">
        {label}
      </text>
      {lines.map((l, n) => (
        <rect key={n} x="18" y={l.y} width={l.w} height="10" rx="5" fill={tint} fillOpacity="0.35" />
      ))}
    </svg>
  );
}
