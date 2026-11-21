"""
API del Empleado Digital Prebel: webhook de WhatsApp Cloud API.

    GET  /health   -> estado del servicio
    GET  /webhook  -> verificación de Meta (hub.challenge)
    POST /webhook  -> mensajes entrantes; responde 200 de inmediato y procesa
                      la consulta al LLM y el envío en segundo plano.

Ejecutar (desde la raíz del repositorio):
    uvicorn server.app:app --host 0.0.0.0 --port 8000
"""

import hashlib
import hmac
import logging
import threading
from collections import OrderedDict

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

from brain.chatbot_groq import MotorChat
from server.config import Config
from server.whatsapp_service import WhatsAppService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("prebel.server")

MENSAJE_ERROR = (
    "En este momento no puedo responder tu consulta. Por favor intenta de nuevo "
    "en unos minutos o comunícate con Gestión Humana."
)
MENSAJE_NO_TEXTO = (
    "Por ahora solo puedo leer mensajes de texto. Escríbeme tu pregunta sobre "
    "vinculación y nómina, créditos, auxilios o beneficios."
)
MAX_CARACTERES_PREGUNTA = 1000


class Deduplicador:
    """
    Recuerda los últimos message.id procesados. Meta reintenta la entrega si
    no recibe 200 a tiempo, y a veces entrega el mismo evento dos veces.

    Limitación: vive en memoria del proceso. Con varios workers o tras un
    reinicio no protege; para producción usar Redis o SQLite.
    """

    def __init__(self, capacidad: int = 5000):
        self.capacidad = capacidad
        self._vistos: OrderedDict[str, None] = OrderedDict()
        self._lock = threading.Lock()

    def es_nuevo(self, message_id: str) -> bool:
        with self._lock:
            if message_id in self._vistos:
                return False
            self._vistos[message_id] = None
            if len(self._vistos) > self.capacidad:
                self._vistos.popitem(last=False)
            return True


def firma_valida(cuerpo: bytes, firma: str | None, secreto: str) -> bool:
    if not (firma and secreto and firma.startswith("sha256=")):
        return False
    esperada = hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, firma.removeprefix("sha256="))


def extraer_mensajes(payload: dict) -> list[dict]:
    """Aplana entry[].changes[].value.messages[]; ignora statuses y otros eventos."""
    mensajes = []
    if payload.get("object") != "whatsapp_business_account":
        return mensajes
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            if change.get("field") != "messages":
                continue
            for m in (change.get("value") or {}).get("messages") or []:
                if m.get("id") and m.get("from"):
                    mensajes.append(m)
    return mensajes


def crear_app(motor=None, whatsapp=None, config: Config | None = None) -> FastAPI:
    config = config or Config.desde_entorno()
    whatsapp = whatsapp or WhatsAppService(config)
    dedup = Deduplicador()
    estado = {"motor": motor}

    def obtener_motor():
        # Carga perezosa: el servidor arranca aunque falte la API key del LLM,
        # y /health lo reporta en lugar de caerse.
        if estado["motor"] is None:
            estado["motor"] = MotorChat()
        return estado["motor"]

    if not config.verify_token:
        log.warning("WHATSAPP_VERIFY_TOKEN vacío: la verificación GET /webhook fallará.")
    if not config.app_secret and not config.permitir_sin_firma:
        log.warning("WHATSAPP_APP_SECRET vacío: se rechazarán todos los POST /webhook.")

    app = FastAPI(title="Prebel Empleado Digital", version="0.1.0")

    @app.get("/health")
    def health():
        try:
            m = obtener_motor()
            return {"status": "ok", "modelo": m.modelo, "fragmentos": len(m.fragmentos)}
        except Exception as e:  # noqa: BLE001 - se reporta, no se oculta
            return {"status": "degradado", "error": str(e)}

    @app.get("/webhook", response_class=PlainTextResponse)
    def verificar(request: Request):
        q = request.query_params
        if (q.get("hub.mode") == "subscribe" and config.verify_token
                and hmac.compare_digest(q.get("hub.verify_token", ""), config.verify_token)):
            return q.get("hub.challenge", "")
        raise HTTPException(status_code=403, detail="Token de verificación inválido")

    def procesar(mensaje: dict):
        wa_id = mensaje["from"]
        try:
            if mensaje.get("type") != "text":
                respuesta = MENSAJE_NO_TEXTO
            else:
                texto = (mensaje.get("text") or {}).get("body", "").strip()
                if not texto:
                    return
                respuesta = obtener_motor().responder(texto[:MAX_CARACTERES_PREGUNTA], wa_id)
        except Exception:  # noqa: BLE001
            log.exception("Fallo procesando mensaje %s", mensaje.get("id"))
            respuesta = MENSAJE_ERROR
        if not whatsapp.enviar_texto(wa_id, respuesta):
            log.error("No se pudo entregar la respuesta del mensaje %s", mensaje.get("id"))

    @app.post("/webhook")
    async def recibir(request: Request, tareas: BackgroundTasks):
        cuerpo = await request.body()
        if not config.permitir_sin_firma and not firma_valida(
                cuerpo, request.headers.get("X-Hub-Signature-256"), config.app_secret):
            raise HTTPException(status_code=401, detail="Firma inválida")
        try:
            payload = await request.json()
        except ValueError:
            raise HTTPException(status_code=400, detail="JSON inválido")

        encolados = 0
        for m in extraer_mensajes(payload):
            if dedup.es_nuevo(m["id"]):
                tareas.add_task(procesar, m)
                encolados += 1
        return {"status": "recibido", "encolados": encolados}

    return app


app = crear_app()
