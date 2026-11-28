import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { ASSETS, WHATSAPP_URL } from "../config";
import { FACTS, NOTES, TEAM } from "./content";
import s from "./Presentation.module.css";

const BASE = import.meta.env.BASE_URL;
const IMG = {
  web: `${BASE}presentacion/web-sarha.webp`,
  qr: `${BASE}presentacion/qr-whatsapp.svg`,
};

/** Lienzo de diseño: cada diapositiva mide 1920 × 1080 y se escala a la pantalla. */
const W = 1920;
const H = 1080;

type Slide = { id: keyof typeof NOTES; label: string; tone?: "dark"; body: ReactNode };

const SLIDES: Slide[] = [
  {
    id: "gancho",
    label: "Gancho y equipo",
    body: (
      <>
        <img className={s.heroImg} src={ASSETS.portrait} alt="" aria-hidden="true" />
        <div className={s.heroVeil} aria-hidden="true" />
        <div className={s.heroText}>
          <p className={s.eyebrow}>Reto 7 · EstudIA · Prebel S.A.S. BIC</p>
          <h1 className={s.hook}>
            ¿A quién le pregunta un trabajador de Prebel, a las 6 a.m., <span className={s.blue}>cómo retirar sus cesantías?</span>
          </h1>
          <p className={s.lead}>
            Hoy no hay una respuesta única. Por eso creamos <b>SARHA</b>, la asistente de Gestión Humana de Prebel en WhatsApp y en la web.
          </p>
        </div>
        <div className={s.team}>
          <p className={s.label}>Nuestro equipo</p>
          <div className={s.teamGrid}>
            {TEAM.filter((m) => m.name.trim()).map((m) => (
              <div key={m.name} className={s.member}>
                <strong>{m.name}</strong>
                <span>{m.role}</span>
              </div>
            ))}
          </div>
        </div>
      </>
    ),
  },
  {
    id: "problema",
    label: "El problema",
    body: (
      <>
        <p className={s.eyebrow}>El problema · a quién afecta</p>
        <h2 className={s.h2}>
          Un problema de dos lados: <span className={s.blue}>quien pregunta y quien responde.</span>
        </h2>
        <div className={s.pills}>
          <span className={s.pill}>PA · Administrativo</span>
          <span className={s.pill}>PO · Operativo</span>
          <span className={s.pill}>PI · Impulso y mercadeo</span>
          <span className={s.pill}>PP · Practicantes</span>
          <span className={`${s.pill} ${s.pillSolid}`}>{FACTS.collaborators} colaboradores</span>
        </div>
        <div className={s.grid3}>
          <article className={s.card}>
            <span className={s.num}>01</span>
            <h3>Los colaboradores</h3>
            <ul>
              <li>Tienen dudas a diario: certificados, cesantías, vacaciones, incapacidades, créditos y auxilios.</li>
              <li>No saben cómo gestionar su trámite ni a quién acudir.</li>
            </ul>
          </article>
          <article className={`${s.card} ${s.cardBlue}`}>
            <span className={s.num}>02</span>
            <h3>Gestión Humana</h3>
            <ul>
              <li>Cada caso va a un responsable distinto según tema y público: {FACTS.responsibles} personas, sin un correo único.</li>
              <li>No tiene métricas: no sabe qué se pregunta ni qué queda sin respuesta.</li>
            </ul>
          </article>
          <article className={s.card}>
            <span className={s.num}>03</span>
            <h3>La solución de hoy</h3>
            <ul>
              <li>Un GPT público en ChatGPT.</li>
              <li>Por fuera de WhatsApp, el canal de todos.</li>
              <li>Por fuera de la infraestructura de Prebel.</li>
            </ul>
          </article>
        </div>
      </>
    ),
  },
  {
    id: "solucion",
    label: "La solución",
    body: (
      <div className={s.split}>
        <div className={s.avatarRing}>
          <img className={s.avatar} src={ASSETS.portrait} alt="SARHA, asistente de Gestión Humana de Prebel" />
        </div>
        <div className={s.grow}>
          <p className={s.eyebrow}>La solución</p>
          <h2 className={s.display}>
            Hola, soy <span className={s.blue}>SARHA.</span>
          </h2>
          <p className={s.lead}>Servicios Automatizados de Recursos Humanos Ágiles, en WhatsApp y en la web.</p>
          <div className={s.grid2}>
            <article className={s.cardSm}>
              <h3>Menú numérico 1–5</h3>
              <p>Nómina, créditos, auxilios, Business Partner, y contactos y urgencias. Sin escribir largo.</p>
            </article>
            <article className={s.cardSm}>
              <h3>Pregunta libre</h3>
              <p>Por texto o por voz, con tus propias palabras y a cualquier hora.</p>
            </article>
            <article className={s.cardSm}>
              <h3>Solo información oficial</h3>
              <p>Responde con los documentos de Gestión Humana, cita la fuente y no inventa.</p>
            </article>
            <article className={s.cardSm}>
              <h3>Te lleva a la persona correcta</h3>
              <p>Te da el responsable según tu tema y tu público, sin pedirte datos personales.</p>
            </article>
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "proceso",
    label: "Cómo llegamos",
    body: (
      <>
        <p className={s.eyebrow}>El proceso · cómo llegamos al MVP</p>
        <h2 className={s.h2}>
          De los documentos oficiales <span className={s.blue}>a un chatbot probado en vivo.</span>
        </h2>
        <div className={s.grid4}>
          <article className={s.card}>
            <span className={s.num}>01</span>
            <h3>Base oficial</h3>
            <p>
              {FACTS.docs} documentos de Gestión Humana, indexados en {FACTS.sections} secciones.
            </p>
          </article>
          <article className={s.card}>
            <span className={s.num}>02</span>
            <h3>Motor propio</h3>
            <p>Búsqueda local sin internet y un menú que recuerda dónde va cada celular.</p>
          </article>
          <article className={s.card}>
            <span className={s.num}>03</span>
            <h3>Pruebas</h3>
            <p>
              {FACTS.testsBot + FACTS.testsServer} pruebas automáticas en verde: {FACTS.testsBot} del bot y {FACTS.testsServer} del servidor.
            </p>
          </article>
          <article className={s.card}>
            <span className={s.num}>04</span>
            <h3>En vivo</h3>
            <p>WhatsApp real con Twilio y Meta: Hola → 1 → 2 → 1.</p>
          </article>
        </div>
        <div className={s.band}>
          <b>Listo para producción:</b> Docker en el servidor de Prebel. Para actualizar a SARHA, Gestión Humana edita sus documentos, sin tocar
          código.
        </div>
      </>
    ),
  },
  {
    id: "web",
    label: "La web de SARHA",
    body: (
      <div className={s.split}>
        <div className={s.webText}>
          <p className={s.eyebrow}>La web de SARHA</p>
          <h2 className={s.h2}>
            Otra puerta, <span className={s.blue}>la misma respuesta.</span>
          </h2>
          <ul className={s.dots}>
            <li>
              <b>Habla conmigo:</b> le preguntas con la voz y te responde con la suya.
            </li>
            <li>
              <b>Chat escrito:</b> el mismo motor y el mismo menú de WhatsApp.
            </li>
            <li>
              <b>Escríbeme en WhatsApp:</b> abre el chat con «Hola» listo.
            </li>
            <li>
              <b>Ética y privacidad:</b> qué hace, qué no hace, urgencias y a quién acudir.
            </li>
          </ul>
        </div>
        <div className={s.shotFrame}>
          <img className={s.shot} src={IMG.web} alt="Portada de la web de SARHA" />
        </div>
      </div>
    ),
  },
  {
    id: "funciona",
    label: "Cómo funciona",
    body: (
      <>
        <p className={s.eyebrow}>Cómo funciona · el desarrollo</p>
        <h2 className={s.h2}>
          Tres capas, <span className={s.blue}>una sola fuente.</span>
        </h2>
        <div className={s.flow}>
          <article className={s.card}>
            <h3>1. Canales</h3>
            <p className={s.chip}>WhatsApp (Twilio + Meta)</p>
            <p className={s.chip}>Chat en la web</p>
            <p className={s.chip}>Voz en la web (Gemini Live)</p>
          </article>
          <span className={s.arrow} aria-hidden="true">
            →
          </span>
          <article className={`${s.card} ${s.cardBlue}`}>
            <h3>2. Motor SARHA (Python)</h3>
            <p className={s.chip}>Menú con sesión por celular</p>
            <p className={s.chip}>Búsqueda local en los documentos</p>
            <p className={s.chip}>Respuesta con fuente y responsable</p>
          </article>
          <span className={s.arrow} aria-hidden="true">
            →
          </span>
          <article className={s.card}>
            <h3>3. Datos y despliegue</h3>
            <p className={s.chip}>Documentos oficiales, solo lectura</p>
            <p className={s.chip}>Docker en el servidor de Prebel</p>
            <p className={s.chip}>Reporte anónimo de consultas</p>
          </article>
        </div>
        <div className={s.band}>
          <b>Controles:</b> mensaje oficial si algo no está en los documentos · respuestas largas divididas para WhatsApp · no pide ni guarda
          datos personales (Ley 1581).
        </div>
      </>
    ),
  },
  {
    id: "valor",
    label: "Propuesta de valor",
    body: (
      <>
        <p className={s.eyebrow}>Propuesta de valor</p>
        <h2 className={s.h2}>
          Qué cambia <span className={s.blue}>con SARHA.</span>
        </h2>
        <div className={s.table} role="table" aria-label="Hoy frente a SARHA">
          <div className={`${s.tr} ${s.th}`} role="row">
            <span role="columnheader" />
            <span role="columnheader">Hoy (GPT público)</span>
            <span role="columnheader">Con SARHA</span>
          </div>
          {[
            ["Canal", "ChatGPT, fuera del día a día", "WhatsApp, chat y voz en la web"],
            ["Respuestas", "Generales, sin fuente", "Solo documentos oficiales, con fuente y responsable"],
            ["Gestión Humana", "Sin métricas de lo que se pregunta", "Reporte anónimo de temas y preguntas sin respuesta"],
            ["Infraestructura", "Plataforma externa", "Servidor de Prebel con Docker, sin suscripción"],
          ].map(([k, a, b]) => (
            <div key={k} className={s.tr} role="row">
              <span role="cell" className={s.tk}>
                {k}
              </span>
              <span role="cell">{a}</span>
              <span role="cell" className={s.tb}>
                {b}
              </span>
            </div>
          ))}
        </div>
      </>
    ),
  },
  {
    id: "cierre",
    label: "Cierre",
    body: (
      <div className={s.split}>
        <div className={s.grow}>
          <p className={s.eyebrow}>Cierre · ¿y ahora?</p>
          <h2 className={s.display}>
            Esa pregunta <span className={s.blue}>ya tiene respuesta.</span>
          </h2>
          <p className={s.lead}>
            ¿A quién le pregunta un trabajador de Prebel, a las 6 a.m., cómo retirar sus cesantías? <b>Ahora, a SARHA, desde su WhatsApp.</b>
          </p>
          <ol className={s.steps}>
            <li>Abrimos la web de SARHA.</li>
            <li>Clic en «Habla con SARHA» y se abre WhatsApp.</li>
            <li>Escribimos «Hola» y le preguntamos en vivo.</li>
          </ol>
          <div className={s.ctaRow}>
            <a className={s.btnBlue} href="#">
              Ver la web
            </a>
            <a className={s.btnOutline} href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer">
              Escribir a SARHA
            </a>
          </div>
        </div>
        <div className={s.qrCard}>
          <img src={IMG.qr} alt="Código QR para escribirle a SARHA por WhatsApp" className={s.qr} />
          <strong>Escanea y escríbele «Hola»</strong>
          <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer">
            {FACTS.waDisplay}
          </a>
        </div>
      </div>
    ),
  },
];

/** Número de diapositiva desde el hash: #presentacion/3 → índice 2. */
function indexFromHash() {
  const n = Number(window.location.hash.split("/")[1]);
  return Number.isInteger(n) && n >= 1 && n <= SLIDES.length ? n - 1 : 0;
}

export default function Presentation() {
  const [i, setI] = useState(indexFromHash);
  const [scale, setScale] = useState(1);
  const [notes, setNotes] = useState(false);
  const touch = useRef<number | null>(null);

  const go = useCallback((n: number) => {
    const next = Math.max(0, Math.min(SLIDES.length - 1, n));
    setI(next);
    window.history.replaceState(null, "", `#presentacion/${next + 1}`);
  }, []);

  const fullscreen = useCallback(() => {
    if (document.fullscreenElement) void document.exitFullscreen();
    else void document.documentElement.requestFullscreen?.().catch(() => undefined);
  }, []);

  // Escala del lienzo 1920 × 1080 a la ventana
  useLayoutEffect(() => {
    const fit = () => setScale(Math.min(window.innerWidth / W, window.innerHeight / H));
    fit();
    window.addEventListener("resize", fit);
    return () => window.removeEventListener("resize", fit);
  }, []);

  // Teclado: flechas, espacio, Inicio/Fin, F (pantalla completa), N (notas), Esc (volver a la web)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const k = e.key;
      if (k === "ArrowRight" || k === "PageDown" || k === " ") {
        e.preventDefault();
        go(i + 1);
      } else if (k === "ArrowLeft" || k === "PageUp") {
        e.preventDefault();
        go(i - 1);
      } else if (k === "Home") go(0);
      else if (k === "End") go(SLIDES.length - 1);
      else if (k === "f" || k === "F") fullscreen();
      else if (k === "n" || k === "N") setNotes((v) => !v);
      else if (k === "Escape" && !document.fullscreenElement) window.location.hash = "";
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [i, go, fullscreen]);

  useEffect(() => {
    document.title = `Presentación · ${SLIDES[i].label} · SARHA Prebel`;
  }, [i]);

  const slide = SLIDES[i];

  return (
    <div
      className={s.viewport}
      onTouchStart={(e) => (touch.current = e.touches[0].clientX)}
      onTouchEnd={(e) => {
        if (touch.current === null) return;
        const dx = e.changedTouches[0].clientX - touch.current;
        if (Math.abs(dx) > 50) go(dx < 0 ? i + 1 : i - 1);
        touch.current = null;
      }}
    >
      <div className={s.stage} style={{ width: W, height: H, transform: `translate(-50%, -50%) scale(${scale})` }}>
        <section key={slide.id} className={s.slide} aria-roledescription="diapositiva" aria-label={`${i + 1} de ${SLIDES.length}: ${slide.label}`}>
          {slide.body}
          <footer className={s.slideFoot}>
            <img src={ASSETS.logo} alt="Prebel" className={s.footLogo} />
            <span>SARHA · Gestión Humana Más Cerca de Ti</span>
            <span>
              {i + 1} / {SLIDES.length}
            </span>
          </footer>
        </section>
      </div>

      {notes && (
        <aside className={s.notes} aria-label="Notas del orador">
          <strong>Notas · {slide.label}</strong>
          <p>{NOTES[slide.id]}</p>
        </aside>
      )}

      <nav className={s.controls} aria-label="Controles de la presentación">
        <a className={s.ctrl} href="#" title="Volver a la web (Esc)">
          ← Web
        </a>
        <button type="button" className={s.ctrl} onClick={() => go(i - 1)} disabled={i === 0} aria-label="Diapositiva anterior">
          ‹
        </button>
        <span className={s.counter} aria-live="polite">
          {i + 1} / {SLIDES.length}
        </span>
        <button type="button" className={s.ctrl} onClick={() => go(i + 1)} disabled={i === SLIDES.length - 1} aria-label="Diapositiva siguiente">
          ›
        </button>
        <button type="button" className={s.ctrl} onClick={() => setNotes((v) => !v)} aria-pressed={notes} title="Notas del orador (N)">
          Notas
        </button>
        <button type="button" className={s.ctrl} onClick={fullscreen} title="Pantalla completa (F)">
          ⛶
        </button>
      </nav>
    </div>
  );
}
