"""Cliente mínimo de WhatsApp Cloud API (Graph API de Meta)."""

import logging

import httpx

from server.config import Config

log = logging.getLogger("prebel.whatsapp")

# Límite de la Cloud API para el cuerpo de un mensaje de texto.
MAX_CARACTERES_TEXTO = 4096


def partir_texto(texto: str, limite: int = MAX_CARACTERES_TEXTO) -> list[str]:
    """Parte respuestas largas en bloques <= limite, cortando en saltos de línea."""
    partes, actual = [], ""
    for linea in texto.splitlines(keepends=True):
        while len(linea) > limite:
            if actual:
                partes.append(actual)
                actual = ""
            partes.append(linea[:limite])
            linea = linea[limite:]
        if len(actual) + len(linea) > limite:
            partes.append(actual)
            actual = ""
        actual += linea
    if actual.strip():
        partes.append(actual)
    return [p.strip() for p in partes if p.strip()]


class WhatsAppService:
    def __init__(self, config: Config, cliente: httpx.Client | None = None):
        self.config = config
        self.cliente = cliente or httpx.Client(timeout=15)

    @property
    def url(self) -> str:
        return (f"https://graph.facebook.com/{self.config.graph_version}/"
                f"{self.config.phone_number_id}/messages")

    def enviar_texto(self, destino: str, texto: str) -> bool:
        """Envía el texto (en varios mensajes si excede el límite). True si todo salió bien."""
        if not (self.config.access_token and self.config.phone_number_id):
            log.error("WHATSAPP_ACCESS_TOKEN o WHATSAPP_PHONE_NUMBER_ID sin configurar.")
            return False
        ok = True
        for parte in partir_texto(texto):
            r = self.cliente.post(
                self.url,
                headers={"Authorization": f"Bearer {self.config.access_token}"},
                json={
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": destino,
                    "type": "text",
                    "text": {"preview_url": False, "body": parte},
                },
            )
            if r.status_code >= 400:
                log.error("Error %s enviando a WhatsApp: %s", r.status_code, r.text[:500])
                ok = False
                break
        return ok
