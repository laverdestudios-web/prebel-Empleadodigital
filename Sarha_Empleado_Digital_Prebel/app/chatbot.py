"""Rule-compliant HR Chatbot engine grounded exclusively in docs/*.md."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import httpx

from app.config import Settings
from app.knowledge import KnowledgeBase, KnowledgeChunk, SearchHit, strip_accents, tokenize
from app.menu import MENU_NODES, MenuNode, format_menu_text, resolve_menu_chunks
from app.metrics import metrics

OUT_OF_SCOPE_MESSAGE = (
    "Lo siento, esa información no está disponible en este momento, "
    "ya que mi conocimiento se limita únicamente a los documentos cargados."
)

PRIVACY_BLOCK_MESSAGE = (
    "🔒 Por tu seguridad y en cumplimiento de las políticas de protección de datos de Prebel "
    "(Ley 1581 de 2012), este asistente no recibe documentos personales, historias clínicas, "
    "incapacidades ni consulta saldos o salarios individuales.\n\n"
    "Para radicar tu documento o recibir atención personalizada, comunícate directamente con el "
    "canal autorizado de Gestión Humana correspondiente a tu nómina (PA, PO, PI o PP). "
    "Puedes escribir *5* para ver el directorio oficial de contactos."
)

DISCLAIMER_MESSAGE = (
    "ℹ️ Este asistente virtual SARHA (Gestión Humana Prebel) funciona con inteligencia artificial "
    "y puede cometer errores. Su contenido es meramente orientativo con base en los documentos "
    "autorizados por Prebel. Te recomendamos validar la información o resolver dudas específicas "
    "con Stefanny Pulgarín (Bienestar y RSE) o Michell Román (Asistente de Gestión Humana)."
)

PRIVATE_DATA_PATTERNS = (
    r"\bdesprendible[s]?\b",
    r"\bmi\s+(salario|sueldo|nomina|liquidacion)\b",
    r"\bsaldo[s]?\s+(de\s+)?(vacaciones|cesantias|credito[s]?)\b",
    r"\bcuanto\s+(gano|me\s+pagan|tengo\s+en\s+cesantias)\b",
    r"\bhistoria[s]?\s+clinica[s]?\b",
    r"\b(mi\s+)?(cedula|cc)\s*[:#]?\s*\d{6,11}\b",
    r"\bdiagnostico\s+(medico|psicologico)\b",
)

EXCLUDED_POLICY_PATTERNS = (
    r"\bacoso\s+laboral\b",
    r"\bconvivencia\s+laboral\b",
    r"\breglamento\s+interno\b",
    r"\bdotacion\b",
)

GREETING_WORDS = {
    "hola", "buenos dias", "buenas tardes", "buenas noches", "saludos",
    "hey", "que tal", "buen dia", "menu", "inicio", "ayuda", "opciones",
}


@dataclass
class ChatResponse:
    """Structured response returned by the chatbot."""

    answer: str
    sources: list[dict[str, str]] = field(default_factory=list)
    mode: str = "local_rag"
    is_out_of_scope: bool = False
    suggested_questions: list[str] = field(default_factory=list)
    menu_options: list[dict[str, str]] = field(default_factory=list)


class HRChatbot:
    """Prebel Gestión Humana chatbot grounded strictly in the Markdown knowledge base."""

    def __init__(self, kb: KnowledgeBase, settings: Settings) -> None:
        self.kb = kb
        self.settings = settings
        self._sessions: dict[str, str] = {}

    def reset_session(self, session_id: str = "default") -> None:
        """Reset a user session back to the root menu."""
        self._sessions[session_id] = "root"

    def answer(self, question: str, channel: str = "web", session_id: str = "default") -> ChatResponse:
        """Process a user query or numeric menu choice and return a grounded response."""
        raw_q = (question or "").strip()
        current_node_id = self._sessions.get(session_id, "root")
        current_node = MENU_NODES.get(current_node_id, MENU_NODES["root"])

        if not raw_q:
            return self._render_menu("root", channel=channel, session_id=session_id)

        norm_q = strip_accents(raw_q)
        norm_clean = re.sub(r"[^\w\s]", "", norm_q).strip()

        # 1. Numeric menu selection (e.g., "1", "2", "0", "00")
        if re.fullmatch(r"\d{1,2}", norm_clean):
            resp = self._handle_menu_number(norm_clean, current_node, channel=channel, session_id=session_id)
            cat = resp.sources[0]["category"] if resp.sources else current_node.title
            metrics.record_query(channel=channel, category=cat, is_out_of_scope=resp.is_out_of_scope, is_menu=True)
            return resp

        # 2. Greeting or menu request
        if norm_clean in GREETING_WORDS:
            resp = self._render_menu("root", channel=channel, session_id=session_id)
            metrics.record_query(channel=channel, category="Menú Principal", is_out_of_scope=False, is_menu=True)
            return resp

        # 2.5 Privacy / sensitive PII or explicitly excluded topic guard (Ley 1581 & Policy 2.4/5.1)
        if any(re.search(pat, norm_q) for pat in PRIVATE_DATA_PATTERNS):
            metrics.record_query(channel=channel, category=None, is_out_of_scope=True, is_privacy_block=True)
            return ChatResponse(
                answer=PRIVACY_BLOCK_MESSAGE,
                sources=[],
                mode=self._active_mode(),
                is_out_of_scope=True,
                suggested_questions=["5. Contactos, Urgencias, ARL y Códigos PA/PO/PI/PP", "00. Menú principal"],
            )

        if any(re.search(pat, norm_q) for pat in EXCLUDED_POLICY_PATTERNS):
            metrics.record_query(channel=channel, category=None, is_out_of_scope=True)
            return ChatResponse(
                answer=OUT_OF_SCOPE_MESSAGE,
                sources=[],
                mode=self._active_mode(),
                is_out_of_scope=True,
                suggested_questions=["00. Menú principal", "5. Contactos, Urgencias, ARL y Códigos PA/PO/PI/PP"],
            )

        # 3. Ambiguous broad queries (per Instrucciones_Tono_Ejemplos_Restricciones.md)
        ambiguous = self._check_ambiguity(norm_clean, channel=channel, session_id=session_id)
        if ambiguous is not None:
            metrics.record_query(channel=channel, category="Desambiguación", is_out_of_scope=False, is_menu=True)
            return ambiguous

        # 4. Retrieve relevant hits from docs/*.md
        hits = self.kb.search_hits(raw_q, top_k=5)
        if not hits or not self._is_grounded_hit(hits[0]):
            metrics.record_query(channel=channel, category=None, is_out_of_scope=True)
            return ChatResponse(
                answer=OUT_OF_SCOPE_MESSAGE,
                sources=[],
                mode=self._active_mode(),
                is_out_of_scope=True,
                suggested_questions=["00", "1", "2", "3", "4", "5"],
                menu_options=[
                    {"number": "00", "label": "Ver menú principal"},
                ],
            )

        best = hits[0]
        selected_chunks: list[KnowledgeChunk] = [best.chunk]
        for hit in hits[1:]:
            if len(selected_chunks) >= 3:
                break
            if hit.score >= best.score * 0.80 and hit.title_hits >= max(1, best.title_hits):
                selected_chunks.append(hit.chunk)

        resp = self._build_grounded_response(raw_q, selected_chunks, channel=channel)
        metrics.record_query(channel=channel, category=best.chunk.category, is_out_of_scope=False)
        return resp

    def _handle_menu_number(
        self,
        choice: str,
        current_node: MenuNode,
        channel: str,
        session_id: str,
    ) -> ChatResponse:
        if choice == "00" or (choice == "0" and current_node.parent_id is None):
            return self._render_menu("root", channel=channel, session_id=session_id)

        if choice == "0" and current_node.parent_id:
            return self._render_menu(current_node.parent_id, channel=channel, session_id=session_id)

        selected = next((item for item in current_node.items if item.number == choice), None)
        if selected is None:
            bold = "*" if channel == "whatsapp" else "**"
            return ChatResponse(
                answer=(
                    f"La opción {bold}{choice}{bold} no está en el menú actual ({current_node.title}).\n\n"
                    f"{format_menu_text(current_node, channel=channel)}"
                ),
                mode=self._active_mode(),
                suggested_questions=self._menu_chips(current_node),
                menu_options=self._menu_options_payload(current_node),
            )

        if selected.next_node:
            return self._render_menu(selected.next_node, channel=channel, session_id=session_id)

        # Leaf item: resolve exact chunks from docs/*.md
        chunks = resolve_menu_chunks(self.kb, selected)
        if not chunks:
            return ChatResponse(answer=OUT_OF_SCOPE_MESSAGE, mode=self._active_mode(), is_out_of_scope=True)

        resp = self._build_grounded_response(selected.label, chunks, channel=channel)
        nav_hint = (
            "\n\n_Escribe *0* para volver al menú anterior, *00* para el menú principal, u otro número de este menú._"
            if channel == "whatsapp"
            else "\n\nEscribe **0** para volver al menú anterior, **00** para el menú principal, u otro número de este menú."
        )
        resp.answer = f"{resp.answer}{nav_hint}"
        resp.menu_options = self._menu_options_payload(current_node)
        resp.suggested_questions = self._menu_chips(current_node)
        return resp

    def _render_menu(self, node_id: str, channel: str, session_id: str) -> ChatResponse:
        self._sessions[session_id] = node_id
        node = MENU_NODES[node_id]
        return ChatResponse(
            answer=format_menu_text(node, channel=channel),
            mode=self._active_mode(),
            suggested_questions=self._menu_chips(node),
            menu_options=self._menu_options_payload(node),
        )

    @staticmethod
    def _menu_options_payload(node: MenuNode) -> list[dict[str, str]]:
        opts = [{"number": i.number, "label": i.label} for i in node.items]
        if node.parent_id:
            opts.append({"number": "0", "label": "Volver al menú anterior"})
            opts.append({"number": "00", "label": "Menú principal"})
        return opts

    @staticmethod
    def _menu_chips(node: MenuNode) -> list[str]:
        chips = [f"{i.number}. {i.label}" for i in node.items[:6]]
        if node.parent_id:
            chips.append("0. Volver")
        return chips

    def _build_grounded_response(
        self,
        question: str,
        selected_chunks: list[KnowledgeChunk],
        channel: str,
    ) -> ChatResponse:
        mode = self._active_mode()
        if mode != "local_rag":
            llm_text = self._try_llm_synthesis(question, selected_chunks, mode)
            if llm_text:
                return ChatResponse(
                    answer=llm_text,
                    sources=self._format_sources(selected_chunks),
                    mode=mode,
                    suggested_questions=self._follow_up_suggestions(selected_chunks),
                )

        formatted = self._format_deterministic_answer(selected_chunks, channel=channel)
        return ChatResponse(
            answer=formatted,
            sources=self._format_sources(selected_chunks),
            mode="local_rag",
            suggested_questions=self._follow_up_suggestions(selected_chunks),
        )

    @staticmethod
    def _is_grounded_hit(hit: SearchHit) -> bool:
        """Verify the top search hit actually covers the query rather than a stray word."""
        if hit.total_query_terms == 1:
            return hit.score >= 2.0 and (hit.title_hits >= 1 or hit.score >= 3.5)
        if hit.total_query_terms == 2:
            return hit.matched_terms == 2 and hit.score >= 2.8
        coverage = hit.matched_terms / hit.total_query_terms
        if hit.matched_terms < 2 or coverage < 0.55:
            return False
        return hit.score >= 3.0

    def _active_mode(self) -> str:
        provider = self.settings.llm_provider
        if provider == "gemini" and self.settings.gemini_api_key:
            return "gemini"
        if provider == "openai" and self.settings.openai_api_key:
            return "openai"
        if provider == "ollama" and self.settings.ollama_base_url:
            return "ollama"
        return "local_rag"

    def _check_ambiguity(
        self,
        norm_clean: str,
        channel: str,
        session_id: str,
    ) -> ChatResponse | None:
        tokens = set(tokenize(norm_clean, remove_stopwords=True))
        if tokens and tokens <= {"credito", "creditos", "prestamo", "prestamos"}:
            return self._render_menu("creditos", channel=channel, session_id=session_id)

        if tokens and tokens <= {"auxilio", "auxilios", "beneficio", "beneficios"}:
            return self._render_menu("auxilios", channel=channel, session_id=session_id)

        if tokens and tokens <= {"cesantia", "cesantias", "retiro", "retirar"} and (
            "cesantia" in tokens or "cesantias" in tokens
        ):
            return self._render_menu("cesantias", channel=channel, session_id=session_id)

        return None

    def _format_deterministic_answer(self, chunks: list[KnowledgeChunk], channel: str = "web") -> str:
        sections: list[str] = []
        seen_contents: set[str] = set()
        for chunk in chunks:
            cleaned = chunk.content.strip()
            if cleaned in seen_contents:
                continue
            seen_contents.add(cleaned)
            cleaned = re.sub(r"^\[\s*\]\s*", "- ", cleaned, flags=re.MULTILINE)
            sections.append(f"**{chunk.section_path}**\n{cleaned}")

        body = "\n\n".join(sections)
        primary = chunks[0]
        source_line = f"Fuente: {primary.source_file} → {primary.section_path}"

        if channel == "whatsapp":
            body_wa = re.sub(r"\*\*(.+?)\*\*", r"*\1*", body)
            return (
                f"¡Claro! Esto es lo que necesitas saber:\n\n"
                f"{body_wa}\n\n"
                f"Si necesitas más detalles, aquí estoy para ayudarte.\n\n"
                f"_{source_line}_\n\n"
                f"_{DISCLAIMER_MESSAGE}_"
            )

        return (
            f"¡Claro! Esto es lo que necesitas saber:\n\n"
            f"{body}\n\n"
            f"Si necesitas más detalles, aquí estoy para ayudarte.\n\n"
            f"`{source_line}`\n\n"
            f"*{DISCLAIMER_MESSAGE}*"
        )

    def _format_sources(self, chunks: list[KnowledgeChunk]) -> list[dict[str, str]]:
        return [
            {
                "file": c.source_file,
                "category": c.category,
                "section": c.section_path,
            }
            for c in chunks
        ]

    def _follow_up_suggestions(self, chunks: list[KnowledgeChunk]) -> list[str]:
        cat = chunks[0].category
        if cat == "Vinculación y Nómina":
            return [
                "0. Volver al menú anterior",
                "00. Menú principal",
                "¿Cómo reporto una incapacidad?",
                "¿Dónde consulto mis días de vacaciones?",
            ]
        if cat == "Créditos y Condiciones":
            return [
                "0. Volver al menú anterior",
                "00. Menú principal",
                "¿Cuánto tarda la aprobación del crédito?",
            ]
        if cat == "Auxilios y Beneficios":
            return [
                "0. Volver al menú anterior",
                "00. Menú principal",
                "¿A quién solicito información sobre auxilios?",
            ]
        return [
            "0. Volver al menú anterior",
            "00. Menú principal",
            "¿Quién es mi Business Partner de Gestión Humana?",
        ]

    def _try_llm_synthesis(
        self,
        question: str,
        chunks: list[KnowledgeChunk],
        provider: str,
    ) -> str | None:
        """Optionally synthesize answer with Gemini, OpenAI, or Ollama while strictly grounded."""
        context_blocks = "\n\n---\n\n".join(
            f"[Archivo: {c.source_file} | Sección: {c.section_path}]\n{c.content}"
            for c in chunks
        )
        system_prompt = (
            f"{self.kb.instructions_text}\n\n"
            "CONTEXTO RECUPERADO DE LOS DOCUMENTOS OFICIALES:\n"
            f"{context_blocks}\n\n"
            "Responde exclusivamente usando el contexto anterior, sin inventar ni omitir cifras, "
            "plazos, requisitos ni contactos."
        )

        try:
            if provider == "gemini":
                url = (
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{self.settings.gemini_model}:generateContent?key={self.settings.gemini_api_key}"
                )
                payload = {
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": question}]}],
                    "generationConfig": {"temperature": 0.1},
                }
                resp = httpx.post(url, json=payload, timeout=20.0)
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()

            if provider == "openai":
                resp = httpx.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                    json={
                        "model": self.settings.openai_model,
                        "temperature": 0.1,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question},
                        ],
                    },
                    timeout=20.0,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"].strip()

            if provider == "ollama":
                resp = httpx.post(
                    f"{self.settings.ollama_base_url.rstrip('/')}/api/chat",
                    json={
                        "model": self.settings.ollama_model,
                        "stream": False,
                        "options": {"temperature": 0.1},
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": question},
                        ],
                    },
                    timeout=30.0,
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"].strip()
        except Exception:
            return None
        return None
