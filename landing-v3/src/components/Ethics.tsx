import s from "./Ethics.module.css";

// Fuente: docs/politica-etica-seguridad-prebel.md (marco del equipo) cruzado con las respuestas oficiales de Prebel.
// En la web pública van los responsables por tema, pero no sus correos ni celulares: SARHA los da cuando se le pregunta.

const PRINCIPLES = [
  { t: "Transparencia", d: "Desde el primer mensaje sabes que hablas con una inteligencia artificial de apoyo, nunca con una persona." },
  { t: "Fidelidad documental", d: "Responde solo con los documentos autorizados por Prebel. Sin internet, sin suposiciones. Si el dato no existe, lo dice." },
  { t: "No sustitución", d: "Orienta sobre procedimientos y responsables. No toma decisiones laborales, médicas ni disciplinarias, ni hace trámites." },
  { t: "Equidad y accesibilidad", d: "Igual para personal administrativo, operativo, de impulso y mercadeo y practicantes, por texto o por voz." },
  { t: "Vinculación directa", d: "Aclara que los beneficios y auxilios aplican solo a colaboradores contratados directamente por Prebel." },
];

const PRIVACY = [
  { t: "No pide datos personales", d: "Ni cédula, ni salario, ni desprendibles, ni historias clínicas. Si alguien los comparte, le recuerda no hacerlo y le da el canal autorizado." },
  { t: "No guarda conversaciones", d: "En esta fase el público del colaborador (PA, PO, PI o PP) solo vive durante la conversación y se descarta al terminar." },
  { t: "No recibe documentos", d: "Incapacidades, fórmulas o cédulas se radican por el canal oficial de Gestión Humana, nunca por el asistente." },
  { t: "El celular no es una clave", d: "Un número de teléfono no basta para entregar información individual: toda consulta personal va al responsable de Gestión Humana." },
  { t: "Métricas anónimas", d: "Se propone un reporte mensual agregado, sin nombres ni teléfonos: temas consultados y preguntas sin cobertura, para mejorar los documentos." },
];

const URGENT = [
  { s: "Emergencia médica en sede (Productora, Comercial, Rionegro)", c: "Servicio EMI, a través del brigadista de la sede" },
  { s: "Accidente o incidente de trabajo", c: "Reportar a la Business Partner, al personal de SST y al jefe directo (reporte a la ARL)" },
  { s: "Acompañamiento psicológico", c: "Red de Amor: 604 360 7080, opción 3" },
  { s: "Programa Desahogadero", c: "Bienestar: 310 405 7760" },
];

const MATRIX = [
  { n: "Angela Quintero", p: "Vinculación, certificados y seguridad social", a: "PO" },
  { n: "Michell Román", p: "Vinculación, certificados y seguridad social", a: "PA · PI" },
  { n: "Shirley Silgado", p: "Nómina administrativa", a: "PA" },
  { n: "Yasmín Yepes", p: "Nómina operativa", a: "PO" },
  { n: "Cristina Giraldo", p: "Nómina de impulso y mercadeo y practicantes", a: "PI · PP" },
  { n: "Johanna Puentes", p: "Cesantías e incapacidades de impulso y mercadeo", a: "Todos · PI" },
  { n: "Linda Salamanca", p: "Vacaciones de impulso y mercadeo", a: "PI" },
  { n: "Stefanny Pulgarín", p: "Bienestar, créditos, auxilios, beneficios y registro de mascotas", a: "Todos" },
  { n: "Nathalia León", p: "Business Partner · sedes Productora y Rionegro", a: "Todos" },
  { n: "Laura Jaramillo", p: "Business Partner · sede Comercial y fuera de sede", a: "Todos" },
];

export default function Ethics() {
  return (
    <>
      <section className={s.block} aria-labelledby="etica">
        <p className={s.eyebrow} data-fade>
          Ética e IA responsable
        </p>
        <h2 id="etica" className={s.h2} data-fade>
          Una IA que sabe <span className={s.blue}>hasta dónde llega.</span>
        </h2>
        <div className={s.grid5}>
          {PRINCIPLES.map((x, i) => (
            <div key={x.t} className={s.card} data-fade>
              <span className={s.num}>{String(i + 1).padStart(2, "0")}</span>
              <h3>{x.t}</h3>
              <p>{x.d}</p>
            </div>
          ))}
        </div>
      </section>

      <section className={s.block} aria-labelledby="privacidad">
        <p className={s.eyebrow} data-fade>
          Privacidad · Ley 1581 de 2012 y Decreto 1377 de 2013
        </p>
        <h2 id="privacidad" className={s.h2} data-fade>
          Tus datos, <span className={s.blue}>fuera del chat.</span>
        </h2>
        <p className={s.lead} data-fade>
          Los colaboradores de Prebel ya autorizaron el tratamiento de sus datos con la compañía. SARHA va más allá: está diseñada para no
          necesitarlos.
        </p>
        <div className={s.grid2}>
          {PRIVACY.map((x) => (
            <div key={x.t} className={s.row} data-fade>
              <span className={s.lock} aria-hidden="true" />
              <div>
                <h3>{x.t}</h3>
                <p>{x.d}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className={s.block} aria-labelledby="urgencias">
        <p className={s.eyebrow} data-fade>
          Protocolo de urgencias · sin horario
        </p>
        <h2 id="urgencias" className={s.h2} data-fade>
          En una emergencia, <span className={s.blue}>el canal correcto al instante.</span>
        </h2>
        <div className={s.urgent}>
          {URGENT.map((x) => (
            <div key={x.s} className={s.urgentRow} data-fade>
              <span>{x.s}</span>
              <strong>{x.c}</strong>
            </div>
          ))}
        </div>
        <p className={s.small} data-fade>
          SARHA responde consultas informativas 24/7. Cuando un trámite necesita a una persona, avisa que se atiende en el horario de
          Gestión Humana, sin prometer respuesta inmediata.
        </p>
      </section>

      <section className={s.block} aria-labelledby="matriz">
        <p className={s.eyebrow} data-fade>
          Matriz de escalamiento
        </p>
        <h2 id="matriz" className={s.h2} data-fade>
          Siempre sabe <span className={s.blue}>a quién llevarte.</span>
        </h2>
        <p className={s.lead} data-fade>
          Según el tema y tu público (PA administrativo, PO operativo, PI impulso y mercadeo, PP practicante), SARHA te da el responsable con
          su correo y teléfono exactos. La matriz es configurable: se actualiza sin tocar el código.
        </p>
        <div className={s.matrix} data-fade>
          {MATRIX.map((x) => (
            <div key={x.n} className={s.mRow}>
              <strong>{x.n}</strong>
              <span>{x.p}</span>
              <em>{x.a}</em>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
