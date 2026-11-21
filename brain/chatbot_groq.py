"""
Chatbot de Gestión Humana Prebel (prototipo de consola) sobre Groq o Gemini.

Responde solo con base en los documentos Markdown de docs/. En cada turno
recupera los fragmentos más relevantes (BM25, sin dependencias externas) y
los inyecta como contexto, en lugar de enviar todo el corpus (~80 KB) en cada
llamada, que excede los límites de tokens por minuto del plan gratuito de Groq.

Uso (cualquiera de los dos proveedores, vía API compatible con OpenAI):
    export GEMINI_API_KEY="..."            # aistudio.google.com
    # o bien
    export GROQ_API_KEY="gsk_..."          # console.groq.com
    export LLM_MODEL="..."                 # opcional, sobrescribe el modelo
    python brain/chatbot_groq.py
"""

import math
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from openai import OpenAI

# --------------------------------------------------------------------------
# Configuración
# --------------------------------------------------------------------------
DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
INSTRUCCIONES_FILE = "Instrucciones_Tono_Ejemplos_Restricciones.md"

PROVEEDORES = {
    "gemini": {
        "env_key": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "modelo": "gemini-flash-lite-latest",
    },
    "groq": {
        "env_key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "modelo": "qwen/qwen3-32b",
    },
}
TOP_K = 5                 # fragmentos recuperados por pregunta
MAX_CONTEXT_CHARS = 9000  # tope del contexto inyectado (~2.5k tokens)
MAX_CHUNK_CHARS = 2500    # tamaño máximo de un fragmento
MAX_TURNOS_HISTORIAL = 6  # pares usuario/asistente que se conservan
TEMPERATURE = 0.2         # baja: se busca fidelidad al texto, no creatividad

MENSAJE_NO_DISPONIBLE = (
    "Lo siento, esa información no está disponible en este momento, ya que mi "
    "conocimiento se limita únicamente a los documentos cargados."
)

STOPWORDS = set("""
a al algo algun alguna algunas alguno algunos ante antes como con contra cual
cuales cuando de del desde donde dos el ella ellas ellos en entre era es esa
esas ese eso esos esta estan estas este esto estos fue ha hay la las le les lo
los mas me mi mis muy no nos o otra otro para pero por porque que quien se
ser si sin sobre son su sus tambien te tengo tiene tu tus un una uno unos y ya
yo puedo quiero saber cual cuanto como hola favor gracias necesito
""".split())


# --------------------------------------------------------------------------
# Carga y fragmentación del corpus
# --------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def tokenizar(texto: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9]+", normalizar(texto))
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def titulo_negrita(linea: str) -> str | None:
    """Devuelve el texto si la línea completa está en negrita (**...**)."""
    m = re.fullmatch(r"\*\*([^*].*?)\*\*:?", linea.strip())
    return m.group(1).strip(" :") if m else None


def partir(fuente: str, seccion: str, cuerpo: str) -> list[dict]:
    cuerpo = cuerpo.strip()
    if len(cuerpo) < 40:
        return []
    return [
        {"fuente": fuente, "seccion": seccion, "texto": cuerpo[i:i + MAX_CHUNK_CHARS]}
        for i in range(0, len(cuerpo), MAX_CHUNK_CHARS)
    ]


def fragmentar_glosario(nombre: str, texto: str) -> list[dict]:
    """Documentos tipo glosario: un fragmento por término '- **Término**'."""
    fragmentos = []
    for bloque in re.split(r"\n(?=- \*\*)", texto):
        m = re.match(r"- \*\*(.+?)\*\*", bloque)
        seccion = m.group(1).strip(" :") if m else "Introducción"
        fragmentos.extend(partir(nombre, seccion, bloque))
    return fragmentos


