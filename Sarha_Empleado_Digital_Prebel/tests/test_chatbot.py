"""Automated tests for Prebel Gestión Humana Chatbot."""

from __future__ import annotations

import asyncio
import json

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.chatbot import OUT_OF_SCOPE_MESSAGE, PRIVACY_BLOCK_MESSAGE
from app.main import (
    ChatRequest,
    SelfServiceRequest,
    chat_endpoint,
    get_anonymized_metrics,
    get_categories,
    get_contacts_matrix,
    health,
    kb,
    receive_twilio_whatsapp,
    receive_whatsapp_webhook,
    self_service_guide,
    self_service_procedures,
    serve_console_chat,
    serve_home,
    twilio_info,
    verify_whatsapp_webhook,
)


def _run(coro):
    """Step an async coroutine without opening event-loop sockets."""
    try:
        while True:
            coro.send(None)
    except StopIteration as stop:
        return stop.value


def _make_request(payload: dict) -> Request:
    body = json.dumps(payload).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    scope = {"type": "http", "method": "POST", "path": "/webhook", "headers": []}
    return Request(scope, receive)


def test_knowledge_base_indexed_properly() -> None:
    assert len(kb.chunks) >= 30
    source_files = {c.source_file for c in kb.chunks}
    assert "Auxilios_y_beneficios_Prebel_20260310.md" in source_files
    assert "Creditos_Prebel_20260310.md" in source_files
    assert "Vinculacion_y_nomina_20260310.md" in source_files
    assert "Glosario_Business_Partner_20260922.md" in source_files
    assert "Instrucciones_Tono_Ejemplos_Restricciones.md" not in source_files
    assert "politica-etica-seguridad-prebel.md" not in source_files


def test_health_and_home() -> None:
    data = _run(health())
    assert data["status"] == "ok"
    assert data["chunks_indexed"] == len(kb.chunks)

    home = _run(serve_home())
    assert home.status_code == 200
    home_html = home.body.decode("utf-8")
    assert "SARHA" in home_html
    assert "Habla con SARHA" in home_html
    assert "/api/twilio/info" in home_html

    console = _run(serve_console_chat())
    assert console.status_code == 200
    assert "Autogestión" in console.body.decode("utf-8")

    cats = _run(get_categories())
    assert len(cats["categories"]) >= 4


def test_greeting_returns_menu() -> None:
    body = _run(chat_endpoint(ChatRequest(message="Hola", channel="web")))
    assert "Vinculación y Nómina" in body["answer"]
    assert "Créditos y Condiciones" in body["answer"]
    assert "Auxilios y Beneficios" in body["answer"]
    assert "únicamente con base en los documentos cargados" in body["answer"]


def test_out_of_scope_question() -> None:
    body = _run(chat_endpoint(ChatRequest(message="¿Cuál es el salario mínimo actual?", channel="web")))
    assert body["is_out_of_scope"] is True
    assert body["answer"] == OUT_OF_SCOPE_MESSAGE


def test_ambiguous_credits_question() -> None:
    body = _run(chat_endpoint(ChatRequest(message="Háblame de los créditos", channel="web")))
    ans = body["answer"].lower()
    assert "educación" in ans
    assert "mascotas" in ans
    assert "salud" in ans
    assert "vivienda" in ans


def test_cesantias_compra_vivienda() -> None:
    body = _run(
        chat_endpoint(
            ChatRequest(
                message="¿Cuáles son los requisitos para retirar cesantías por compra de vivienda?",
                channel="web",
            )
        )
    )
    assert body["is_out_of_scope"] is False
    assert "johanna.puentes@prebel.com.co" in body["answer"]
    assert "3104589490" in body["answer"]
    assert "promesa de compraventa" in body["answer"].lower()
    assert "matrícula inmobiliaria" in body["answer"].lower() or "matricula inmobiliaria" in body["answer"].lower()


def test_auxilio_visual_odontologico() -> None:
    body = _run(
        chat_endpoint(ChatRequest(message="¿Cuál es el valor del auxilio visual u odontológico?", channel="web"))
    )
    assert "$332.000" in body["answer"]


def test_credito_mascotas() -> None:
    body = _run(
        chat_endpoint(
            ChatRequest(message="¿Qué es el crédito de grave calamidad doméstica de mascotas?", channel="web")
        )
    )
    ans = body["answer"].lower()
    assert "perros o gatos" in ans
    assert "sin intereses" in ans


