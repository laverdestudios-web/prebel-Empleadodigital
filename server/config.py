"""Configuración del servidor leída de variables de entorno (ver .env.example)."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    verify_token: str
    app_secret: str
    access_token: str
    phone_number_id: str
    graph_version: str
    permitir_sin_firma: bool
    chat_pruebas: bool = False

    @classmethod
    def desde_entorno(cls) -> "Config":
        return cls(
            verify_token=os.environ.get("WHATSAPP_VERIFY_TOKEN", ""),
            app_secret=os.environ.get("WHATSAPP_APP_SECRET", ""),
            access_token=os.environ.get("WHATSAPP_ACCESS_TOKEN", ""),
            phone_number_id=os.environ.get("WHATSAPP_PHONE_NUMBER_ID", ""),
            graph_version=os.environ.get("WHATSAPP_GRAPH_VERSION", "v21.0"),
            # Solo para pruebas locales con curl. Nunca en un entorno expuesto.
            permitir_sin_firma=os.environ.get("WEBHOOK_PERMITIR_SIN_FIRMA", "") == "1",
            # Página /prueba para chatear con el motor sin WhatsApp. Sin
            # autenticación y consume cuota del LLM: solo en local o demo.
            chat_pruebas=os.environ.get("CHAT_PRUEBAS", "") == "1",
        )