def fragmentar(nombre: str, texto: str) -> list[dict]:
    """
    Divide un documento por encabezados conservando la ruta de títulos:
      - '#...'          -> encabezado jerárquico
      - '***' / '---'   -> separador: reinicia la ruta (cambio de tema)
      - '**Tema**'      -> tema (p. ej. '**Auxilio de matrimonio:**')
      - '**¿Pregunta?**'-> pregunta dentro del tema actual
    """
    if len(re.findall(r"^- \*\*", texto, flags=re.M)) >= 5:
        return fragmentar_glosario(nombre, texto)

    fragmentos, ruta, tema, pregunta, actual = [], {}, "", "", []

    def seccion() -> str:
        partes = [ruta[n] for n in sorted(ruta)] + [tema, pregunta]
        return " > ".join(p for p in partes if p)

    for linea in texto.splitlines():
        s = linea.strip()
        negrita = titulo_negrita(s)
        if s.startswith("#") or s in ("***", "---") or negrita:
            fragmentos.extend(partir(nombre, seccion(), "\n".join(actual)))
            actual = []
            if s.startswith("#"):
                nivel = len(s) - len(s.lstrip("#"))
                ruta = {n: t for n, t in ruta.items() if n < nivel}
                ruta[nivel] = s.lstrip("#").strip()
                tema = pregunta = ""
            elif s in ("***", "---"):
                ruta, tema, pregunta = {}, "", ""
                continue
            elif negrita.startswith("¿"):
                pregunta = negrita
            else:
                tema, pregunta = negrita, ""
        actual.append(linea)
    fragmentos.extend(partir(nombre, seccion(), "\n".join(actual)))
    return fragmentos


def cargar_corpus() -> tuple[str, list[dict]]:
    if not DOCS_DIR.is_dir():
        sys.exit(f"No se encontró la carpeta de documentos: {DOCS_DIR}")

    instrucciones, fragmentos = "", []
    for ruta in sorted(DOCS_DIR.glob("*.md")):
        texto = ruta.read_text(encoding="utf-8")
        if ruta.name == INSTRUCCIONES_FILE:
            instrucciones = texto
        else:
            fragmentos.extend(fragmentar(ruta.name, texto))

    if not fragmentos:
        sys.exit("No hay documentos de conocimiento en docs/.")
    return instrucciones, fragmentos


# --------------------------------------------------------------------------
# Recuperación BM25
# --------------------------------------------------------------------------
class BM25:
    def __init__(self, fragmentos: list[dict], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        # El título de sección se cuenta dos veces: suele contener el tema.
        self.docs = [
            tokenizar(f["seccion"]) * 2 + tokenizar(f["texto"]) for f in fragmentos
        ]
        self.tf = [Counter(d) for d in self.docs]
        self.len = [len(d) for d in self.docs]
        self.avgdl = sum(self.len) / len(self.len)
        n = len(self.docs)
        df = Counter(t for d in self.docs for t in set(d))
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def buscar(self, consulta: str, k: int) -> list[tuple[int, float]]:
        terminos = tokenizar(consulta)
        puntajes = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for t in terminos:
                if t not in tf:
                    continue
                f = tf[t]
                s += self.idf[t] * f * (self.k1 + 1) / (
                    f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avgdl)
                )
            if s > 0:
                puntajes.append((i, s))
        puntajes.sort(key=lambda x: x[1], reverse=True)
        return puntajes[:k]


def construir_contexto(fragmentos, indice, consulta) -> str:
    partes, total = [], 0
    for i, _ in indice.buscar(consulta, TOP_K):
        f = fragmentos[i]
        bloque = f"[Fuente: {f['fuente']} → {f['seccion']}]\n{f['texto']}"
        if total + len(bloque) > MAX_CONTEXT_CHARS:
            break
        partes.append(bloque)
        total += len(bloque)
    return "\n\n---\n\n".join(partes)


