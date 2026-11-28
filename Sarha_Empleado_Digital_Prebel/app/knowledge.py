"""Knowledge base loader, Markdown/HTML parser, and BM25 + keyword retriever."""

from __future__ import annotations

import html
import math
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

INSTRUCTIONS_FILENAME = "Instrucciones_Tono_Ejemplos_Restricciones.md"
EXCLUDED_DOC_FILENAMES = {
    INSTRUCTIONS_FILENAME,
    "politica-etica-seguridad-prebel.md",
}

SPANISH_STOPWORDS = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con",
    "contra", "cual", "cuales", "cuando", "de", "del", "desde", "donde",
    "dos", "el", "ella", "ellas", "ellos", "en", "entre", "era", "es",
    "esa", "esas", "ese", "eso", "esos", "esta", "estaba", "estado",
    "estan", "estar", "estas", "este", "esto", "estos", "fue", "fueron",
    "ha", "haber", "habia", "han", "has", "hasta", "hay", "la", "las",
    "le", "les", "lo", "los", "mas", "me", "mi", "mis", "mucho", "muy",
    "nada", "ni", "no", "nos", "nosotros", "o", "os", "otra", "otras",
    "otro", "otros", "para", "pero", "por", "porque", "que", "quien",
    "quienes", "se", "sea", "ser", "si", "sin", "sobre", "somos", "son",
    "soy", "su", "sus", "te", "ten", "tener", "tengo", "ti", "tiene",
    "tienen", "todo", "todos", "tu", "tus", "un", "una", "unas", "uno",
    "unos", "usted", "ustedes", "y", "ya", "yo", "quiero", "saber",
    "puedo", "necesito", "favor", "hola", "buenos", "buenas", "dias",
    "tardes", "noches", "informacion", "sobre", "acerca", "como", "cual",
    "cuales", "cuanto", "cuantos", "donde", "quien", "prebel",
    "actual", "actualmente", "hoy", "hablame", "cuentame", "dime",
    "explicame", "informame", "ayudame", "existen", "tienen", "hay",
    "ofrecen", "maneja", "manejan", "conocer",
}

CATEGORY_LABELS = {
    "Vinculacion_y_nomina_20260310.md": "Vinculación y Nómina",
    "Creditos_Prebel_20260310.md": "Créditos y Condiciones",
    "Auxilios_y_beneficios_Prebel_20260310.md": "Auxilios y Beneficios",
    "Glosario_Business_Partner_20260922.md": "Glosario y Business Partner",
    "Aclaraciones_y_Contactos_Prebel_2026.md": "Contactos, Urgencias y Aclaraciones",
}


