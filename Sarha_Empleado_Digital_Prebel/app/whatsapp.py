"""Meta WhatsApp Cloud API webhook parser and outbound message sender."""

from __future__ import annotations

import httpx

from app.config import Settings


def extract_incoming_messages(payload: dict) -> list[dict[str, str]]:
    """Extract sender phone number and text body from a Meta WhatsApp webhook payload."""
    messages: list[dict[str, str]] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") == "text":
                    sender = msg.get("from", "")
                    body = msg.get("text", {}).get("body", "")
                    if sender and body:
                        messages.append({"from": sender, "body": body})
    return messages


async def send_whatsapp_text(to_phone: str, text: str, settings: Settings) -> bool:
    """Send a text message via Meta WhatsApp Cloud API when credentials are configured."""
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id:
        return False

    url = (
        f"https://graph.facebook.com/{settings.whatsapp_api_version}/"
        f"{settings.whatsapp_phone_number_id}/messages"
    )
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"preview_url": False, "body": text[:4096]},
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        return resp.status_code < 400
