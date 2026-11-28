# Reporte de revisión · SARHA (28-11-2026)

Para el equipo, y en especial para quien pone operativo el chatbot de WhatsApp (Antigravity IDE). Rama de integración: **`sarha-landing-v3`**. Al final hay un **prompt listo para el agente de IA**.

## 1. Qué se hizo hoy en `sarha-landing-v3`

| Cambio | Dónde | Afecta al bot de WhatsApp |
|---|---|---|
| Se integraron las ramas `sarha-prebel-whatsapp-v2` (Twilio), `claude/ecstatic-einstein` y `claude/vigilant-ptolemy` | todo el repo | No: se integraron sin conflictos |
| Se fusionó el PR #3 (corrige el test del correo de Angela Quintero) | `Sarha_Empleado_Digital_Prebel/tests/test_chatbot.py` | Solo el test (18/18) |
| **CORS** para que la landing use `POST /api/chat` | `Sarha_Empleado_Digital_Prebel/app/main.py` (+11 líneas), `app/config.py` (`CORS_ORIGINS`), `.env.example` | **No** (comprobado abajo) |
| Pestaña **Chat** en la landing con el mismo motor de WhatsApp; botones a `wa.me/12272405417` | `landing-v3/` | No |
| Optimización: zoom como `zoom.mp4`, canvas sin redibujar de más, hover sin reacomodar la fila | `landing-v3/` | No |
| Decisión del equipo: el motor se queda en **Gemini**; `claude/lucid-hypatia` no se integra | — | No |

El PR #4 (presentación en la web + Netlify) **no toca** `Sarha_Empleado_Digital_Prebel/`, `server/`, `brain/` ni `docs/`.

Comparado con la rama original de maoescabe, el bot solo cambió en esto (`git diff origin/sarha-prebel-whatsapp-v2 origin/sarha-landing-v3 -- Sarha_Empleado_Digital_Prebel/`):
```
.env.example  +2   (CORS_ORIGINS)
app/config.py +9   (lee CORS_ORIGINS)
app/main.py   +11  (CORSMiddleware)
tests/test_chatbot.py  1 línea (correo en minúsculas)
```

## 2. Prueba del webhook de Twilio con el código de `sarha-landing-v3`

Se simularon mensajes como los que manda Twilio (`POST /twilio/webhook`, form-urlencoded) con `fastapi.testclient`:

| Mensaje | Respuesta | Resultado |
|---|---|---|
| `Hola` | 200, TwiML, menú principal de 5 opciones | ✅ |
| `1` → `2` → `1` | Vinculación y Nómina → Retiro de cesantías → Compra de vivienda | ✅ |
| `¿Cuál es el salario mínimo actual?` | Mensaje oficial de «no disponible» | ✅ |
| Foto (`NumMedia=1`) | Aviso de privacidad, sin descargar la imagen | ✅ |
| Aviso de entrega (`MessageStatus=delivered`) | `<Response></Response>` vacío (se ignora) | ✅ |
| Petición con `Origin` de otro sitio | Responde normal: el CORS no afecta a Twilio | ✅ |

Pruebas automáticas: `server/tests` + `brain/tests` **33/33**; `Sarha_Empleado_Digital_Prebel/tests` **18/18**.

**Conclusión:** el código del webhook responde bien. Si WhatsApp no contesta, la causa está en dónde corre el backend o en la configuración de Twilio, no en el código integrado.

## 3. Por qué WhatsApp puede no responder (revisar en este orden)

