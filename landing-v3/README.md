# Landing SARHA v3 · Prebel

Landing de scroll de SARHA, el asistente de Gestión Humana de Prebel. El retrato de SARHA se enfoca saliendo de un desenfoque. Al hacer scroll, la cámara entra en su ojo y un escáner "lee" la pregunta. Después aparece una sola pieza, la fuente única de consulta, que se abre en las 4 capas oficiales: Nómina, Créditos, Auxilios y Business Partner. Todo el movimiento es código; no hay video.

Stack: Vite + React 19 + TypeScript (estricto) + GSAP 3 con ScrollTrigger. CSS plano: tokens globales + CSS Modules.

## Correr

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # genera dist/, estático: sirve en Nginx, Docker o cualquier hosting
```

## Dónde se cambia cada cosa

| Qué | Archivo |
|---|---|
| **Número de WhatsApp** (pendiente) | `src/config.ts` → `WHATSAPP_NUMBER` |
| Textos del inicio | `src/components/Hero.tsx` |
| Título, texto y las 4 tarjetas | `src/components/Features.tsx` (`FEATURES`) |
| Enlaces del menú | `src/components/Header.tsx` |
| Colores, letras, tamaños | `src/styles/tokens.css` |
| Tiempos de la escena de scroll | `src/App.tsx` (`SCENE`) |
| Iris al que entra el zoom y encuadre | `src/components/PortraitCanvas.tsx` (`IRIS`, `LEFT_BIAS`, `FACE_X`) |
| Escáner del ojo | `src/components/Hud.tsx` |
| Las 4 hojas (capas) | `src/components/LensStack.tsx` |

## Imágenes (`public/`)

- `sarha-portrait.webp`, 4096 × 2304: SARHA generada con Higgsfield Soul 2.0 y subida a 4K. Su iris está en (2160, 943), con radio 51. Si se cambia la foto, hay que actualizar `IRIS`.
- `sarha-ojo.webp`, 940 × 788: recorte del ojo para la tarjeta del inicio.
- `logo-prebel.png`, 300 × 63.

## Rendimiento

- El canvas solo se redibuja cuando cambia el scroll o el tamaño de la ventana.
- No hay `backdrop-filter` encima del video, porque obliga a recalcular el desenfoque en cada cuadro.
- Las hojas no usan sombra con `filter`.
- El hover de las tarjetas solo anima color, `translate` y `opacity`; el alto no cambia, así que la fila no se reacomoda.
- Medido en Chrome: 59 fps al hacer scroll y 60 fps en el hover.

## Accesibilidad y movimiento

- Con "reducir movimiento" activado en el sistema no hay zoom, escáner ni desenfoques: el contenido aparece con un fundido y las capas ya salen abiertas.
- Las tarjetas se activan con el mouse, con Tab o al tocarlas en el celular.
- El cursor propio solo aparece en equipos con mouse.

## Portada y zoom al ojo

- La portada es el primer cuadro del video, quieto: no sigue el cursor (Juan lo descartó).
- `public/sarha/zoom.mp4`: el video **MAGI-2** (5 s, 130 cuadros, hecho desde la foto de SARHA) que entra a su ojo izquierdo. Está codificado con todos sus cuadros independientes (`-g 1`), así que saltar a cualquier punto es instantáneo y gasta poca memoria. No se reproduce: el scroll elige el cuadro y se dibuja en el canvas. Para regenerarlo: `ffmpeg -i casting/sarha-zoom-magi2.mp4 -an -vf scale=1440:810 -c:v libx264 -crf 22 -g 1 -movflags +faststart zoom.mp4`. `IRIS_TRACK` (`PortraitCanvas.tsx`) guarda la posición y el tamaño del iris por cuadro, para que el escáner caiga justo sobre él. El video original está en `PREBEL/casting/sarha-zoom-magi2.mp4`.
- `public/sarha/avatar.webp`: la cara de SARHA en el botón de voz.

## Hablar con SARHA (voz)

- Botón «Habla conmigo» en el inicio y el círculo flotante «Hablar con SARHA». Usa la **Gemini Live API** (`gemini-2.5-flash-native-audio-latest`, voz `Kore`) con la key gratis de Google AI Studio.
- La key **nunca llega al navegador**: el navegador pide un token efímero a `/api/live-token`. En desarrollo lo da `vite.config.ts`, que lee `GEMINI_API_KEY` de `PREBEL/.env`. En producción lo da `worker/index.ts`.
- SARHA responde **solo** con `docs/` (Vinculación y Nómina, Créditos, Auxilios y Beneficios, Glosario BP y las aclaraciones oficiales de Prebel). Las instrucciones están en `api/liveToken.ts`. Si cambia un documento, se corre `npm run knowledge`; el build también lo hace.
- Si el navegador no da permiso al micrófono, se le puede escribir y responde con su voz.

## Publicarla gratis (Cloudflare Workers)

```bash
npm run build
npx wrangler login
npx wrangler secret put GEMINI_API_KEY
npx wrangler deploy
```

## Chat escrito (el mismo bot de WhatsApp)

- En el panel de SARHA hay dos pestañas: **Voz** (Gemini Live) y **Chat**. El chat usa `POST /api/chat` del backend `Sarha_Empleado_Digital_Prebel/`, el mismo motor que responde en WhatsApp. Trae el menú numérico (1–5, 0, 00) como botones, deja escribir libre y muestra el aviso de privacidad (Ley 1581).
- Cada pestaña del navegador tiene su `session_id` (en `sessionStorage`) para que el menú recuerde dónde va. No identifica a la persona y no se guarda nada.
- Variables (en `landing-v3/.env.local`, opcionales):
  - `VITE_SARHA_API_URL`: URL del backend. Por defecto es `/api`, que en desarrollo pasa por el proxy de `vite.config.ts` hacia `http://localhost:8000`.
  - `VITE_SARHA_WA_NUMBER`: línea de WhatsApp. Por defecto `12272405417` (Twilio + Meta Business).
- El backend permite el origen de la landing con `CORS_ORIGINS` (ver `Sarha_Empleado_Digital_Prebel/.env.example`). En producción se agrega ahí el dominio real.

## Demo completa (backend + landing)

```bash
# Terminal 1: backend de SARHA (chat web y WhatsApp)
cd Sarha_Empleado_Digital_Prebel
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# Terminal 2: landing
cd landing-v3
npm install
npm run dev      # abrir http://localhost:5173 en Chrome
```
