"""Pruebas del webhook con payloads reales de WhatsApp Cloud API (LLM y Graph simulados)."""

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from server.app import MENSAJE_ERROR, MENSAJE_NO_TEXTO, crear_app
from server.config import Config
from server.whatsapp_service import partir_texto

SECRETO = "secreto-de-prueba"
VERIFY = "token-verificacion"
WA_ID = "573001234567"


class MotorFalso:
    modelo, fragmentos = "falso", [1, 2, 3]

    def olvidar(self, conversacion_id):
        pass

    def __init__(self, falla=False):
        self.llamadas, self.falla = [], falla

    def responder(self, texto, conversacion_id):
        self.llamadas.append((texto, conversacion_id))
        if self.falla:
            raise RuntimeError("503 UNAVAILABLE")
        return f"respuesta a: {texto}"


class WhatsAppFalso:
    def __init__(self):
        self.enviados = []

    def enviar_texto(self, destino, texto):
        self.enviados.append((destino, texto))
        return True


def config(**kw):
    base = dict(verify_token=VERIFY, app_secret=SECRETO, access_token="x",
                phone_number_id="123", graph_version="v21.0", permitir_sin_firma=False)
    base.update(kw)
    return Config(**base)


def payload_texto(texto="¿Cuánto es el auxilio de lentes?", mid="wamid.A1", tipo="text"):
    msg = {"from": WA_ID, "id": mid, "timestamp": "1732200000", "type": tipo}
    if tipo == "text":
        msg["text"] = {"body": texto}
    else:
        msg[tipo] = {"id": "media-1", "mime_type": "audio/ogg"}
    return {
        "object": "whatsapp_business_account",
        "entry": [{"id": "WABA_ID", "changes": [{"field": "messages", "value": {
            "messaging_product": "whatsapp",
            "metadata": {"display_phone_number": "573000000000", "phone_number_id": "123"},
            "contacts": [{"profile": {"name": "Colaborador"}, "wa_id": WA_ID}],
            "messages": [msg],
        }}]}],
    }


def payload_status():
    return {"object": "whatsapp_business_account", "entry": [{"id": "WABA_ID", "changes": [{
        "field": "messages", "value": {"messaging_product": "whatsapp",
        "metadata": {"phone_number_id": "123"},
        "statuses": [{"id": "wamid.X", "status": "delivered", "recipient_id": WA_ID}]}}]}]}


def firmar(cuerpo: bytes, secreto=SECRETO) -> str:
    return "sha256=" + hmac.new(secreto.encode(), cuerpo, hashlib.sha256).hexdigest()


@pytest.fixture
def entorno():
    motor, wa = MotorFalso(), WhatsAppFalso()
    cliente = TestClient(crear_app(motor=motor, whatsapp=wa, config=config()))
    return cliente, motor, wa


def post(cliente, payload, firma=True, secreto=SECRETO):
    cuerpo = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if firma:
        headers["X-Hub-Signature-256"] = firmar(cuerpo, secreto)
    return cliente.post("/webhook", content=cuerpo, headers=headers)


# --- GET /webhook -------------------------------------------------------------
def test_verificacion_ok(entorno):
    cliente, *_ = entorno
    r = cliente.get("/webhook", params={"hub.mode": "subscribe",
                                         "hub.verify_token": VERIFY, "hub.challenge": "1158201444"})
    assert r.status_code == 200 and r.text == "1158201444"


@pytest.mark.parametrize("params", [
    {"hub.mode": "subscribe", "hub.verify_token": "otro", "hub.challenge": "1"},
    {"hub.mode": "unsubscribe", "hub.verify_token": VERIFY, "hub.challenge": "1"},
    {},
])
def test_verificacion_rechazada(entorno, params):
    cliente, *_ = entorno
    assert cliente.get("/webhook", params=params).status_code == 403


def test_verificacion_sin_token_configurado():
    cliente = TestClient(crear_app(MotorFalso(), WhatsAppFalso(), config(verify_token="")))
    r = cliente.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "",
                                         "hub.challenge": "1"})
    assert r.status_code == 403


# --- POST /webhook: flujo normal ----------------------------------------------
def test_mensaje_texto_responde(entorno):
    cliente, motor, wa = entorno
    r = post(cliente, payload_texto())
    assert r.status_code == 200 and r.json()["encolados"] == 1
    assert motor.llamadas == [("¿Cuánto es el auxilio de lentes?", WA_ID)]
    assert wa.enviados == [(WA_ID, "respuesta a: ¿Cuánto es el auxilio de lentes?")]


def test_mensaje_duplicado_se_procesa_una_vez(entorno):
    cliente, motor, wa = entorno
    for _ in range(3):
        assert post(cliente, payload_texto(mid="wamid.DUP")).status_code == 200
    assert len(motor.llamadas) == 1 and len(wa.enviados) == 1


