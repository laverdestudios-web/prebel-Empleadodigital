# Módulo Server (WhatsApp & Backend API) — Computador 2

API FastAPI que conecta WhatsApp Cloud API con el motor de `brain/chatbot_groq.py`.

| Endpoint | Uso |
|---|---|
| `GET /health` | Estado del servicio y del motor (modelo, fragmentos cargados) |
| `GET /webhook` | Verificación de Meta (`hub.mode`, `hub.verify_token`, `hub.challenge`) |
| `GET /prueba` | Chat de pruebas (solo con `CHAT_PRUEBAS=1`) |
| `POST /webhook` | Mensajes entrantes. Valida `X-Hub-Signature-256`, responde 200 de inmediato y procesa en segundo plano |

Comportamiento del `POST /webhook`:
- Rechaza con 401 si la firma HMAC-SHA256 (App Secret) no es válida.
- Deduplica por `message.id` (Meta reintenta entregas).
- Ignora `statuses` (sent/delivered/read): no consumen LLM.
- Mensajes no texto (audio, imagen): respuesta fija pidiendo texto.
- Historial independiente por `wa_id`, con expiración a los 30 min.
- Si el LLM falla, el colaborador recibe un mensaje de error, no silencio.

## Probar el chatbot sin WhatsApp (`/prueba`)

Página de chat que usa el mismo motor que el webhook. Se habilita con
`CHAT_PRUEBAS=1` y está apagada por defecto (no tiene autenticación y consume
cuota del LLM).

**Windows, un clic:** copiar `server\.env.example` a `server\.env`, escribir
`GEMINI_API_KEY` y ejecutar `server\probar_chatbot.bat`. Se abre
`http://localhost:8000/prueba`.

Cada pestaña es una conversación independiente; "Nueva conversación" borra el
historial. Las respuestas muestran el tiempo y el modelo usado.

## Ejecutar en local (desde la raíz del repositorio)

```bash
python -m venv .venv && .venv\Scripts\activate        # Windows
pip install -r server/requirements-dev.txt
copy server\.env.example server\.env                   # y completar valores
uvicorn server.app:app --port 8000 --env-file server/.env
python -m pytest server/tests -q
```

Para que Meta alcance el webhook en desarrollo: `cloudflared tunnel --url http://localhost:8000`
o `ngrok http 8000`, y registrar `https://<url>/webhook` con el `WHATSAPP_VERIFY_TOKEN`.

## Despliegue on-premise (Docker)

```bash
cd server
cp .env.example .env    # completar
docker compose up -d --build
```

El contenedor publica solo en `127.0.0.1:8000`; la entrada pública debe ser un
reverse proxy con TLS o un túnel.

## Limitaciones conocidas

- Deduplicación e historial en memoria: un solo worker; se pierden al reiniciar.
  Para producción, Redis o SQLite.
- Si el proceso muere después del 200 y antes de responder, el mensaje se pierde
  (Meta no reintenta). Para producción, cola persistente.
- Ventana de 24 h de WhatsApp: el bot solo responde a mensajes entrantes; no envía
  plantillas.