def strip_accents(text: str) -> str:
    """Normalize text by removing diacritics and lowercasing."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    """Tokenize Spanish text into normalized alphanumeric terms."""
    cleaned = strip_accents(text)
    raw_tokens = re.findall(r"[a-z0-9]+", cleaned)
    if not remove_stopwords:
        return raw_tokens
    return [tok for tok in raw_tokens if tok not in SPANISH_STOPWORDS and len(tok) > 1]


def clean_inline_html(text: str) -> str:
    """Convert inline HTML tags found in the markdown files into clean markdown/text."""
    text = html.unescape(text)
    text = re.sub(r"</?u>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    return text


def _clean_cell_text(cell_html: str) -> str:
    cell_text = clean_inline_html(cell_html)
    cell_text = re.sub(r"<[^>]+>", "", cell_text)
    cell_text = re.sub(r"\n{3,}", "\n\n", cell_text)
    return cell_text.strip()


def html_tables_to_markdown(raw_text: str) -> str:
    """Merge split HTML <table> blocks and convert them into clean Markdown sections."""
    # Merge adjacent tables split across PDF/Word page breaks
    merged_raw = re.sub(r"</table>\s*<table>", "\n", raw_text, flags=re.IGNORECASE)
    table_pattern = re.compile(r"<table>(.*?)</table>", re.DOTALL | re.IGNORECASE)

    def _replace_table(match: re.Match[str]) -> str:
        table_html = match.group(1)
        rows = re.findall(r"<tr>(.*?)</tr>", table_html, flags=re.DOTALL | re.IGNORECASE)
        merged_entries: list[tuple[str, str]] = []

        for row_html in rows:
            cell_matches = re.findall(
                r"<t[hd]([^>]*)>(.*?)</t[hd]>",
                row_html,
                flags=re.DOTALL | re.IGNORECASE,
            )
            if not cell_matches:
                continue

            attrs_list = [m[0].lower() for m in cell_matches]
            cells = [_clean_cell_text(m[1]) for m in cell_matches]

            # Skip header rows
            if cells[0] in {"Motivo", "Nómina"}:
                continue

            # Continuation row from a split table:
            # e.g. <td rowspan="2"></td><td>inmobiliaria...</td> or <td colspan="2">matrimonio...</td>
            is_continuation = (
                (len(cells) >= 2 and cells[0] == "")
                or ("colspan=" in attrs_list[0] and not cells[0].startswith("**"))
            )
            if is_continuation and merged_entries:
                cont_text = "\n".join(c for c in cells if c)
                prev_title, prev_body = merged_entries[-1]
                separator = " " if prev_body and not prev_body.endswith((".", ":")) else "\n"
                merged_entries[-1] = (prev_title, f"{prev_body}{separator}{cont_text}".strip())
                continue

            non_empty = [c for c in cells if c]
            if len(non_empty) >= 2:
                title = non_empty[0].strip("* ").strip()
                body = "\n".join(non_empty[1:]).strip()
                merged_entries.append((title, body))
            elif len(non_empty) == 1 and merged_entries:
                prev_title, prev_body = merged_entries[-1]
                merged_entries[-1] = (prev_title, f"{prev_body}\n{non_empty[0]}".strip())

        if not merged_entries:
            return ""

        lines = [f"### {title}\n{body}" for title, body in merged_entries]
        return "\n\n" + "\n\n".join(lines) + "\n\n"

    return table_pattern.sub(_replace_table, merged_raw)


@dataclass
class KnowledgeChunk:
    """A self-contained section from a Prebel HR Markdown document."""

    chunk_id: str
    source_file: str
    category: str
    section_path: str
    title: str
    content: str
    tokens: list[str] = field(default_factory=list)
    title_tokens: list[str] = field(default_factory=list)


@dataclass
class SearchHit:
    """Ranked search result with score and coverage diagnostics."""

    chunk: KnowledgeChunk
    score: float
    matched_terms: int
    total_query_terms: int
    title_hits: int


class KnowledgeBase:
    """In-memory BM25 + title-boosted retriever over Prebel docs/*.md."""

    def __init__(self, docs_dir: Path) -> None:
        self.docs_dir = docs_dir
        self.instructions_text: str = ""
        self.chunks: list[KnowledgeChunk] = []
        self._doc_freq: dict[str, int] = {}
        self._avg_len: float = 1.0
        self.reload()

    def reload(self) -> None:
        """Load and index all Markdown documents in docs_dir."""
        self.chunks = []
        self._doc_freq = {}

        if not self.docs_dir.exists():
            return

        instructions_path = self.docs_dir / INSTRUCTIONS_FILENAME
        if instructions_path.exists():
            self.instructions_text = instructions_path.read_text(encoding="utf-8")

        for md_path in sorted(self.docs_dir.glob("*.md")):
            if md_path.name in EXCLUDED_DOC_FILENAMES:
                continue
            self.chunks.extend(self._parse_markdown_file(md_path))

        total_len = 0
        for chunk in self.chunks:
            chunk.tokens = tokenize(f"{chunk.section_path} {chunk.title} {chunk.content}")
            chunk.title_tokens = tokenize(f"{chunk.section_path} {chunk.title}")
            total_len += len(chunk.tokens)
            for term in set(chunk.tokens):
                self._doc_freq[term] = self._doc_freq.get(term, 0) + 1

        self._avg_len = (total_len / len(self.chunks)) if self.chunks else 1.0

    def _parse_markdown_file(self, md_path: Path) -> list[KnowledgeChunk]:
        raw = md_path.read_text(encoding="utf-8")
        raw = clean_inline_html(raw)
        raw = html_tables_to_markdown(raw)

        category = CATEGORY_LABELS.get(md_path.name, md_path.stem)

        if md_path.name == "Glosario_Business_Partner_20260922.md":
            return self._parse_glossary(md_path.name, category, raw)

        chunks: list[KnowledgeChunk] = []
        h1 = ""
        h2 = ""
        h3 = ""
        current_title = md_path.stem
        buffer: list[str] = []

        def _flush() -> None:
            text = "\n".join(buffer).strip()
            buffer.clear()
            if not text or text == "***":
                return
            path_parts = [p for p in (h1, h2, h3) if p]
            if not path_parts:
                path_parts = [current_title]
            section_path = " → ".join(dict.fromkeys(path_parts))
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{md_path.stem}_{len(chunks)}",
                    source_file=md_path.name,
                    category=category,
                    section_path=section_path,
                    title=current_title,
                    content=text,
                )
            )

        for line in raw.splitlines():
            stripped = line.strip()

            if stripped == "***":
                _flush()
                h1 = ""
                h2 = ""
                h3 = ""
                continue

            heading_match = re.match(r"^(#{1,4})\s+(.+)$", stripped)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip("* ").strip()
                _flush()

                # Keep sub-topics like "# Hijo(s)", "# Hijastro(s)", "# Padres" nested under numbered section 4
                is_numbered_top = bool(re.match(r"^\d+\.", title))
                if level == 1 and h2 and re.match(r"^\d+\.", h2) and not is_numbered_top:
                    h3 = title
                elif is_numbered_top and h1:
                    h2, h3 = title, ""
                elif level == 1:
                    h1, h2, h3 = title, "", ""
                elif level == 2:
                    h2, h3 = title, ""
                else:
                    h3 = title
                current_title = title
                continue

            # Standalone bold title or unbolded standalone question (e.g. "¿Cuáles son los requisitos...?")
            bold_header_match = re.match(r"^\*\*([^*]{4,220})\*\*:?$", stripped)
            plain_question_match = (
                stripped.startswith("¿") and stripped.endswith("?") and len(stripped) <= 220
            )
            if bold_header_match or plain_question_match:
                title = (
                    bold_header_match.group(1).strip().rstrip(":")
                    if bold_header_match
                    else stripped
                )
                _flush()
                if title.startswith("¿"):
                    if md_path.name == "Auxilios_y_beneficios_Prebel_20260310.md" and "solicitar información" in title.lower():
                        h2, h3 = title, ""
                    else:
                        h3 = title
                elif re.match(r"^\d+\.", title) and h1:
                    h2, h3 = title, ""
                elif md_path.name == "Auxilios_y_beneficios_Prebel_20260310.md" and h1:
                    h2, h3 = title, ""
                elif not h1:
                    h1 = title
                else:
                    h3 = title
                current_title = title
                continue

            buffer.append(line)

        _flush()
        return chunks

    def _parse_glossary(self, filename: str, category: str, raw: str) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        current_title = "Glosario Business Partner"
        buffer: list[str] = []

        def _flush() -> None:
            text = "\n".join(buffer).strip()
            buffer.clear()
            if not text:
                return
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"glossary_{len(chunks)}",
                    source_file=filename,
                    category=category,
                    section_path=f"Glosario → {current_title}",
                    title=current_title,
                    content=text,
                )
            )

        top_level_terms = (
            "Business Partner de Gestión Humana",
            "Accidente de trabajo",
            "Incidente de trabajo",
            "Ausentismo",
            "Onboarding",
            "Proceso Disciplinario",
            "Espacio de concertación",
            "Grupos Primarios",
            "Pacto Colectivo",
            "GPS",
            "GUION DE LIDERES",
        )
        ausentismo_subterms = (
            "Licencia remunerada",
            "Licencia no remunerada",
            "Licencia de maternidad",
            "Licencia de paternidad",
            "Licencia de luto",
            "Suspensión de contrato",
            "Incapacidades",
        )

        for line in raw.splitlines():
            stripped = line.strip()
            matched_term = next(
                (t for t in top_level_terms if stripped.lower().startswith(f"- **{t.lower()}")),
                None,
            )
            if matched_term:
                _flush()
                current_title = matched_term
            else:
                matched_sub = next(
                    (s for s in ausentismo_subterms if stripped.lower().startswith(f"- {s.lower()}:")),
                    None,
                )
                if matched_sub:
                    _flush()
                    current_title = f"Ausentismo → {matched_sub}"
            buffer.append(line)

        _flush()
        return chunks

    def search_hits(self, query: str, top_k: int = 5) -> list[SearchHit]:
        """Score and return detailed SearchHit objects using BM25 + title & phrase boost."""
        q_tokens = list(dict.fromkeys(tokenize(query)))
        if not q_tokens or not self.chunks:
            return []

        n_docs = len(self.chunks)
        k1 = 1.5
        b = 0.75
        q_norm = strip_accents(query)

        hits: list[SearchHit] = []
        for chunk in self.chunks:
            if not chunk.tokens:
                continue
            tf_map: dict[str, int] = {}
            for tok in chunk.tokens:
                tf_map[tok] = tf_map.get(tok, 0) + 1

            score = 0.0
            matched_terms = 0
            doc_len = len(chunk.tokens)
            for term in q_tokens:
                tf = tf_map.get(term, 0)
                if tf == 0 and len(term) >= 5:
                    # Allow a capped single prefix match for Spanish singular/plural stems
                    has_prefix = any(
                        len(doc_tok) >= 5 and (doc_tok.startswith(term[:5]) or term.startswith(doc_tok[:5]))
                        for doc_tok in tf_map
                    )
                    if has_prefix:
                        tf = 0.65
                if tf == 0:
                    continue

                matched_terms += 1
                df = self._doc_freq.get(term, 1)
                idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
                denom = tf + k1 * (1 - b + b * (doc_len / self._avg_len))
                score += idf * ((tf * (k1 + 1)) / denom)

            title_norm = strip_accents(f"{chunk.section_path} {chunk.title}")
            title_hits = sum(1 for t in q_tokens if t in title_norm)
            score += title_hits * 1.5

            q_clean = q_norm.strip("¿?¡! ")
            if len(q_clean) >= 6 and q_clean in strip_accents(chunk.title):
                score += 6.0
            if len(q_norm) >= 6 and q_norm in strip_accents(chunk.content):
                score += 2.5

            if score > 0:
                hits.append(
                    SearchHit(
                        chunk=chunk,
                        score=score,
                        matched_terms=matched_terms,
                        total_query_terms=len(q_tokens),
                        title_hits=title_hits,
                    )
                )

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:top_k]

    def search(self, query: str, top_k: int = 5) -> list[tuple[KnowledgeChunk, float]]:
        """Convenience wrapper returning (chunk, score) tuples."""
        return [(hit.chunk, hit.score) for hit in self.search_hits(query, top_k=top_k)]

    def list_categories(self) -> list[dict[str, object]]:
        """Return high-level categories and sample topics for the UI menu."""
        grouped: dict[str, list[str]] = {}
        for chunk in self.chunks:
            topics = grouped.setdefault(chunk.category, [])
            parts = chunk.section_path.split(" → ")
            label = parts[1] if len(parts) > 1 and parts[0].startswith("Chatbot") else parts[0]
            if label not in topics and len(topics) < 8:
                topics.append(label)
        return [{"category": cat, "topics": topics} for cat, topics in grouped.items()]