1. **El backend no es público.** Twilio no llega a `localhost`. Necesita una URL **HTTPS pública**: Render, el servidor de Prebel o un túnel (ngrok / Cloudflare Tunnel) mientras se prueba.
2. **URL del webhook en Twilio.** En la consola de Twilio, la línea `+1 227 240 5417` (o el Sandbox) debe apuntar a `https://<backend>/twilio/webhook` con método **POST**. No debe apuntar a `server/app.py` (ese es otro webhook, el de Meta Cloud API) ni a una URL de ngrok vieja. Cada vez que ngrok se reinicia, la URL cambia.
3. **Firma de Twilio detrás de un proxy.** Con `TWILIO_VALIDATE_SIGNATURE=true` detrás de Render o ngrok, la URL que ve FastAPI es `http://` y la que firmó Twilio es `https://`. Resultado: **403 en todos los mensajes**. Para la demo, déjalo en `false`; para validar la firma, arranca uvicorn con `--proxy-headers --forwarded-allow-ips="*"`.
4. **Variables de entorno en el servidor.** El `Dockerfile` no copia `.env`: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER` (por defecto queda el del Sandbox, `+14155238886`), `LLM_PROVIDER=local` y `CORS_ORIGINS` se ponen en el panel del servidor.
5. **Sandbox o línea aprobada.** Si es el Sandbox, cada celular primero debe enviar `join <código>`. Si es la línea `+1 227 240 5417` aprobada por Meta, no hace falta. Hay que confirmar cuál es, porque el QR de la presentación asume que basta con escribir «Hola».
6. **Render gratis se duerme.** Tarda unos 50 s en despertar y Twilio espera unos 15 s: el primer mensaje se pierde. Antes de presentar, abran `https://<backend>/health`.
7. **Ver los errores reales.** En Twilio: *Monitor → Logs → Errors* (11200 = no pudo llegar a la URL; 12300 = respuesta no válida). En el backend: busca las líneas `[TWILIO IN]`, `[TWILIO STATUS]` y `[TWILIO PRIVACY BLOCK]`.

## 4. Hallazgos de la revisión del PR #4 (presentación)

La otra sesión ya subió correcciones al PR #4 (commit `27b2c2c`), pero **todavía no se revisan**. Quedaron pendientes del equipo:

- **Dos copias de los documentos que no coinciden.** `docs/` lo usan la voz y el cerebro; `Sarha_Empleado_Digital_Prebel/docs/` lo usan el chat y WhatsApp. En la copia del bot se cambió a Lucía Mejía por Johanna Puentes o Cristina Giraldo. Para cesantías, eso coincide con la respuesta 3.9 de Prebel. Pero en `Auxilios_y_beneficios_Prebel_20260310.md` línea 50, el correo de incapacidades de **practicantes (PP)** se cambió a `johanna.puentes`, y Prebel solo dijo que Johanna atiende **impulso y mercadeo (PI)**. Hay que acordar una sola versión aprobada y sincronizar las dos copias, porque si no, la voz y WhatsApp pueden dar correos distintos.
- **La presentación vieja de Claude Slides** (menú 1–4, 101 secciones, 15 pruebas) queda descartada: la oficial es `#presentacion` en la web.
- **Faltan los nombres de 2 integrantes** en `landing-v3/src/presentation/content.ts`.

## 5. Cómo levantar todo para la demo

```bash
# Backend (chat web + WhatsApp)
cd Sarha_Empleado_Digital_Prebel
python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --proxy-headers --forwarded-allow-ips="*"

# Túnel público para Twilio, mientras se prueba (otra terminal)
ngrok http 8000        # copia la URL https y ponla en Twilio: https://<url>/twilio/webhook (POST)

# Landing (otra terminal)
cd landing-v3 && npm install && npm run dev            # http://localhost:5173
```

---

## Prompt para el agente de Antigravity (Gemini)

