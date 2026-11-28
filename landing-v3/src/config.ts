// Datos que el equipo cambia sin tocar componentes.

/** Número de WhatsApp de SARHA con indicativo, sin "+" ni espacios. PENDIENTE: número real de Prebel. */
export const WHATSAPP_NUMBER = "57XXXXXXXXXX";

export const WHATSAPP_URL = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent("Hola SARHA")}`;

const base = import.meta.env.BASE_URL;
export const ASSETS = {
  portrait: `${base}sarha-portrait.webp`, // 4096 × 2304
  eye: `${base}sarha-ojo.webp`, // 940 × 788
  logo: `${base}logo-prebel.png`, // 794 × 170, fondo transparente
};
