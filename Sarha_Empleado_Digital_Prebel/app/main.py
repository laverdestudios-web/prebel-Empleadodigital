"""FastAPI application for Prebel Gestión Humana Chatbot (SARHA + Twilio + Meta WhatsApp)."""

from __future__ import annotations

from urllib.parse import parse_qs

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from twilio.request_validator import RequestValidator

from app.chatbot import HRChatbot, PRIVACY_BLOCK_MESSAGE
from app.config import BASE_DIR, settings
from app.knowledge import KnowledgeBase
from app.metrics import anonymize_session, metrics
from app.self_service import build_self_service_guide, list_procedures, load_contacts_config
from app.twilio_whatsapp import build_twiml_response, build_wa_me_url, split_whatsapp_message
from app.whatsapp import extract_incoming_messages, send_whatsapp_text

kb = KnowledgeBase(settings.docs_dir)
chatbot = HRChatbot(kb, settings)

app = FastAPI(
    title=settings.app_name,
    description="Chatbot de Gestión Humana Prebel S.A.S. BIC (SARHA Web + Twilio WhatsApp + Meta Cloud API)",
    version="1.1.0",
)

if settings.static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    channel: str = Field(default="web", pattern="^(web|whatsapp)$")
    session_id: str = Field(default="web", min_length=1, max_length=120)


class SelfServiceRequest(BaseModel):
    procedure_id: str
    variant_id: str
    employee_name: str = ""
    document_id: str = ""
    email: str = ""
    phone: str = ""
    target_entity: str = ""


@app.get("/", response_class=HTMLResponse)
async def serve_home() -> HTMLResponse:
    """Serve the SARHA v2 landing page linked to Twilio WhatsApp and live chatbot."""
    v2_path = BASE_DIR / "landing_sarha_prebel_v2 segunda fase.html"
    if v2_path.exists():
        return HTMLResponse(content=v2_path.read_text(encoding="utf-8"))
    sarha_path = settings.static_dir / "sarha.html"
    if sarha_path.exists():
        return HTMLResponse(content=sarha_path.read_text(encoding="utf-8"))
    index_path = settings.static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="UI not found")
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.get("/presentacion", response_class=HTMLResponse)
async def serve_presentation() -> HTMLResponse:
    """Serve the 3-minute executive pitch presentation."""
    pres_path = BASE_DIR / "presentacion_sarha_prebel.html"
    if not pres_path.exists():
        raise HTTPException(status_code=404, detail="Presentation not found")
    return HTMLResponse(content=pres_path.read_text(encoding="utf-8"))


@app.get("/chat", response_class=HTMLResponse)
async def serve_console_chat() -> HTMLResponse:
    """Serve the full-screen chat & self-service console."""
    index_path = settings.static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Console UI not found")
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.get("/health")
async def health() -> dict[str, object]:
    """Health check endpoint for on-premise monitoring."""
    return {
        "status": "ok",
        "chunks_indexed": len(kb.chunks),
        "mode": chatbot._active_mode(),
        "twilio_configured": bool(settings.twilio_account_sid and settings.twilio_auth_token),
        "twilio_whatsapp_number": settings.twilio_whatsapp_number,
        "whatsapp_configured": bool(settings.whatsapp_access_token and settings.whatsapp_phone_number_id),
    }


@app.get("/api/twilio/info")
async def twilio_info() -> dict[str, object]:
    """Return Twilio WhatsApp connection link & sandbox instructions for the SARHA UI."""
    return {
        "configured": bool(settings.twilio_account_sid and settings.twilio_auth_token),
        "whatsapp_number": settings.twilio_whatsapp_number,
        "sandbox_join_code": settings.twilio_sandbox_join_code,
        "wa_link": build_wa_me_url(settings, initial_text="Hola"),
        "webhook_path": "/twilio/webhook",
    }


@app.get("/api/categories")
async def get_categories() -> dict[str, object]:
    """Return indexed HR categories and topics."""
    return {"categories": kb.list_categories()}


@app.get("/api/config/contacts")
async def get_contacts_matrix() -> dict[str, object]:
    """Return the configurable external escalation & contacts matrix (config/contacts.json)."""
    return load_contacts_config()


