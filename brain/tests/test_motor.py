"""Pruebas del motor sin LLM: fragmentación, recuperación y validación de citas."""

from brain import chatbot_groq as c

INSTRUCCIONES, FRAGMENTOS = c.cargar_corpus()
INDICE = c.BM25(FRAGMENTOS)


def top(consulta, k=c.TOP_K):
    return [FRAGMENTOS[i]["seccion"] for i, _ in INDICE.buscar(consulta, k)]


def test_corpus_carga_e_incluye_indices():
    assert INSTRUCCIONES and len(FRAGMENTOS) > 90
    assert any(f["seccion"] == "Índice de temas de Creditos Prebel" for f in FRAGMENTOS)


def test_citas_sin_jerarquia_heredada_erronea():
    secciones = {f["seccion"] for f in FRAGMENTOS}
    assert "Auxilios y beneficios Prebel > Auxilio de matrimonio" in secciones
    assert not any("Auxilios educativos o bonos de desarrollo > Auxilio de" in s for s in secciones)
    assert not any(s.startswith("Padres >") for s in secciones)


def test_sinonimos_coloquiales():
    assert any("Auxilio visual" in s for s in top("auxilio de gafas", 3))
    assert any("Índice de temas de Creditos" in s for s in top("me prestan plata para una moto", 3))


def test_vivienda_recupera_adquisicion():
    assert any("adquisición de vivienda o lote" in s for s in top("Requisitos para el crédito de vivienda"))


def test_contexto_respeta_tope():
    assert len(c.construir_contexto(FRAGMENTOS, INDICE, "credito vivienda requisitos")) <= c.MAX_CONTEXT_CHARS


ETIQUETAS = [("Creditos_Prebel_20260310.md", "CRÉDITO PARA CASOS ESPECIALES DE SALUD")]


def test_cita_valida_se_conserva():
    r = "Texto\nFuente: Creditos_Prebel_20260310.md → CRÉDITO PARA CASOS ESPECIALES DE SALUD"
    assert c.validar_fuentes(r, ETIQUETAS) == r


def test_cita_inventada_se_corrige():
    r = c.validar_fuentes("Texto\nFuente: Creditos_Prebel_20260310.md → Listado general", ETIQUETAS)
    assert "Listado general" not in r and "CASOS ESPECIALES DE SALUD" in r


def test_cita_de_archivo_ajeno_se_elimina():
    assert c.validar_fuentes("Texto\n\nFuente: Otro.md → X\n\nAviso", ETIQUETAS) == "Texto\n\nAviso"
