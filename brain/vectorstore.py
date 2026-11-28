"""
Base de Conocimiento Vectorial ($0 costo, local, sin suscripciones).
Genera embeddings con gemini-embedding-001 y realiza búsqueda semántica con similitud de coseno.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
from google import genai

from config import (
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
    KNOWLEDGE_STORE_PATH,
    DOCS_DIR,
    TOP_K_RESULTS
)
from ingester import load_all_chunks


class PrebelVectorStore:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrada. Revisa tu archivo .env")
        self.client = genai.Client(api_key=api_key)
        self.chunks: List[Dict[str, str]] = []
        self.embeddings: np.ndarray = np.array([])
        
    def build_or_load(self, force_rebuild: bool = False):
        """Carga la base de datos existente o genera los embeddings desde cero."""
        if KNOWLEDGE_STORE_PATH.exists() and not force_rebuild:
            with open(KNOWLEDGE_STORE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.chunks = data["chunks"]
            self.embeddings = np.array(data["embeddings"], dtype=np.float32)
            if len(self.chunks) >= 99:
                return

        print("🚀 Generando base vectorial completa con documentos de Prebel...")
        raw_chunks = load_all_chunks(DOCS_DIR)
        
        all_embeddings = []
        valid_chunks = []
        total = len(raw_chunks)
        
        for i, c in enumerate(raw_chunks):
            text = f"{c['title']}\n{c['content']}"
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.models.embed_content(
                        model=EMBEDDING_MODEL,
                        contents=text
                    )
                    all_embeddings.append(response.embeddings[0].values)
                    valid_chunks.append(c)
                    time.sleep(0.65)  # Respeta cuota de 100 RPM del tier gratuito
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_s = 62 if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) else 5
                        time.sleep(wait_s)
                    else:
                        print(f"⚠️ Error en fragmento '{c['title']}': {e}")
            
            if (i + 1) % 15 == 0 or (i + 1) == total:
                print(f"   Embeddings: {i + 1}/{total}")
                
        self.chunks = valid_chunks
        self.embeddings = np.array(all_embeddings, dtype=np.float32)
        
        # Guardar en disco persistente
        KNOWLEDGE_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(KNOWLEDGE_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "chunks": self.chunks,
                "embeddings": self.embeddings.tolist()
            }, f, ensure_ascii=False)
            
        print(f"💾 Base de conocimiento guardada en {KNOWLEDGE_STORE_PATH}")
        print(f"✅ Total: {len(self.chunks)} vectores generados.")

    def search(self, query: str, top_k: int = TOP_K_RESULTS) -> List[Tuple[Dict[str, str], float]]:
        """Busca los fragmentos más relevantes para una consulta dada."""
        if len(self.chunks) == 0:
            self.build_or_load()
            
        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query
        )
        query_vec = np.array(response.embeddings[0].values, dtype=np.float32)
        
        norm_query = np.linalg.norm(query_vec)
        norm_embeddings = np.linalg.norm(self.embeddings, axis=1)
        
        similarities = np.dot(self.embeddings, query_vec) / (norm_embeddings * norm_query + 1e-10)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(similarities[idx])))
            
        return results


if __name__ == "__main__":
    store = PrebelVectorStore()
    store.build_or_load(force_rebuild=True)
