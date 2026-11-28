"""
Agente RAG de Gestión Humana - Prebel S.A.S. BIC
Orquesta la recuperación de fragmentos y genera respuestas fieles siguiendo el System Prompt oficial.
"""
from typing import Dict, Any, List
from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    MODEL_NAME,
    SYSTEM_PROMPT_PATH,
    TOP_K_RESULTS
)
from vectorstore import PrebelVectorStore


class PrebelAgent:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada.")
        self.client = genai.Client(api_key=api_key)
        self.vector_store = PrebelVectorStore(api_key=api_key)
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Carga el System Prompt maestro."""
        if SYSTEM_PROMPT_PATH.exists():
            return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        return "Eres el Asistente de Gestión Humana de Prebel S.A.S. BIC."

    def ask(self, user_question: str) -> Dict[str, Any]:
        """
        Procesa una pregunta del usuario:
        1. Búsqueda semántica en la base de conocimientos.
        2. Construcción del contexto con trazabilidad de fuentes.
        3. Inferencia con Gemini siguiendo las directrices estrictas.
        """
        # Saludos o aperturas breves
        greetings = ["hola", "buenos días", "buenas tardes", "buenas noches", "hey", "saludos"]
        clean_q = user_question.strip().lower()
        if clean_q in greetings or len(clean_q) <= 4:
            return {
                "answer": (
                    "¡Hola! 👋 Soy SARHA, tu asistente virtual de *Gestión Humana Más Cerca de Ti* de Prebel S.A.S. BIC. Puedo orientarte 24/7 sobre:\n\n"
                    "1. 📋 **Vinculación y Nómina** (certificados laborales, cesantías, EPS, pensiones, vacaciones, incapacidades)\n"
                    "2. 💰 **Créditos y Condiciones** (educación, salud, mascotas, vivienda)\n"
                    "3. 🎁 **Auxilios y Beneficios** (educativos, visual/odontológico, salud mental, matrimonio, nacimiento y más)\n"
                    "4. 🤝 **Business Partners y Procesos** (licencias, ausentismo, urgencias y acompañamiento)\n\n"
                    "🔒 *Aviso de privacidad: Esta herramienta funciona con Inteligencia Artificial con fines estrictamente informativos (Ley 1581 de 2012). Por tu seguridad, no compartas en este chat tu cédula, desprendibles, salarios ni historias clínicas.*\n\n"
                    "¿Sobre cuál trámite o beneficio necesitas información?\n\n"
                    "Este asistente de Gestión Humana Más Cerca de Ti funciona con inteligencia artificial y puede cometer errores. "
                    "Te recomendamos validar la información o resolver cualquier duda con Stefanny Pulgarín, "
                    "Analista de Bienestar y RSE, o Michell Román, Asistente Gestión Humana."
                ),
                "sources": []
            }

        # 1. Recuperar fragmentos relevantes
        matches = self.vector_store.search(user_question, top_k=TOP_K_RESULTS)
        
        # 2. Formatear el contexto
        context_blocks = []
        sources = []
        for chunk, score in matches:
            context_blocks.append(
                f"--- DOCUMENTO: {chunk['source']} | SECCIÓN: {chunk['title']} (Relevancia: {score:.2f}) ---\n"
                f"{chunk['content']}\n"
            )
            sources.append({
                "source": chunk["source"],
                "section": chunk["title"],
                "score": round(score, 3)
            })
            
        full_context = "\n".join(context_blocks)
        
        # 3. Prompt de usuario enriquecido con contexto
        user_prompt = (
            f"CONTEXTO OFICIAL DE PREBEL:\n\n"
            f"{full_context}\n\n"
            f"PREGUNTA DEL COLABORADOR:\n"
            f"{user_question}\n\n"
            f"INSTRUCCIONES: Responde con exactitud basándote ÚNICAMENTE en el CONTEXTO anterior. "
            f"Si la información no está en el contexto, usa la frase exacta de contingencia. "
            f"Recuerda incluir siempre al final el mensaje obligatorio de descargo de responsabilidad."
        )
        
        # 4. Generación con Gemini
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.1,  # Temperatura baja para máxima fidelidad
                )
            )
            answer = response.text
        except Exception as e:
            answer = f"⚠️ Ocurrió un error al procesar tu solicitud: {str(e)}"
            
        return {
            "answer": answer,
            "sources": sources
        }


# Instancia singleton para reutilizar en API y tests
_agent_instance = None

def get_agent() -> PrebelAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PrebelAgent()
    return _agent_instance

def responder_pregunta(pregunta: str) -> str:
    """Función de interfaz lista para conectar con el servidor de WhatsApp."""
    agent = get_agent()
    result = agent.ask(pregunta)
    return result["answer"]