def test_statuses_no_disparan_llm(entorno):
    cliente, motor, wa = entorno
    r = post(cliente, payload_status())
    assert r.status_code == 200 and r.json()["encolados"] == 0
    assert motor.llamadas == [] and wa.enviados == []


def test_mensaje_no_texto(entorno):
    cliente, motor, wa = entorno
    post(cliente, payload_texto(tipo="audio", mid="wamid.AUD"))
    assert motor.llamadas == []
    assert wa.enviados == [(WA_ID, MENSAJE_NO_TEXTO)]


def test_fallo_del_llm_envia_mensaje_de_error():
    motor, wa = MotorFalso(falla=True), WhatsAppFalso()
    cliente = TestClient(crear_app(motor, wa, config()))
    assert post(cliente, payload_texto()).status_code == 200
    assert wa.enviados == [(WA_ID, MENSAJE_ERROR)]


def test_pregunta_larga_se_trunca(entorno):
    cliente, motor, _ = entorno
    post(cliente, payload_texto(texto="a" * 5000, mid="wamid.LARGO"))
    assert len(motor.llamadas[0][0]) == 1000


def test_otro_objeto_se_ignora(entorno):
    cliente, motor, _ = entorno
    r = post(cliente, {"object": "page", "entry": []})
    assert r.status_code == 200 and motor.llamadas == []


# --- POST /webhook: seguridad -------------------------------------------------
def test_sin_firma_401(entorno):
    cliente, motor, _ = entorno
    assert post(cliente, payload_texto(), firma=False).status_code == 401
    assert motor.llamadas == []


def test_firma_con_otro_secreto_401(entorno):
    cliente, motor, _ = entorno
    assert post(cliente, payload_texto(), secreto="atacante").status_code == 401
    assert motor.llamadas == []


def test_secreto_no_configurado_rechaza_todo():
    motor = MotorFalso()
    cliente = TestClient(crear_app(motor, WhatsAppFalso(), config(app_secret="")))
    assert post(cliente, payload_texto(), secreto="").status_code == 401
    assert motor.llamadas == []


def test_modo_pruebas_sin_firma():
    motor = MotorFalso()
    cliente = TestClient(crear_app(motor, WhatsAppFalso(), config(permitir_sin_firma=True)))
    assert post(cliente, payload_texto(), firma=False).status_code == 200
    assert len(motor.llamadas) == 1


def test_json_invalido_400(entorno):
    cliente, *_ = entorno
    cuerpo = b"{no es json"
    r = cliente.post("/webhook", content=cuerpo,
                     headers={"X-Hub-Signature-256": firmar(cuerpo)})
    assert r.status_code == 400


# --- Otros --------------------------------------------------------------------
def test_health(entorno):
    cliente, *_ = entorno
    assert cliente.get("/health").json()["status"] == "ok"


def test_partir_texto_respeta_limite():
    texto = "\n".join(["linea " * 50] * 40)
    partes = partir_texto(texto, 1000)
    assert all(len(p) <= 1000 for p in partes)
    assert " ".join(partes).split() == texto.split()  # no se pierden palabras


# --- Modo pruebas (/prueba) ---------------------------------------------------
def test_prueba_deshabilitada_por_defecto(entorno):
    cliente, *_ = entorno
    assert cliente.get("/prueba").status_code == 404
    assert cliente.post("/prueba/chat", json={"mensaje": "hola", "sesion": "a"}).status_code == 404


def test_prueba_chat():
    motor = MotorFalso()
    cliente = TestClient(crear_app(motor, WhatsAppFalso(), config(chat_pruebas=True)))
    assert "modo pruebas" in cliente.get("/prueba").text
    r = cliente.post("/prueba/chat", json={"mensaje": "auxilio de gafas", "sesion": "abc"})
    assert r.status_code == 200 and r.json()["respuesta"] == "respuesta a: auxilio de gafas"
    assert motor.llamadas == [("auxilio de gafas", "prueba:abc")]  # no choca con un wa_id


@pytest.mark.parametrize("datos", [
    {"mensaje": "", "sesion": "abc"},
    {"mensaje": "x" * 1001, "sesion": "abc"},
    {"mensaje": "hola", "sesion": "../etc"},
])
def test_prueba_chat_valida_entrada(datos):
    cliente = TestClient(crear_app(MotorFalso(), WhatsAppFalso(), config(chat_pruebas=True)))
    assert cliente.post("/prueba/chat", json=datos).status_code == 422


def test_prueba_chat_error_del_llm_502():
    cliente = TestClient(crear_app(MotorFalso(falla=True), WhatsAppFalso(), config(chat_pruebas=True)))
    r = cliente.post("/prueba/chat", json={"mensaje": "hola", "sesion": "abc"})
    assert r.status_code == 502 and "503 UNAVAILABLE" in r.json()["detail"]