```text
Eres el responsable de dejar operativo el chatbot de WhatsApp de SARHA (repo laverdestudios-web/prebel-Empleadodigital, Reto 7 EstudIA · Prebel S.A.S. BIC). Trabaja sobre la rama sarha-landing-v3. No toques main. No cambies el proveedor de IA (el proyecto usa búsqueda local / Gemini; no se usa la API de Claude). Habla en español y explícame cada paso antes de ejecutarlo.

Primero lee REPORTE-REVISION-WHATSAPP.md en la raíz del repo. Ahí está lo que cambió hoy y la prueba de que el webhook /twilio/webhook responde bien con el código integrado.

TAREA 1 · Sincronizar y verificar (no subas nada todavía)
1) git fetch origin && git switch sarha-landing-v3 && git pull
2) Si yo tengo cambios locales en Sarha_Empleado_Digital_Prebel/ que hicieron funcionar WhatsApp y NO están en GitHub, muéstramelos (git status, git diff) y explícame cada uno antes de hacer nada.
3) Corre y pégame los resultados:
   - cd Sarha_Empleado_Digital_Prebel && python -m pytest -q tests        → deben pasar 18
   - cd .. && python -m pytest -q server/tests brain/tests                 → deben pasar 33
   - Simula Twilio (sin red) con fastapi.testclient: POST /twilio/webhook con form data From, To, Body, NumMedia=0, con los mensajes "Hola", "1", "2", "1" (misma sesión), "¿Cuál es el salario mínimo actual?", y una foto (NumMedia=1). Todos deben devolver 200 y TwiML con <Message>.

TAREA 2 · Diagnosticar por qué no responde en WhatsApp real (sección 3 del reporte). Revisa en este orden y dime qué encontraste en cada punto:
   a) ¿Dónde corre el backend y cuál es su URL pública HTTPS? (Twilio no llega a localhost).
   b) En la consola de Twilio, la URL del webhook de la línea/Sandbox: ¿es exactamente https://<backend>/twilio/webhook con POST? ¿Es una URL de ngrok vieja?
   c) TWILIO_VALIDATE_SIGNATURE: si está en true detrás de Render o ngrok, da 403. Para la demo, déjalo en false, o arranca uvicorn con --proxy-headers --forwarded-allow-ips="*".
   d) Variables en el servidor: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER (si no se define, queda el del Sandbox, +14155238886), LLM_PROVIDER=local, CORS_ORIGINS. El Dockerfile no copia .env.
   e) ¿Es el Sandbox (hay que enviar "join <código>") o la línea aprobada +1 227 240 5417?
   f) Twilio → Monitor → Logs → Errors: dime los códigos (11200, 12300, etc.) y qué significan.
   g) En el log del backend, ¿aparecen [TWILIO IN] al escribirle? Si no aparecen, el mensaje no está llegando: es el punto a o b.

TAREA 3 · Arreglar sin romper
- Corrige solo lo necesario para que responda. No cambies la lógica del menú ni las respuestas.
- Nunca subas .env ni credenciales. Antes de cada commit:
  git diff | grep -nE "AIza|sk-ant-|gsk_|AC[a-f0-9]{32}|AUTH_TOKEN=.+"   → debe salir vacío.
- NO edites docs/ ni Sarha_Empleado_Digital_Prebel/docs/. Si encuentras diferencias entre esas dos copias, solo repórtalas (están en la sección 4 del reporte).
- Vuelve a correr las pruebas de la TAREA 1 (18 y 33 deben seguir pasando).
- Crea una rama integra-whatsapp-<tu-nombre> desde sarha-landing-v3, haz commit y push, y abre un Pull Request hacia sarha-landing-v3 (no hacia main) con: causa encontrada, qué cambiaste, resultados de las pruebas y captura de una conversación real en WhatsApp con "Hola" → 1 → 2 → 1.

TAREA 4 · Checklist final para la demo (confírmamelo punto por punto)
- Desde un celular que nunca le haya escrito: "Hola" → menú de 5 opciones.
- 1 → 2 → 1 → requisitos de retiro de cesantías por compra de vivienda.
- "¿Cuál es el salario mínimo actual?" → mensaje oficial de no disponible.
- Una foto → aviso de privacidad.
- /health del backend responde (si está en Render, despiértalo 10 minutos antes).
```
