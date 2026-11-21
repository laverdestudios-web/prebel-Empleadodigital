"""
Configuración del Chatbot Prebel - Empleado Digital
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
BRAIN_DIR = PROJECT_ROOT / "brain"
DATA_DIR = PROJECT_ROOT / "data"
KNOWLEDGE_STORE_PATH = DATA_DIR / "prebel_knowledge.json"
SYSTEM_PROMPT_PATH = BRAIN_DIR / "system_prompt.md"

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Configuración del modelo oficial Gemini
MODEL_NAME = "gemini-3.5-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-001"

# Configuración de búsqueda semántica
TOP_K_RESULTS = 4
