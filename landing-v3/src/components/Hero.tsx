import { ASSETS, WHATSAPP_URL } from "../config";
import Arrow from "./Arrow";
import Chars from "./Chars";
import { TALK_EVENT } from "./VoiceDock";
import s from "./Hero.module.css";

export default function Hero() {
  return (
    <section className={s.hero} aria-labelledby="hero-title">
      <div className={s.top}>
        <p className={s.eyebrow} data-reveal="label">
          Asistente virtual de Gestión Humana · Prebel
        </p>
        <h1 id="hero-title" className={s.headline} data-reveal="headline" aria-label="Hola, soy SARHA. Estoy para ti.">
          <Chars text="Hola, soy SARHA." line={1} />
          <Chars text="Estoy para ti." line={2} className={s.blue} />
        </h1>
      </div>

      <div className={s.callout} data-reveal="callout">
        <div className={s.card}>
          <div className={s.cardRow}>
            <div className={s.cardText}>
              <span>24 horas</span>
              <span className={s.muted}>Todos los días</span>
            </div>
            <a href="#temas" className={s.more}>
              Ver <Arrow size={10.85} />
            </a>
          </div>
          <img src={ASSETS.eye} width={940} height={788} alt="Mirada de SARHA" className={s.cardImg} />
        </div>
        <div className={s.pager} aria-hidden="true">
          <span className={`${s.dot} ${s.dotActive}`} />
          <span className={s.dot} />
          <span className={s.dot} />
          <span className={s.dot} />
        </div>
      </div>

      <div className={s.bottom}>
        <p data-reveal="body">
          Servicios Automatizados de Recursos Humanos Ágiles. Consulta nómina, créditos, auxilios y trámites en WhatsApp, con la
          información oficial de Prebel.
        </p>
        <div className={s.buttons} data-reveal="buttons">
          <button type="button" className={`${s.btn} ${s.btnBlue}`} onClick={() => window.dispatchEvent(new Event(TALK_EVENT))}>
            Habla conmigo
          </button>
          <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className={`${s.btn} ${s.btnOutline}`}>
            <span className={s.long}>Escríbeme en </span>WhatsApp
          </a>
        </div>
      </div>

      <div className={s.scroll} data-reveal="scroll">
        <span>Desliza</span>
        <span className={s.scrollCircle} aria-hidden="true">
          ↓
        </span>
      </div>
    </section>
  );
}