def test_business_partner_glossary() -> None:
    body = _run(
        chat_endpoint(ChatRequest(message="¿Quién es mi Business Partner de Gestión Humana?", channel="web"))
    )
    ans = body["answer"]
    assert "Nathalia León" in ans
    assert "Laura Jaramillo" in ans


def test_self_service_endpoints() -> None:
    procs = _run(self_service_procedures())
    assert len(procs["procedures"]) >= 4

    g = _run(
        self_service_guide(
            SelfServiceRequest(
                procedure_id="certificado_laboral",
                variant_id="operativo",
                employee_name="Carlos Ruiz",
                document_id="1037654321",
            )
        )
    )
    assert "angela.quintero@prebel.com.co" in g["contact"].lower()
    assert "Carlos Ruiz" in g["template"]


def test_whatsapp_webhook_verification_and_message() -> None:
    verify_ok = _run(
        verify_whatsapp_webhook(
            hub_mode="subscribe",
            hub_verify_token="prebel_gh_verify_token",
            hub_challenge="123456",
        )
    )
    assert verify_ok.status_code == 200
    assert verify_ok.body.decode("utf-8") == "123456"

    with pytest.raises(HTTPException) as exc_info:
        _run(
            verify_whatsapp_webhook(
                hub_mode="subscribe",
                hub_verify_token="wrong_token",
                hub_challenge="123456",
            )
        )
    assert exc_info.value.status_code == 403

    incoming_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "573001112233",
                                    "type": "text",
                                    "text": {"body": "¿Cuál es el valor del auxilio visual u odontológico?"},
                                }
                            ]
                        }
                    }
                ]
            }
        ],
    }
    data = _run(receive_whatsapp_webhook(_make_request(incoming_payload)))
    assert data["processed"] == 1
    assert "$332.000" in data["replies"][0]["answer"]


def test_all_menu_leaves_resolve_chunks() -> None:
    from app.menu import MENU_NODES, resolve_menu_chunks

    for node in MENU_NODES.values():
        for item in node.items:
            if item.next_node:
                assert item.next_node in MENU_NODES
            else:
                chunks = resolve_menu_chunks(kb, item)
                assert len(chunks) >= 1, f"Menu item {node.node_id}.{item.number} ({item.label}) resolved 0 chunks"


def test_numbered_menu_navigation_flow() -> None:
    sid = "test-nav-1"
    # 1. Start at root menu
    r0 = _run(chat_endpoint(ChatRequest(message="hola", channel="web", session_id=sid)))
    assert "Vinculación y Nómina" in r0["answer"]

    # 2. Pick 1 -> Vinculación y Nómina
    r1 = _run(chat_endpoint(ChatRequest(message="1", channel="web", session_id=sid)))
    assert "Certificados laborales" in r1["answer"]
    assert "Retiro de cesantías" in r1["answer"]

    # 3. Pick 2 -> Retiro de cesantías
    r2 = _run(chat_endpoint(ChatRequest(message="2", channel="web", session_id=sid)))
    assert "Compra de vivienda" in r2["answer"]

    # 4. Pick 1 -> Compra de vivienda (exact answer)
    r3 = _run(chat_endpoint(ChatRequest(message="1", channel="web", session_id=sid)))
    assert "johanna.puentes@prebel.com.co" in r3["answer"]
    assert "3104589490" in r3["answer"]

    # 5. Pick 0 -> back to Vinculación y Nómina
    r_back = _run(chat_endpoint(ChatRequest(message="0", channel="web", session_id=sid)))
    assert "Certificados laborales" in r_back["answer"]

    # 6. Pick 00 -> back to Main Menu
    r_home = _run(chat_endpoint(ChatRequest(message="00", channel="web", session_id=sid)))
    assert "Menú Principal" in r_home["answer"]

    # 7. Pick 3 -> Auxilios, then 3 -> Auxilio visual u odontológico
    r_aux = _run(chat_endpoint(ChatRequest(message="3", channel="whatsapp", session_id=sid)))
    assert "*3.* Auxilio visual" in r_aux["answer"]
    r_vis = _run(chat_endpoint(ChatRequest(message="3", channel="whatsapp", session_id=sid)))
    assert "$332.000" in r_vis["answer"]

    # 8. Free-text question still works from inside any menu
    r_free = _run(
        chat_endpoint(
            ChatRequest(message="¿Quién es mi Business Partner de Gestión Humana?", channel="web", session_id=sid)
        )
    )
    assert "Nathalia León" in r_free["answer"]


def _make_twilio_request(from_phone: str, body_text: str) -> Request:
    from urllib.parse import urlencode

    raw = urlencode({"From": from_phone, "To": "whatsapp:+14155238886", "Body": body_text}).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": raw, "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/twilio/webhook",
        "headers": [(b"content-type", b"application/x-www-form-urlencoded")],
    }
    return Request(scope, receive)


