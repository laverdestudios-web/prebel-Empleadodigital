"""
Ingesta y segmentación semántica de los documentos oficiales de Prebel.
Divide cada documento por secciones temáticas respetando tablas, requisitos y contactos.
"""
import re
from pathlib import Path
from typing import List, Dict

KNOWLEDGE_FILES = [
    "Aclaraciones_y_Contactos_Prebel_2026.md",
    "Auxilios_y_beneficios_Prebel_20260310.md",
    "Creditos_Prebel_20260310.md",
    "Vinculacion_y_nomina_20260310.md",
    "Glosario_Business_Partner_20260922.md",
]


def clean_markdown_text(text: str) -> str:
    """Limpia etiquetas HTML residuales conservando la estructura."""
    text = re.sub(r'</?u>', '', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    return text


def split_into_chunks(text: str, filename: str) -> List[Dict[str, str]]:
    """
    Divide el documento en chunks basados en títulos markdown, preguntas o términos en negrita.
    """
    cleaned = clean_markdown_text(text)
    
    # Patrón que detecta:
    # 1. Headers Markdown (#, ##, ###)
    # 2. Títulos en negrita independientes (**Auxilio...:**)
    # 3. Items de lista con título en negrita (- **Término**: o - **Término:** texto)
    # 4. Preguntas en negrita (**¿Qué es...?**)
    header_pattern = re.compile(
        r'^(?:'
        r'#{1,4}\s+[^\n]+|'
        r'(?:[-*]\s+)?\*\*[^*]{3,80}\*\*:?|'
        r'\*\*¿[^*]+\?\*\*'
        r')', 
        re.MULTILINE
    )
    
    matches = list(header_pattern.finditer(cleaned))
    chunks = []
    
    if not matches:
        return [{
            "source": filename,
            "title": "General",
            "content": cleaned.strip()
        }]
    
    # Preámbulo si existe
    if matches[0].start() > 30:
        pre_content = cleaned[:matches[0].start()].strip()
        if len(pre_content) > 50:
            chunks.append({
                "source": filename,
                "title": "Introducción",
                "content": pre_content
            })
    
    for i, match in enumerate(matches):
        raw_header = match.group().strip()
        clean_title = (
            raw_header
            .lstrip('#')
            .lstrip('-')
            .lstrip('*')
            .strip()
            .strip('*')
            .strip(':')
            .strip()
        )
        
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(cleaned)
        content = cleaned[start:end].strip()
        
        # Filtro de tamaño mínimo
        if len(content) > 35:
            chunks.append({
                "source": filename,
                "title": clean_title,
                "content": content
            })
            
    return chunks


def load_all_chunks(docs_dir: Path) -> List[Dict[str, str]]:
    """Carga y procesa todos los archivos de conocimiento de Prebel."""
    all_chunks = []
    for filename in KNOWLEDGE_FILES:
        filepath = docs_dir / filename
        if not filepath.exists():
            print(f"⚠️ Archivo no encontrado: {filepath}")
            continue
        
        text = filepath.read_text(encoding="utf-8")
        chunks = split_into_chunks(text, filename)
        print(f"📄 {filename} → {len(chunks)} secciones temáticas.")
        all_chunks.extend(chunks)
        
    print(f"\n✅ Total de fragmentos de conocimiento extraídos: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    from config import DOCS_DIR
    chunks = load_all_chunks(DOCS_DIR)
    print("\nÚltimos 5 chunks:")
    for c in chunks[-5:]:
        print(f"- [{c['source']}] {c['title']} ({len(c['content'])} caracteres)")
