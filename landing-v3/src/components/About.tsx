import { WHATSAPP_URL } from "../config";
import { CHAT_EVENT, TALK_EVENT } from "./VoiceDock";
import Ethics from "./Ethics";
import s from "./About.module.css";

// Datos tomados de la ficha del Reto 7 y de las respuestas oficiales de Prebel a los equipos.
const STATS = [
  { n: "1.300", l: "colaboradores pueden consultarla" },
  { n: "24/7", l: "disponible, también en festivos" },
  { n: "4", l: "bases oficiales de Gestión Humana" },
  { n: "0", l: "datos personales pedidos o guardados" },
];

const CAN = [
  "Orientar sobre vinculación, nómina, cesantías, vacaciones e incapacidades.",
  "Explicar créditos, auxilios y beneficios con sus cifras, requisitos y plazos exactos.",
  "Decir a quién acudir según el tema y tu público: administrativo, operativo, impulso y mercadeo o practicante.",
  "Dar los canales oficiales ante accidentes, emergencias y acompañamiento psicológico, a cualquier hora.",
];

const CANNOT = [
  "Consultar salarios, desprendibles o saldos individuales.",
  "Recibir incapacidades, historias clínicas o documentos personales.",
  "Aprobar créditos, auxilios, permisos o vacaciones.",
  "Dar diagnósticos médicos o conceptos jurídicos personalizados.",
];

const STEPS = [
  { t: "Escribes o le hablas", d: "Por WhatsApp o con la voz desde esta página, con tus propias palabras." },
  { t: "Busca en las fuentes oficiales", d: "Solo en los documentos de Gestión Humana de Prebel. Sin internet y sin suposiciones." },
  { t: "Te responde y te orienta", d: "Con el dato exacto y el contacto responsable. Si no está documentado, te lo dice." },
];

const NEXT = [
  "Matriz de escalamiento configurable por tema y público.",
  "Horarios, tiempos de respuesta y valores de auxilios editables sin código.",
  "Reporte mensual anónimo de las preguntas sin respuesta.",
  "Integración con Prebelnet.",
];

const talk = () => window.dispatchEvent(new Event(TALK_EVENT));
const chat = () => window.dispatchEvent(new Event(CHAT_EVENT));

export default function About() {
  return (
    <div className={s.about}>
      <section className={s.block} aria-labelledby="que-es">
        <p className={s.eyebrow} data-fade>
          Gestión Humana Más Cerca de Ti
        </p>
        <h2 id="que-es" className={s.h2} data-fade>
          SARHA es la compañera de Gestión Humana <span className={s.blue}>que siempre está.</span>
        </h2>
        <div className={s.two}>
          <p className={s.lead} data-fade>
            Servicios Automatizados de Recursos Humanos Ágiles: una asistente virtual que responde las dudas del día a día sobre trámites,
            beneficios, créditos y nómina, en WhatsApp, el canal que todos usamos.
          </p>
          <p className={s.lead} data-fade>
            Nace del Reto 7 de EstudIA con Prebel S.A.S. BIC. Hoy esas consultas dependen de un asistente fuera de WhatsApp y de escribirle a
            la persona correcta. SARHA reúne todo en una fuente única, confiable y disponible a cualquier hora.
          </p>
        </div>
        <div className={s.stats}>
          {STATS.map((x) => (
            <div key={x.l} className={s.stat} data-fade>
              <strong>{x.n}</strong>
              <span>{x.l}</span>
            </div>
          ))}
        </div>
      </section>

      <section className={s.block} aria-labelledby="como">
        <p className={s.eyebrow} data-fade>
          Cómo responde
        </p>
        <h2 id="como" className={s.h2} data-fade>
          Tres pasos. <span className={s.blue}>Cero invenciones.</span>
        </h2>
        <ol className={s.steps}>
          {STEPS.map((x, i) => (
            <li key={x.t} className={s.step} data-fade>
              <span className={s.num}>{String(i + 1).padStart(2, "0")}</span>
              <h3>{x.t}</h3>
              <p>{x.d}</p>
            </li>
          ))}
        </ol>
        <p className={s.quote} data-fade>
          Si algo no está en los documentos, SARHA lo dice: «Lo siento, esa información no está disponible en este momento, ya que mi
          conocimiento se limita únicamente a los documentos cargados.»
        </p>
      </section>

      <section className={s.block} aria-labelledby="alcance">
        <p className={s.eyebrow} data-fade>
          Alcance
        </p>
        <h2 id="alcance" className={s.h2} data-fade>
          Te orienta. <span className={s.blue}>No reemplaza a Gestión Humana.</span>
        </h2>
        <div className={s.two}>
          <div className={s.card} data-fade>
            <h3>Lo que hace</h3>
            <ul>
              {CAN.map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </div>
          <div className={`${s.card} ${s.cardMuted}`} data-fade>
            <h3>Lo que no hace</h3>
            <ul>
              {CANNOT.map((x) => (
                <li key={x}>{x}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <Ethics />

      <section className={s.block} aria-labelledby="siguiente">
        <p className={s.eyebrow} data-fade>
          Próximas fases
        </p>
        <h2 id="siguiente" className={s.h2} data-fade>
          Hecha para crecer <span className={s.blue}>con Prebel.</span>
        </h2>
        <ul className={s.next}>
          {NEXT.map((x) => (
            <li key={x} data-fade>
              {x}
            </li>
          ))}
        </ul>
      </section>

      <section className={s.cta} aria-labelledby="habla">
        <h2 id="habla" className={s.h2} data-fade>
          Pregúntale tú mismo.
        </h2>
        <p className={s.lead} data-fade>
          Actívale la voz y pregúntale quién es, qué hace o cualquier duda de Gestión Humana. Ella te escucha y te responde.
        </p>
        <div className={s.buttons} data-fade>
          <button className={s.btnBlue} onClick={talk}>
            Hablar con SARHA
          </button>
          <button className={s.btnOutline} onClick={chat}>
            Chatear aquí
          </button>
          <a className={s.btnOutline} href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer">
            Habla con SARHA en WhatsApp
          </a>
          <a className={s.btnOutline} href="#presentacion">
            Ver la presentación
          </a>
        </div>
      </section>

      <footer className={s.footer}>
        <span>SARHA · Gestión Humana Más Cerca de Ti · Prebel S.A.S. BIC</span>
        <span>
          Prototipo académico y empresarial del programa EstudIA (Reto 7, Prebel S.A.S. BIC). Las respuestas se generan con inteligencia
          artificial solo sobre documentación interna no sensible autorizada, y pueden contener errores: valida con Gestión Humana. Este
          sitio no almacena conversaciones ni pide datos sensibles (Ley 1581 de 2012). La arquitectura está preparada para desplegarse en la
          infraestructura que aprueben TI y Legal de Prebel.
        </span>
      </footer>
    </div>
  );
}
