"""
Agente de Gestión Humana - Prebel S.A.S. BIC (Claude / Anthropic API)

Arquitectura: contexto completo + caché de prompts.
  system = [instrucciones del asistente, documentos oficiales (cacheados)]
  messages = [historial reciente..., pregunta actual]
"""
import logging
import re
from typing import Any, Dict, List, Optional

import anthropic

from config import (
    CACHE_TTL,
    EFFORT,
    MAX_HISTORY_TURNS,
    MAX_TOKENS,
    MODEL_NAME,
    SERVER_FALLBACK_MODELS,
    SYSTEM_PROMPT_PATH,
)
from knowledge import load_knowledge_base

logger = logging.getLogger("prebel.agent")

DISCLAIMER = (
    "Este chatbot de Gestión Humana funciona con inteligencia artificial y puede cometer errores. "
    "Te recomendamos validar la información o resolver cualquier duda con Stefanny Pulgarín, "
    "Analista de Bienestar y RSE, o Michell Román, Asistente Gestión Humana."
)

NOT_AVAILABLE = (
    "Lo siento, esa información no está disponible en este momento, ya que mi conocimiento "
    "se limita únicamente a los documentos cargados."
)

TECHNICAL_ERROR = (
    "Lo siento, en este momento no puedo procesar tu consulta por un problema técnico. "
    "Por favor intenta de nuevo en unos minutos."
)

GREETINGS = {
    "hola", "buenos dias", "buenas tardes", "buenas noches", "buenas",
    "hey", "saludos", "hola buenos dias", "hola buenas tardes", "hola buenas noches",
}

WELCOME_MESSAGE = (
    "¡Hola! Soy tu asistente de Gestión Humana de Prebel. Puedo ayudarte con:\n\n"
    "1. 📋 **Vinculación y Nómina** (certificados laborales, cesantías, EPS, pensiones, vacaciones, incapacidades)\n"
    "2. 💰 **Créditos y Condiciones** (educación, salud, mascotas, vivienda)\n"
    "3. 🎁 **Auxilios y Beneficios** (educativos, visual/odontológico, salud mental, matrimonio, nacimiento y más)\n\n"
    "¿Sobre cuál trámite o beneficio necesitas información?\n\n"
    "_Recuerda: respondo únicamente con base en los documentos oficiales de Gestión Humana._\n\n"
    + DISCLAIMER
)


def _normalize(text: str) -> str:
    text = text.strip().lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")):
        text = text.replace(a, b)
    return re.sub(r"[^\w\s]", "", text).strip()


class PrebelAgent:
    def __init__(self, client: Optional[anthropic.Anthropic] = None, model: str = MODEL_NAME):
        # Sin argumentos, el SDK toma la credencial de ANTHROPIC_API_KEY.
        self.client = client or anthropic.Anthropic()
        self.model = model
        self.system_blocks = self._build_system_blocks()

    def _build_system_blocks(self) -> List[Dict[str, Any]]:
        """
        Prefijo estable del prompt: instrucciones + documentos. El punto de caché va en el
        último bloque, de modo que todo el prefijo se reutiliza entre consultas.
        No incluir aquí nada variable (fechas, IDs, nombre del usuario).
        """
        if SYSTEM_PROMPT_PATH.exists():
            instructions = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        else:
            instructions = "Eres el Asistente de Gestión Humana de Prebel S.A.S. BIC."

        knowledge = load_knowledge_base()
        return [
            {"type": "text", "text": instructions},
            {
                "type": "text",
                "text": knowledge,
                "cache_control": {"type": "ephemeral", "ttl": CACHE_TTL},
            },
        ]

    def _build_messages(self, question: str, history: Optional[List[Dict[str, str]]]) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []
        if history:
            # Cada turno = mensaje de usuario + respuesta del asistente.
            messages.extend(history[-2 * MAX_HISTORY_TURNS:])
        messages.append({"role": "user", "content": question})
        return messages

    def _create(self, messages: List[Dict[str, Any]]):
        kwargs: Dict[str, Any] = dict(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=self.system_blocks,
            messages=messages,
            output_config={"effort": EFFORT},
        )
        if self.model in SERVER_FALLBACK_MODELS:
            # Si el clasificador de seguridad rechaza la solicitud (falso positivo),
            # el servidor la reintenta en un modelo de respaldo dentro de la misma llamada.
            return self.client.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                **kwargs,
            )
        return self.client.messages.create(**kwargs)

    def ask(self, user_question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Responde una pregunta del colaborador.

        history: turnos previos en formato [{"role": "user"|"assistant", "content": str}, ...].
                 El servidor de WhatsApp debe guardarlo por número de teléfono.
        """
        question = user_question.strip()
        if not question:
            return {"answer": WELCOME_MESSAGE, "usage": None}

        # Saludo exacto sin historial: respuesta fija, sin llamar al modelo.
        if not history and _normalize(question) in GREETINGS:
            return {"answer": WELCOME_MESSAGE, "usage": None}

        try:
            response = self._create(self._build_messages(question, history))
        except anthropic.AuthenticationError:
            logger.exception("ANTHROPIC_API_KEY inválida o ausente")
            return {"answer": TECHNICAL_ERROR, "usage": None, "error": "authentication"}
        except anthropic.RateLimitError:
            logger.exception("Límite de tasa alcanzado")
            return {"answer": TECHNICAL_ERROR, "usage": None, "error": "rate_limit"}
        except anthropic.APIStatusError as e:
            logger.exception("Error de la API (%s), request_id=%s", e.status_code, getattr(e, "request_id", None))
            return {"answer": TECHNICAL_ERROR, "usage": None, "error": f"api_{e.status_code}"}
        except anthropic.APIConnectionError:
            logger.exception("Sin conexión con la API de Anthropic")
            return {"answer": TECHNICAL_ERROR, "usage": None, "error": "connection"}

        usage = {
            "input_tokens": response.usage.input_tokens,
            "cache_read_input_tokens": response.usage.cache_read_input_tokens,
            "cache_creation_input_tokens": response.usage.cache_creation_input_tokens,
            "output_tokens": response.usage.output_tokens,
            "model": response.model,
            "stop_reason": response.stop_reason,
        }

        if response.stop_reason == "refusal":
            logger.warning("Solicitud rechazada: %s", getattr(response, "stop_details", None))
            return {"answer": f"{NOT_AVAILABLE}\n\n{DISCLAIMER}", "usage": usage}

        answer = "".join(b.text for b in response.content if b.type == "text").strip()
        if not answer:
            answer = f"{NOT_AVAILABLE}\n\n{DISCLAIMER}"
        elif response.stop_reason == "max_tokens":
            logger.warning("Respuesta truncada por max_tokens=%s", MAX_TOKENS)

        return {"answer": answer, "usage": usage}


# Instancia singleton para reutilizar en API y tests
_agent_instance: Optional[PrebelAgent] = None


def get_agent() -> PrebelAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PrebelAgent()
    return _agent_instance


def responder_pregunta(pregunta: str, historial: Optional[List[Dict[str, str]]] = None) -> str:
    """Función de interfaz lista para conectar con el servidor de WhatsApp."""
    return get_agent().ask(pregunta, history=historial)["answer"]