# --------------------------------------------------------------------------
# Prompt y chat
# --------------------------------------------------------------------------
def system_prompt(instrucciones: str, fuentes: list[str]) -> str:
    return (
        "Eres el asistente virtual de Gestión Humana de Prebel S.A.S. BIC. "
        "Atiendes a colaboradores (operativos, administrativos, impulso y "
        "mercadeo) sobre vinculación y nómina, créditos, auxilios y beneficios "
        "y conceptos de Gestión Humana.\n\n"
        "REGLAS CRÍTICAS:\n"
        "1. Responde ÚNICAMENTE con la información del bloque CONTEXTO que "
        "acompaña cada pregunta. No uses conocimiento externo ni inventes.\n"
        "2. Copia cifras, plazos, requisitos, nombres, correos y teléfonos "
        "exactamente como aparecen.\n"
        f"3. Si el CONTEXTO no contiene la respuesta, responde exactamente: "
        f"\"{MENSAJE_NO_DISPONIBLE}\"\n"
        "4. Si la pregunta es ambigua, ofrece las opciones que aparecen en el "
        "CONTEXTO para que el usuario elija.\n"
        "5. Al final indica la fuente con el formato 'Fuente: <archivo> → <sección>'.\n\n"
        f"Documentos disponibles: {', '.join(fuentes)}.\n\n"
        "INSTRUCCIONES DE TONO, FORMATO Y EJEMPLOS:\n"
        f"{instrucciones}"
    )


def limpiar_respuesta(texto: str) -> str:
    # Los modelos Qwen3 pueden devolver su razonamiento entre <think>...</think>.
    return re.sub(r"<think>.*?</think>", "", texto or "", flags=re.DOTALL).strip()


def main():
    nombre = os.environ.get("LLM_PROVIDER") or next(
        (n for n, p in PROVEEDORES.items() if os.environ.get(p["env_key"])), None
    )
    if nombre not in PROVEEDORES:
        sys.exit("Define GEMINI_API_KEY o GROQ_API_KEY (o LLM_PROVIDER=gemini|groq).")
    prov = PROVEEDORES[nombre]
    api_key = os.environ.get(prov["env_key"])
    if not api_key:
        sys.exit(f"Falta la variable de entorno {prov['env_key']}.")
    modelo = os.environ.get("LLM_MODEL", prov["modelo"])

    instrucciones, fragmentos = cargar_corpus()
    indice = BM25(fragmentos)
    fuentes = sorted({f["fuente"] for f in fragmentos})
    # Tiempo límite explícito: sin él, el SDK reintenta los 503 por saturación
    # del proveedor y la consola parece colgada.
    client = OpenAI(api_key=api_key, base_url=prov["base_url"], timeout=60, max_retries=2)

    system = {"role": "system", "content": system_prompt(instrucciones, fuentes)}
    historial: list[dict] = []  # solo pares usuario/asistente, sin contexto

    print(f"Proveedor: {nombre} | Modelo: {modelo}")
    print(f"Corpus: {len(fragmentos)} fragmentos de {len(fuentes)} documentos.")
    print("CHATBOT GESTIÓN HUMANA PREBEL — escribe 'salir' para terminar\n")

    while True:
        try:
            pregunta = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not pregunta:
            continue
        if pregunta.lower() == "salir":
            print("Asistente: ¡Hasta pronto!")
            break

        # Se recupera con la pregunta actual + la anterior para soportar
        # preguntas de seguimiento ("¿y cuáles son los requisitos?").
        previa = historial[-2]["content"] if len(historial) >= 2 else ""
        contexto = construir_contexto(fragmentos, indice, f"{previa} {pregunta}")

        mensaje_usuario = (
            f"CONTEXTO:\n{contexto or '(sin resultados en los documentos)'}\n\n"
            f"PREGUNTA DEL COLABORADOR:\n{pregunta}"
        )
        mensajes = [system] + historial[-2 * MAX_TURNOS_HISTORIAL:] + [
            {"role": "user", "content": mensaje_usuario}
        ]

        try:
            response = client.chat.completions.create(
                model=modelo,
                messages=mensajes,
                temperature=TEMPERATURE,
            )
            reply = limpiar_respuesta(response.choices[0].message.content)
        except Exception as e:  # red, límite de tasa, modelo inexistente, etc.
            print(f"[Error al consultar el modelo: {e}]\n")
            continue

        # En el historial se guarda la pregunta sin el contexto para no
        # multiplicar tokens en cada turno.
        historial.append({"role": "user", "content": pregunta})
        historial.append({"role": "assistant", "content": reply})
        print(f"Asistente: {reply}\n")


if __name__ == "__main__":
    main()
