import type { FocusEvent, PointerEvent } from "react";
import Arrow from "./Arrow";
import s from "./Features.module.css";

/** Las 4 fuentes oficiales de Gestión Humana (los documentos de docs/). Una tarjeta por capa. */
export const FEATURES = [
  {
    title: "Vinculación y Nómina",
    copy: "Certificados laborales, retiro de cesantías, EPS, caja de compensación, vacaciones e incapacidades.",
  },
  {
    title: "Créditos",
    copy: "Educación, computador y calamidad de mascotas al 0 %, vivienda y casos especiales de salud.",
  },
  {
    title: "Auxilios y Beneficios",
    copy: "Auxilio visual u odontológico de $332.000, alimentación, nacimiento, matrimonio y bienestar.",
  },
  {
    title: "Business Partner",
    copy: "Tu Business Partner por sede, licencias, accidentes de trabajo y el Pacto Colectivo.",
  },
];

type Props = { active: number | null; setActive: (i: number | null) => void };

export default function Features({ active, setActive }: Props) {
  return (
    <section className={s.features} id="temas" aria-labelledby="features-title">
      <h2 id="features-title" className={s.heading}>
        <span className={s.line}>Cuatro fuentes.</span>
        <span className={`${s.line} ${s.blue}`}>Una sola respuesta.</span>
      </h2>
      <p className={s.lead}>
        Cada capa de SARHA es un documento oficial de Gestión Humana de Prebel. Juntas forman una fuente única de consulta, en
        WhatsApp y a cualquier hora.
      </p>
      <div className={s.cards}>
        {FEATURES.map((f, i) => (
          <article
            key={f.title}
            tabIndex={0}
            className={s.card}
            data-active={active === i}
            onPointerEnter={(e: PointerEvent) => e.pointerType === "mouse" && setActive(i)}
            onPointerLeave={(e: PointerEvent) => e.pointerType === "mouse" && setActive(null)}
            onFocus={() => setActive(i)}
            onBlur={(e: FocusEvent) => {
              if (!e.currentTarget.contains(e.relatedTarget)) setActive(null);
            }}
          >
            <div className={s.head}>
              <h3 className={s.title}>{f.title}</h3>
              <span className={s.num}>{String(i + 1).padStart(2, "0")}</span>
            </div>
            <p className={s.copy}>{f.copy}</p>
            <div className={s.arrowRow}>
              <div className={s.arrowInner}>
                <Arrow size={20} />
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
