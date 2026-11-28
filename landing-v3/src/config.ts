// Datos que el equipo cambia sin tocar componentes (se pueden fijar con variables VITE_* en landing-v3/.env.local).

/** Línea de WhatsApp de SARHA (Twilio + Meta Business), con indicativo y sin "+". */
export const WHATSAPP_NUMBER = (import.meta.env.VITE_SARHA_WA_NUMBER as string | undefined) ?? "12272405417";

export const WHATSAPP_URL = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent("Hola")}`;

/**
 * API del chatbot de SARHA (Sarha_Empleado_Digital_Prebel, FastAPI). Es el MISMO motor que responde en WhatsApp.
 * En desarrollo "/api" pasa por el proxy de vite.config.ts hacia http://localhost:8000.
 * En producción: VITE_SARHA_API_URL=https://<dominio-del-backend>/api
 */
export const SARHA_API_URL = ((import.meta.env.VITE_SARHA_API_URL as string | undefined) ?? "/api").replace(/\/$/, "");

const base = import.meta.env.BASE_URL;
export const ASSETS = {
  portrait: `${base}sarha-portrait.webp`, // 4096 × 2304
  eye: `${base}sarha-ojo.webp`, // 940 × 788
  logo: `${base}logo-prebel.png`, // 794 × 170, fondo transparente
};
