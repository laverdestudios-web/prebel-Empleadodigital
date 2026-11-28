# Desplegar la web de SARHA en Netlify

La web (`landing-v3/`) y su presentación (`#presentacion`) se publican en Netlify. El chatbot de WhatsApp y el chat escrito usan el backend en Python (`Sarha_Empleado_Digital_Prebel/`), que **no corre en Netlify**: necesita un servidor propio (el de Prebel o uno gratuito como Render).

## Qué funciona con cada parte

| Parte | Dónde corre | Funciona solo con Netlify |
|---|---|---|
| Web, escena del ojo, secciones de ética y privacidad | Netlify (archivos estáticos) | Sí |
| Presentación (botón «Presentación», `#presentacion`) | Netlify (archivos estáticos) | Sí |
| Botón «Habla con SARHA» → WhatsApp | Enlace a `wa.me` | Sí (WhatsApp responde solo si el backend está encendido) |
| Voz «Habla conmigo» (Gemini Live) | Netlify Function `/api/live-token` | Sí, con `GEMINI_API_KEY` |
| Chat escrito de la web | Backend Python `/api/chat` | No: necesita `VITE_SARHA_API_URL` |
| Respuestas en WhatsApp (Twilio) | Backend Python `/twilio/webhook` | No: necesita el backend con HTTPS |

## 1. Publicar la web en Netlify

1. En Netlify: **Add new site → Import an existing project → GitHub** y elegir `laverdestudios-web/prebel-Empleadodigital`.
2. Rama: la de integración (`sarha-landing-v3`, o `main` cuando se fusione).
3. No hay que escribir nada más en la configuración de build: `netlify.toml` (en la raíz del repo) ya dice `base = landing-v3`, `npm run build`, `publish = dist`, la función de voz y Node 22.
4. En **Site configuration → Environment variables**:

| Variable | Para qué | Ejemplo |
|---|---|---|
| `GEMINI_API_KEY` | Voz de SARHA. Key gratis de Google AI Studio. Nunca llega al navegador | `AIza…` |
| `VITE_SARHA_API_URL` | Chat escrito: URL del backend terminada en `/api` | `https://sarha-backend.onrender.com/api` |
| `VITE_SARHA_WA_NUMBER` | Opcional. Línea de WhatsApp, con indicativo y sin «+» | `12272405417` |

Las variables `VITE_*` se leen al construir: si se cambian, hay que volver a desplegar (**Deploys → Trigger deploy**).

## 2. Encender el backend (chat y WhatsApp)

Opción para la demo, gratis: **Render**, con el `Dockerfile` que ya existe.

1. En Render: **New → Web Service → GitHub** y elegir el repo y la rama.
2. **Root directory**: `Sarha_Empleado_Digital_Prebel`. **Runtime**: Docker. Puerto: `8000`.
3. Variables de entorno (ver `Sarha_Empleado_Digital_Prebel/.env.example`):
   - `CORS_ORIGINS=https://<tu-sitio>.netlify.app` (la URL que da Netlify; sin esto el chat de la web es bloqueado por el navegador).
   - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` y `TWILIO_WHATSAPP_NUMBER` de la cuenta de Twilio.
4. En Twilio, el webhook de la línea apunta a `https://<backend>.onrender.com/twilio/webhook` (POST).
5. En Netlify, `VITE_SARHA_API_URL=https://<backend>.onrender.com/api` y volver a desplegar.

> El plan gratis de Render apaga el servicio tras 15 minutos sin uso y tarda cerca de un minuto en despertar. **Antes de presentar, abran `https://<backend>.onrender.com/health`** para despertarlo.
>
> Para producción, el mismo contenedor corre en el servidor de Prebel con `docker compose up -d --build`.

## 3. Revisar antes de presentar

- [ ] La web abre y el botón **Presentación** muestra las 8 diapositivas (flechas, **F** pantalla completa, **N** notas, **Esc** volver).
- [ ] **Habla conmigo** pide el micrófono y SARHA responde con su voz.
- [ ] En el chat escrito, «Hola» muestra el menú de 5 opciones.
- [ ] Desde el celular, el QR de la última diapositiva abre WhatsApp con «Hola», y SARHA responde.
- [ ] En WhatsApp: `Hola → 1 → 2 → 1` da los requisitos de retiro de cesantías por compra de vivienda, y «¿Cuál es el salario mínimo actual?» da el mensaje oficial de «no disponible».

## Si cambia el número de WhatsApp

1. `VITE_SARHA_WA_NUMBER` en Netlify.
2. El QR de la presentación es un archivo fijo: `public/presentacion/qr-whatsapp.svg`. Hay que generarlo de nuevo con el enlace `https://wa.me/<número>?text=Hola`, y cambiar `FACTS.waDisplay` en `src/presentation/content.ts`.

## Pendiente del equipo

Las dos copias de los documentos (`docs/` y `Sarha_Empleado_Digital_Prebel/docs/`) no coinciden: la del bot cambió a Lucía Mejía por Johanna Puentes y Cristina Giraldo. En `Auxilios_y_beneficios_Prebel_20260310.md`, línea 50, el correo de incapacidades de practicantes (PP) se cambió a johanna.puentes sin respaldo en las respuestas de Prebel (Johanna atiende impulso y mercadeo). El equipo debe decidir una sola versión aprobada y sincronizar las dos copias.