@app.get("/api/metrics/report")
async def get_anonymized_metrics() -> dict[str, object]:
    """Return 100% anonymized aggregated pilot metrics (no PII, no phone numbers, no chat logs)."""
    return metrics.snapshot()


@app.post("/api/chat")
async def chat_endpoint(payload: ChatRequest) -> dict[str, object]:
    """Answer an employee question or menu selection strictly from docs/*.md."""
    result = chatbot.answer(payload.message, channel=payload.channel, session_id=payload.session_id)
    return {
        "answer": result.answer,
        "sources": result.sources,
        "mode": result.mode,
        "is_out_of_scope": result.is_out_of_scope,
        "suggested_questions": result.suggested_questions,
        "menu_options": result.menu_options,
    }


@app.get("/api/self-service/procedures")
async def self_service_procedures() -> dict[str, object]:
    """List available guided self-service procedures."""
    return {"procedures": list_procedures()}


@app.post("/api/self-service/guide")
async def self_service_guide(payload: SelfServiceRequest) -> dict[str, object]:
    """Generate a tailored checklist and template for a self-service procedure."""
    return build_self_service_guide(
        procedure_id=payload.procedure_id,
        variant_id=payload.variant_id,
        employee_name=payload.employee_name,
        document_id=payload.document_id,
        email=payload.email,
        phone=payload.phone,
        target_entity=payload.target_entity,
    )


@app.post("/twilio/webhook")
async def receive_twilio_whatsapp(request: Request) -> Response:
    """Twilio WhatsApp Sandbox / Cloud webhook returning TwiML XML."""
    raw_body = (await request.body()).decode("utf-8")
    parsed = {k: v[0] for k, v in parse_qs(raw_body, keep_blank_values=True).items()}

    if settings.twilio_validate_signature and settings.twilio_auth_token:
        signature = request.headers.get("X-Twilio-Signature", "")
        validator = RequestValidator(settings.twilio_auth_token)
        if not validator.validate(str(request.url), parsed, signature):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    sender = parsed.get("From", "twilio-anon")
    anon_id = anonymize_session(sender)
    body = parsed.get("Body", "").strip()
    msg_status = parsed.get("MessageStatus", "")
    num_media = int(parsed.get("NumMedia", "0") or 0)

    # Ignore Twilio delivery status callbacks if routed to the same URL
    if msg_status and not body and num_media == 0:
        print(f"[TWILIO STATUS] session={anon_id} status={msg_status}", flush=True)
        return Response(content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>', media_type="application/xml")

    # Privacy Policy (Ley 1581 / Prebel Section 2.4 & 5.1): never download or process images/documents
    if num_media > 0:
        metrics.record_query(channel="whatsapp", category=None, is_out_of_scope=True, is_privacy_block=True)
        xml_payload = build_twiml_response([PRIVACY_BLOCK_MESSAGE])
        print(f"[TWILIO PRIVACY BLOCK] session={anon_id} media_blocked={num_media}", flush=True)
        return Response(content=xml_payload, media_type="application/xml")

    result = chatbot.answer(body or "hola", channel="whatsapp", session_id=f"tw:{anon_id}")
    parts = split_whatsapp_message(result.answer)
    xml_payload = build_twiml_response(parts)
    print(
        f"[TWILIO IN] session={anon_id} parts={len(parts)} chars={len(result.answer)} oos={result.is_out_of_scope}",
        flush=True,
    )
    return Response(content=xml_payload, media_type="application/xml")


@app.get("/webhook")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
) -> PlainTextResponse:
    """Meta WhatsApp Cloud API webhook verification handshake."""
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Invalid verify token")


@app.post("/webhook")
async def receive_whatsapp_webhook(request: Request) -> dict[str, object]:
    """Receive incoming WhatsApp messages, generate grounded replies, and send via Meta API."""
    payload = await request.json()
    incoming = extract_incoming_messages(payload)
    replies = []
    for item in incoming:
        result = chatbot.answer(
            item["body"],
            channel="whatsapp",
            session_id=f"wa:{item['from']}",
        )
        sent = await send_whatsapp_text(item["from"], result.answer, settings)
        replies.append({"to": item["from"], "sent_via_meta": sent, "answer": result.answer})
    return {"status": "received", "processed": len(replies), "replies": replies}
