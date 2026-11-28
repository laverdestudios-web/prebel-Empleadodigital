# Sarha · Chatbot de Gestión Humana Prebel S.A.S. BIC

Solución de consulta y autogestión para los colaboradores de **Prebel S.A.S. BIC** (personal operativo, administrativo e impulso y mercadeo), basada exclusivamente en los documentos oficiales de la carpeta `docs/`.

## Capacidades principales

1. **Respuestas 100% acotadas a `docs/`**:
   - Indexa automáticamente los archivos Markdown y tablas HTML de `docs/`:
     - `Vinculacion_y_nomina_20260310.md`
     - `Creditos_Prebel_20260310.md`
     - `Auxilios_y_beneficios_Prebel_20260310.md`
     - `Glosario_Business_Partner_20260922.md`
   - Aplica las reglas de tono, trazabilidad (`Fuente: archivo → sección`), manejo de ambigüedad y mensaje exacto de fuera de alcance definidas en `Instrucciones_Tono_Ejemplos_Restricciones.md`.
2. **Funciona 100% On-Premise sin API Key (y soporta LLM opcional)**:
   - Por defecto (`LLM_PROVIDER=local`) opera con motor RAG BM25 determinístico sin enviar datos fuera del servidor.
   - Opcionalmente puede conectarse a **Ollama** (on-premise), **Gemini** o **OpenAI** configurando `.env`.
3. **Autogestión de trámites**:
   - Asistente guiado en la interfaz web para generar el checklist exacto, canal de envío y borrador listo para copiar de:
     - Certificado laboral (Operativo, Impulso y mercado, Administrativo)
     - Reporte de incapacidad
     - Retiro de cesantías (por motivo)
     - Consulta de días de vacaciones
4. **Listo para Meta WhatsApp Cloud API**:
   - Webhook oficial en `GET /webhook` (verificación) y `POST /webhook` (recepción y respuesta automática).
   - Selector en la interfaz web para previsualizar las respuestas en formato **Web** o **WhatsApp**.

---

## Ejecución y pruebas por terminal (sin integrar a WhatsApp)

Antes de conectarlo a WhatsApp o levantar el servidor web, puedes probar el chatbot directamente en tu terminal:

1. **Modo interactivo por terminal** (formato Web por defecto):
   ```bash
   python cli_chat.py
   ```
2. **Modo interactivo simulando respuestas de WhatsApp**:
   ```bash
   python cli_chat.py --channel whatsapp
   ```
3. **Consulta única rápida desde terminal**:
   ```bash
   python cli_chat.py -q "¿Cuáles son los requisitos para retirar cesantías por compra de vivienda?"
   ```

> Si en Windows el comando `python` no responde por el alias de Microsoft Store, usa `py cli_chat.py` o la ruta directa de Python (`C:\Users\maoes\AppData\Local\Python\pythoncore-3.15-64\python.exe cli_chat.py`).

## Ejecución local (Windows / Linux)

1. Crear `.env` a partir de `.env.example` (opcional en modo `local`).
2. Instalar dependencias (si no están instaladas):
   ```bash
   pip install -r requirements.txt
   ```
3. Iniciar el servidor:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. Abrir en el navegador: `http://localhost:8000`

### Ejecutar pruebas automatizadas
```bash
pytest -v
```

---

## Despliegue On-Premise con Docker

```bash
cp .env.example .env
docker compose up -d --build
```
El directorio `./docs` se monta en modo solo lectura (`/app/docs:ro`) para actualizar la base de conocimiento sin reconstruir la imagen.

---

## Integración con Twilio WhatsApp (Línea de prueba para presentación)

El proyecto incluye integración directa con **Twilio WhatsApp Sandbox** en el endpoint `POST /twilio/webhook` (devuelve TwiML XML compatible con WhatsApp y divide automáticamente respuestas largas en mensajes de hasta 1500 caracteres) y vincula la página de inicio **SARHA** (`/`).

### Pasos para probar con Twilio Sandbox

1. Inicia el servidor FastAPI en tu máquina:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
2. Expón el puerto `8000` por HTTPS (por ejemplo con `ngrok http 8000` o un túnel equivalente). Obtendrás una URL pública `https://<tu-subdominio>.ngrok-free.app`.
3. En la consola de **Twilio** (`Messaging → Try it out → Send a WhatsApp message → Sandbox Settings`):
   - **When a message comes in**: `https://<tu-subdominio>.ngrok-free.app/twilio/webhook` (`HTTP POST`)
4. Crea tu archivo `.env` a partir de `.env.example` y configura:
   - `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` (de tu cuenta Twilio)
   - `TWILIO_WHATSAPP_NUMBER=+14155238886` (o el número asignado por Twilio)
   - `TWILIO_SANDBOX_JOIN_CODE=join <tu-codigo>` (el código que muestra Twilio Sandbox)
5. Abre `http://localhost:8000`:
   - Al hacer clic en **«Habla con SARHA»** o **«CONVERSAR CON SARHA EN WHATSAPP»**, se abre directamente WhatsApp hacia la línea de Twilio (`https://wa.me/...`) y también el panel interactivo conectado a `/api/chat`.
   - En `/chat` sigue disponible la consola completa con el asistente de autogestión.

## Requisitos para conectar con Meta WhatsApp Cloud API

1. Contar con una cuenta en **Meta Business Suite** y una app en **Meta for Developers** con el producto **WhatsApp** habilitado.
2. Registrar la línea celular corporativa dedicada de Prebel en la app de Meta.
3. Exponer el endpoint `/webhook` mediante HTTPS (por ejemplo con Nginx/Caddy + certificado TLS en el servidor on-premise).
4. Configurar en Meta Webhooks:
   - **Callback URL**: `https://<tu-dominio>/webhook`
   - **Verify Token**: el valor de `WHATSAPP_VERIFY_TOKEN` en `.env`
   - Suscribir el campo `messages`.
5. Completar en `.env`:
   - `WHATSAPP_ACCESS_TOKEN`
   - `WHATSAPP_PHONE_NUMBER_ID`
