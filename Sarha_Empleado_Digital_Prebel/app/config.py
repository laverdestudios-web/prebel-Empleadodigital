"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Prebel HR chatbot."""

    app_name: str = "Sarha · Chatbot de Gestión Humana Prebel"
    docs_dir: Path = Path(os.getenv("DOCS_DIR", str(BASE_DIR / "docs")))
    static_dir: Path = BASE_DIR / "static"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Optional LLM configuration (if omitted, runs 100% locally via deterministic RAG)
    llm_provider: str = os.getenv("LLM_PROVIDER", "local").strip().lower()
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1").strip()

    # Meta WhatsApp Cloud API configuration
    whatsapp_verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "prebel_gh_verify_token").strip()
    whatsapp_access_token: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    whatsapp_api_version: str = os.getenv("WHATSAPP_API_VERSION", "v21.0").strip()

    # Twilio WhatsApp (Sandbox / Test Line & Production)
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    twilio_whatsapp_number: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886").strip()
    twilio_sandbox_join_code: str = os.getenv("TWILIO_SANDBOX_JOIN_CODE", "").strip()
    twilio_validate_signature: bool = (
        os.getenv("TWILIO_VALIDATE_SIGNATURE", "false").strip().lower() == "true"
    )


settings = Settings()