def test_twilio_info_and_webhook_twiml() -> None:
    info = _run(twilio_info())
    assert info["webhook_path"] == "/twilio/webhook"
    assert "wa.me/" in info["wa_link"]

    phone = "whatsapp:+573001234567"
    r_hello = _run(receive_twilio_whatsapp(_make_twilio_request(phone, "hola")))
    assert r_hello.status_code == 200
    assert r_hello.media_type == "application/xml"
    xml1 = r_hello.body.decode("utf-8")
    assert "<Response>" in xml1
    assert "<Message>" in xml1
    assert "Vinculación y Nómina" in xml1

    # Stateful menu choice 3 -> Auxilios y Beneficios -> 3 -> Auxilio visual
    _run(receive_twilio_whatsapp(_make_twilio_request(phone, "3")))
    r_vis = _run(receive_twilio_whatsapp(_make_twilio_request(phone, "3")))
    xml2 = r_vis.body.decode("utf-8")
    assert "$332.000" in xml2


def test_twilio_message_splitting() -> None:
    from app.twilio_whatsapp import build_twiml_response, split_whatsapp_message

    long_text = "\n\n".join([f"Sección {i}: " + ("texto de prueba " * 30) for i in range(6)])
    parts = split_whatsapp_message(long_text, max_len=1500)
    assert len(parts) >= 2
    assert all(len(p) <= 1500 for p in parts)
    twiml = build_twiml_response(parts)
    assert twiml.count("<Message>") == len(parts)


def test_pdf_official_clarifications_and_updated_contacts() -> None:
    r_codes = _run(
        chat_endpoint(ChatRequest(message="¿Qué significan los códigos PA, PO, PI y PP?", channel="whatsapp"))
    )
    assert "Personal Administrativo" in r_codes["answer"]
    assert "Personal Practicante" in r_codes["answer"]

    r_pet = _run(
        chat_endpoint(
            ChatRequest(message="¿Dónde se registra una mascota en la base de datos de la compañía?", channel="whatsapp")
        )
    )
    assert "Stefanny Pulgarín" in r_pet["answer"]
    assert "3104057760" in r_pet["answer"]

    r_dir = _run(
        chat_endpoint(ChatRequest(message="Directorio de contactos de Gestión Humana", channel="whatsapp"))
    )
    assert "johanna.puentes@prebel.com.co" in r_dir["answer"]
    assert "cristina.giraldo@prebel.com.co" in r_dir["answer"]


def test_ethics_privacy_guard_and_media_blocking() -> None:
    # 1. Private personal data requests are blocked with Ley 1581 privacy notice
    r_pay = _run(chat_endpoint(ChatRequest(message="Necesito mi desprendible de nómina", channel="whatsapp")))
    assert r_pay["is_out_of_scope"] is True
    assert "Ley 1581 de 2012" in r_pay["answer"]

    # 2. Explicitly excluded policy topic (acoso laboral) returns out-of-scope
    r_exc = _run(chat_endpoint(ChatRequest(message="¿Cuál es el canal de acoso laboral?", channel="whatsapp")))
    assert r_exc["is_out_of_scope"] is True
    assert r_exc["answer"] == OUT_OF_SCOPE_MESSAGE

    # 3. Incoming Twilio photo/document (NumMedia=1) is blocked without downloading/storing
    from urllib.parse import urlencode

    raw = urlencode(
        {"From": "whatsapp:+573001234567", "To": "whatsapp:+12272405417", "Body": "", "NumMedia": "1"}
    ).encode("utf-8")

    async def receive():
        return {"type": "http.request", "body": raw, "more_body": False}

    req = Request(
        {"type": "http", "method": "POST", "path": "/twilio/webhook", "headers": []},
        receive,
    )
    media_resp = _run(receive_twilio_whatsapp(req))
    assert media_resp.status_code == 200
    assert "no recibe documentos personales" in media_resp.body.decode("utf-8")


def test_configurable_contacts_and_anonymized_metrics() -> None:
    cfg = _run(get_contacts_matrix())
    assert cfg["contacts"]["cesantias_e_incapacidades_impulso"]["email"] == "johanna.puentes@prebel.com.co"
    assert "urgencies" in cfg

    report = _run(get_anonymized_metrics())
    assert "anonimizados" in report["privacy_guarantee"].lower()
    assert report["total_queries"] >= 1
    assert report["privacy_blocked_events"] >= 1

