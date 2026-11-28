"""Twilio WhatsApp Sandbox/Cloud integration helpers (TwiML + REST + wa.me link)."""

from __future__ import annotations

import re
from urllib.parse import quote

from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from app.config import Settings

MAX_TWILIO_WHATSAPP_CHARS = 1500


def clean_phone_digits(phone: str) -> str:
    """Normalize a WhatsApp number (e.g. 'whatsapp:+14155238886' -> '14155238886')."""
    stripped = phone.replace("whatsapp:", "").strip()
    return re.sub(r"\D", "", stripped)


def build_wa_me_url(settings: Settings, initial_text: str = "Hola") -> str:
    """Build a direct https://wa.me/<number>?text=... link for Twilio WhatsApp."""
    digits = clean_phone_digits(settings.twilio_whatsapp_number)
    if not digits:
        return ""
    msg = settings.twilio_sandbox_join_code.strip() or initial_text
    return f"https://wa.me/{digits}?text={quote(msg)}"


def split_whatsapp_message(text: str, max_len: int = MAX_TWILIO_WHATSAPP_CHARS) -> list[str]:
    """Split long answers on paragraph/line boundaries so Twilio never rejects >1600 chars."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_len:
        return [text]

    parts: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_len:
            current = candidate
            continue

        if current:
            parts.append(current)
            current = ""

        # If a single paragraph exceeds max_len, split by line
        if len(paragraph) <= max_len:
            current = paragraph
        else:
            for line in paragraph.splitlines():
                line_cand = f"{current}\n{line}".strip() if current else line
                if len(line_cand) <= max_len:
                    current = line_cand
                else:
                    if current:
                        parts.append(current)
                    current = line[:max_len]
    if current:
        parts.append(current)
    return parts


def build_twiml_response(messages: list[str]) -> str:
    """Build TwiML XML containing one or more WhatsApp reply messages."""
    twiml = MessagingResponse()
    for msg in messages:
        if msg.strip():
            twiml.message(msg)
    return str(twiml)


def send_twilio_whatsapp(to_phone: str, body: str, settings: Settings) -> list[str]:
    """Send outbound WhatsApp message(s) via Twilio REST API when credentials are present."""
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        return []

    from_num = settings.twilio_whatsapp_number
    if not from_num.startswith("whatsapp:"):
        digits = clean_phone_digits(from_num)
        from_num = f"whatsapp:+{digits}"

    to_num = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:+{clean_phone_digits(to_phone)}"
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    sids: list[str] = []
    for chunk in split_whatsapp_message(body):
        msg = client.messages.create(from_=from_num, to=to_num, body=chunk)
        sids.append(msg.sid)
    return sids
