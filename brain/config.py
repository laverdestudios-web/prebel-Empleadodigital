"""
Configuración del Chatbot Prebel - Empleado Digital (Claude / Anthropic API)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno (.env en la raíz del proyecto)
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Rutas del proyecto
DOCS_DIR = PROJECT_ROOT / "docs"
BRAIN_DIR = PROJECT_ROOT / "brain"
SYSTEM_PROMPT_PATH = BRAIN_DIR / "system_prompt.md"

# Documentos oficiales que forman la base de conocimiento
KNOWLEDGE_FILES = [
    "Auxilios_y_beneficios_Prebel_20260310.md",
    "Creditos_Prebel_20260310.md",
    "Vinculacion_y_nomina_20260310.md",
    "Glosario_Business_Partner_20260922.md",
]

# Credenciales: el SDK de Anthropic lee ANTHROPIC_API_KEY del entorno automáticamente.

# Modelo de Claude (sobrescribible con la variable de entorno PREBEL_MODEL)
MODEL_NAME = os.getenv("PREBEL_MODEL", "claude-opus-5-5")

# Esfuerzo de razonamiento: low | medium | high | xhigh | max
# "low" es adecuado para preguntas y respuestas sobre documentos.
EFFORT = os.getenv("PREBEL_EFFORT", "low")

# Límite de tokens de salida por respuesta
MAX_TOKENS = int(os.getenv("PREBEL_MAX_TOKENS", "8000"))

# Duración de la caché de la base de conocimiento: "5m" o "1h".
# Con tráfico esporádico (WhatsApp) "1h" evita reescribir la caché en cada consulta.
CACHE_TTL = os.getenv("PREBEL_CACHE_TTL", "1h")

# Modelos que admiten el respaldo automático del servidor ante un rechazo de seguridad
SERVER_FALLBACK_MODELS = {
    "claude-opus-5-5",
    "claude-sonnet-5-5",
    "claude-fable-5-2",
    "claude-fable-5-1",
    "claude-opus-5",
}

# Número de turnos previos de la conversación que se envían como contexto
MAX_HISTORY_TURNS = int(os.getenv("PREBEL_MAX_HISTORY_TURNS", "6"))
