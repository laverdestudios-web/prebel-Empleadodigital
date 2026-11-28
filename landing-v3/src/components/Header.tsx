import { ASSETS, WHATSAPP_URL } from "../config";
import s from "./Header.module.css";

const LINKS = ["Nómina", "Créditos", "Auxilios", "Business Partner", "Ayuda"];

export default function Header() {
  return (
    <header className={s.header} data-reveal="header">
      <a href="#" className={s.brand} aria-label="Prebel · SARHA, inicio">
        <img src={ASSETS.logo} width={794} height={170} alt="Prebel" className={s.logo} />
        <span className={s.divider} aria-hidden="true" />
        <span className={s.sarha}>SARHA</span>
      </a>
      <nav className={s.nav} aria-label="Temas">
        {LINKS.map((l) => (
          <a key={l} href="#temas" className={s.link}>
            {l}
          </a>
        ))}
      </nav>
      <div className={s.actions}>
        <a href="#presentacion" className={s.present}>
          Presentación
        </a>
        <a href={WHATSAPP_URL} target="_blank" rel="noopener noreferrer" className={s.cta}>
          SARHA en WhatsApp
        </a>
      </div>
    </header>
  );
}
