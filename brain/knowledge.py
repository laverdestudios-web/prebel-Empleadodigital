"""
Base de conocimiento de Prebel.

Con Claude no se usa búsqueda vectorial: los cuatro documentos oficiales (~25k tokens)
caben completos en el contexto del modelo y se envían en cada consulta como un bloque
fijo del system prompt, almacenado en la caché de prompts de Anthropic. Así el modelo
siempre ve todo el contenido (no hay fragmentos que la búsqueda deje por fuera) y el
costo de releerlo es ~10% del precio normal de entrada.
"""
import re
from pathlib import Path
from typing import List

from config import DOCS_DIR, KNOWLEDGE_FILES


def clean_markdown_text(text: str) -> str:
    """Limpia etiquetas HTML residuales conservando la estructura markdown."""
    text = re.sub(r"</?u>", "", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text.strip()


def load_knowledge_base(docs_dir: Path = DOCS_DIR, files: List[str] = KNOWLEDGE_FILES) -> str:
    """
    Concatena los documentos oficiales en un único texto delimitado por etiquetas XML,
    para que el modelo pueda distinguir de qué documento proviene cada dato.

    El orden y el contenido son deterministas: cualquier cambio de bytes invalida la caché.
    """
    missing = [f for f in files if not (docs_dir / f).exists()]
    if missing:
        raise FileNotFoundError(f"Documentos de conocimiento no encontrados en {docs_dir}: {missing}")

    parts = []
    for filename in files:
        content = clean_markdown_text((docs_dir / filename).read_text(encoding="utf-8"))
        parts.append(f'<documento nombre="{filename}">\n{content}\n</documento>')

    return "<documentos_oficiales_prebel>\n" + "\n\n".join(parts) + "\n</documentos_oficiales_prebel>"


if __name__ == "__main__":
    kb = load_knowledge_base()
    print(f"Documentos: {len(KNOWLEDGE_FILES)}")
    print(f"Caracteres: {len(kb):,}")
    print(f"Tokens estimados (~3.3 caracteres/token en español): {len(kb) / 3.3:,.0f}")
