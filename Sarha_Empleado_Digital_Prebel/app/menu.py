"""Interactive numbered menu tree grounded directly in Prebel docs/*.md sections."""

from __future__ import annotations

from dataclasses import dataclass

from app.knowledge import KnowledgeBase, KnowledgeChunk, strip_accents


@dataclass(frozen=True)
class MenuItem:
    """Single numbered item inside a menu node."""

    number: str
    label: str
    next_node: str | None = None
    source_file: str | None = None
    section_keywords: tuple[str, ...] = ()


@dataclass(frozen=True)
class MenuNode:
    """A menu screen with a title, prompt, and numbered items."""

    node_id: str
    title: str
    parent_id: str | None
    items: tuple[MenuItem, ...]


MENU_NODES: dict[str, MenuNode] = {
    "root": MenuNode(
        node_id="root",
        title="Menú Principal · Gestión Humana Prebel",
        parent_id=None,
        items=(
            MenuItem("1", "Vinculación y Nómina", next_node="vinculacion"),
            MenuItem("2", "Créditos y Condiciones", next_node="creditos"),
            MenuItem("3", "Auxilios y Beneficios", next_node="auxilios"),
            MenuItem("4", "Glosario y Business Partner", next_node="glosario"),
            MenuItem("5", "Contactos, Urgencias, ARL y Códigos PA/PO/PI/PP", next_node="contactos_urgencias"),
        ),
    ),
    "vinculacion": MenuNode(
        node_id="vinculacion",
        title="1. Vinculación y Nómina",
        parent_id="root",
        items=(
            MenuItem("1", "Certificados laborales", next_node="certificados"),
            MenuItem("2", "Retiro de cesantías", next_node="cesantias"),
            MenuItem("3", "Inclusiones EPS", next_node="eps_inclusion"),
            MenuItem("4", "Inclusión caja de compensación familiar", next_node="caja_compensacion"),
            MenuItem(
                "5",
                "Traslados EPS",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("5. Traslados EPS", "5.1", "5.2", "5.3"),
            ),
            MenuItem(
                "6",
                "Traslado de fondo de pensiones privado a Colpensiones",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("6. Proceso traslado", "Colpensiones", "nómina administrativa", "nómina operativa", "impulso y mercadeo"),
            ),
            MenuItem(
                "7",
                "Días de vacaciones (consulta según tu nómina)",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("7. Dias de vacaciones",),
            ),
            MenuItem(
                "8",
                "Incapacidades (plazos y envío según tu nómina)",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("8. Incapacidades",),
            ),
            MenuItem(
                "9",
                "Soporte de pago de seguridad social",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("9. Soporte de Pago Seguridad social",),
            ),
            MenuItem(
                "10",
                "Actualización de datos",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("11. Actualización de datos",),
            ),
        ),
    ),
    "certificados": MenuNode(
        node_id="certificados",
        title="Certificados laborales · Selecciona tu nómina",
        parent_id="vinculacion",
        items=(
            MenuItem(
                "1",
                "Personal operativo",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("1.1 Personal operativo",),
            ),
            MenuItem(
                "2",
                "Personal Impulso y mercado",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("1.2 Personal Impulso y mercado",),
            ),
            MenuItem(
                "3",
                "Personal administrativo",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("1.3 Personal administrativo",),
            ),
        ),
    ),
    "cesantias": MenuNode(
        node_id="cesantias",
        title="Retiro de cesantías · Selecciona el motivo",
        parent_id="vinculacion",
        items=(
            MenuItem(
                "1",
                "Compra de vivienda",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("2. Requisitos retiro de cesantías → Compra de vivienda",),
            ),
            MenuItem(
                "2",
                "Reforma de vivienda",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("2. Requisitos retiro de cesantías → Reforma de vivienda",),
            ),
            MenuItem(
                "3",
                "Pago de impuesto predial",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("2. Requisitos retiro de cesantías → Pago de impuesto predial",),
            ),
            MenuItem(
                "4",
                "Pago de crédito hipotecario",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("2. Requisitos retiro de cesantías → Pago de crédito hipotecario",),
            ),
            MenuItem(
                "5",
                "Gastos notariales (solo escrituras)",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("2. Requisitos retiro de cesantías → Gastos notariales",),
            ),
            MenuItem(
                "6",
                "Estudio (directamente con el fondo de cesantías)",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("2. Requisitos retiro de cesantías → Estudio",),
            ),
        ),
    ),
    "eps_inclusion": MenuNode(
        node_id="eps_inclusion",
        title="Inclusiones EPS · Selecciona la consulta",
        parent_id="vinculacion",
        items=(
            MenuItem(
                "1",
                "Documentos generales para inclusión en EPS",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("3. Inclusiones EPS",),
            ),
            MenuItem(
                "2",
                "Canal de envío · Personal operativo",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("3.1 Personal operativo",),
            ),
            MenuItem(
                "3",
                "Canal de envío · Personal Impulso y mercado",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("3.2 Personal Impulso y mercado",),
            ),
            MenuItem(
                "4",
                "Canal de envío · Personal administrativo",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("3.3 Personal administrativo",),
            ),
        ),
    ),
    "caja_compensacion": MenuNode(
        node_id="caja_compensacion",
        title="Inclusión caja de compensación familiar · Selecciona opción",
        parent_id="vinculacion",
        items=(
            MenuItem(
                "1",
                "Cónyuge o compañero(a) permanente",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("4. Inclusión caja de compensación familiar → Cónyuge",),
            ),
            MenuItem(
                "2",
                "Hijo(s)",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("4. Inclusión caja de compensación familiar → Hijo(s)",),
            ),
            MenuItem(
                "3",
                "Hijastro(s)",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("4. Inclusión caja de compensación familiar → Hijastro(s)",),
            ),
            MenuItem(
                "4",
                "Padres",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("4. Inclusión caja de compensación familiar → Padres",),
            ),
            MenuItem(
                "5",
                "Hermano(s) huérfanos",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("4. Inclusión caja de compensación familiar → Hermano(s)",),
            ),
            MenuItem(
                "6",
                "A quién enviar documentos (según tu nómina)",
                source_file="Vinculacion_y_nomina_20260310.md",
                section_keywords=("4. Inclusión caja de compensación familiar → Personal",),
            ),
        ),
    ),
    "creditos": MenuNode(
        node_id="creditos",
        title="2. Créditos y Condiciones",
        parent_id="root",
        items=(
            MenuItem("1", "Crédito para educación y/o compra de computadores", next_node="cred_educacion"),
            MenuItem("2", "Crédito de grave calamidad doméstica de mascotas", next_node="cred_mascotas"),
            MenuItem("3", "Crédito para casos especiales de salud", next_node="cred_salud"),
            MenuItem("4", "Crédito de vivienda, reformas, legalización e impuesto predial", next_node="cred_vivienda"),
            MenuItem(
                "5",
                "Antigüedad mínima y persona de contacto para créditos",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("antigüedad debo tener", "persona de Gestión Humana que me puede ayudar"),
            ),
        ),
    ),
    "cred_educacion": MenuNode(
        node_id="cred_educacion",
        title="Crédito de educación y computadores · Selecciona una pregunta",
        parent_id="creditos",
        items=(
            MenuItem(
                "1",
                "¿Qué es y quiénes son beneficiarios?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Qué es el crédito para educación", "¿Quiénes son beneficiarios del crédito para educación"),
            ),
            MenuItem(
                "2",
                "¿Cuáles son los requisitos?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son los requisitos para solicitar el de crédito para educación",),
            ),
            MenuItem(
                "3",
                "¿Cuáles son las condiciones (monto, tasa, plazo)?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son las condiciones del crédito para educación",),
            ),
            MenuItem(
                "4",
                "¿A quién contactar, cuánto tarda y cómo se desembolsa?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿A quién me puedo dirigir para presentarle mi solicitud de crédito para educación", "¿Cuánto tarda el proceso de aprobación del crédito para educación", "¿Cómo es el proceso de desembolso para el crédito de educación", "¿El crédito para educación"),
            ),
        ),
    ),
    "cred_mascotas": MenuNode(
        node_id="cred_mascotas",
        title="Crédito de calamidad de mascotas · Selecciona una pregunta",
        parent_id="creditos",
        items=(
            MenuItem(
                "1",
                "¿Qué es, quiénes son beneficiarios y qué cubre?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Qué es el crédito de grave calamidad doméstica de mascotas", "¿Quiénes son beneficiarios del crédito de grave calamidad doméstica de mascotas", "¿Cuáles son las destinaciones para el crédito de grave calamidad"),
            ),
            MenuItem(
                "2",
                "¿Cuáles son los requisitos?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son los requisitos para solicitar el crédito de grave calamidad",),
            ),
            MenuItem(
                "3",
                "¿Cuáles son las condiciones (monto, tasa, plazo)?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son las condiciones para solicitar el crédito de grave calamidad",),
            ),
            MenuItem(
                "4",
                "¿A quién contactar, cuánto tarda y cómo se desembolsa?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿A quién me puedo dirigir para presentarle mi solicitud de crédito de grave calamidad", "tarda el proceso de aprobación del crédito de grave calamidad", "desembolso para el crédito de grave calamidad"),
            ),
        ),
    ),
    "cred_salud": MenuNode(
        node_id="cred_salud",
        title="Crédito casos especiales de salud · Selecciona una pregunta",
        parent_id="creditos",
        items=(
            MenuItem(
                "1",
                "¿Qué es, quiénes son beneficiarios y qué cubre?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Qué es el crédito para casos especiales de salud", "¿Quiénes son beneficiarios del crédito para casos especiales de salud", "¿Cuáles son las destinaciones para el crédito de casos especiales de salud"),
            ),
            MenuItem(
                "2",
                "¿Cuáles son los requisitos?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("requisitos para solicitar el crédito de casos especiales de salud",),
            ),
            MenuItem(
                "3",
                "¿Cuáles son las condiciones?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son las condiciones para solicitar el crédito de casos especiales de salud",),
            ),
            MenuItem(
                "4",
                "¿A quién contactar, cuánto tarda y cómo se desembolsa?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿A quién me puedo dirigir para presentarle mi solicitud de crédito para casos especiales de salud", "¿Cuánto tarda el proceso de aprobación del crédito para casos especiales de salud", "¿Cómo es el proceso de desembolso para el crédito de casos especiales de salud"),
            ),
        ),
    ),
    "cred_vivienda": MenuNode(
        node_id="cred_vivienda",
        title="Crédito de vivienda · Selecciona una pregunta",
        parent_id="creditos",
        items=(
            MenuItem(
                "1",
                "¿Qué es, beneficiarios y requisitos generales?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Qué es el crédito para préstamo de vivienda", "¿Quiénes son beneficiarios del crédito para préstamo de vivienda", "requisitos generales del crédito para préstamo de vivienda"),
            ),
            MenuItem(
                "2",
                "Requisitos para adquisición de vivienda o lote",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son los requisitos para la adquisición de vivienda o lote",),
            ),
            MenuItem(
                "3",
                "Requisitos para reforma de vivienda",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son los requisitos para reforma de vivienda",),
            ),
            MenuItem(
                "4",
                "Requisitos para calamidades habitacionales",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son los requisitos para calamidades habitacionales",),
            ),
            MenuItem(
                "5",
                "Requisitos para legalización y liberación de hipoteca",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son los requisitos para legalización del inmueble", "¿Cuáles son los requisitos para la liberación de gravámenes hipotecarios", "¿Cuáles son los requisitos para la escritura"),
            ),
            MenuItem(
                "6",
                "Requisitos para pago de impuesto predial",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿Cuáles son los requisitos para el pago del impuesto predial",),
            ),
            MenuItem(
                "7",
                "¿A quién contactar y cuánto tarda la aprobación?",
                source_file="Creditos_Prebel_20260310.md",
                section_keywords=("¿A quién me puedo dirigir para presentarle mi solicitud de crédito de vivienda", "¿Cuánto tarda el proceso de aprobación del crédito de vivienda"),
            ),
        ),
    ),
    "auxilios": MenuNode(
        node_id="auxilios",
        title="3. Auxilios y Beneficios · Selecciona una opción",
        parent_id="root",
        items=(
            MenuItem(
                "1",
                "Auxilios educativos o bonos de desarrollo (requisitos y valores)",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilios educativos o bonos de desarrollo",),
            ),
            MenuItem(
                "2",
                "Auxilio de incapacidad",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilio de incapacidad",),
            ),
            MenuItem(
                "3",
                "Auxilio visual u odontológico ($332.000)",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilio visual u odontológico",),
            ),
            MenuItem(
                "4",
                "Auxilio de alimentación (sedes e impulso y mercadeo)",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilio de alimentación",),
            ),
            MenuItem(
                "5",
                "Programas y auxilio de salud mental (Desahogadero / Red de amor)",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("programas de salud mental", "Auxilio de salud mental"),
            ),
            MenuItem(
                "6",
                "Auxilio de nacimiento, adopción y/o aborto",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilio de nacimiento, adopción y/o aborto",),
            ),
            MenuItem(
                "7",
                "Auxilio de matrimonio",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilio de matrimonio",),
            ),
            MenuItem(
                "8",
                "Auxilio por pensión de vejez o invalidez",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilio por pensión de vejez o invalidez",),
            ),
            MenuItem(
                "9",
                "Auxilio por muerte o invalidez / fallecimiento de familiares",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Auxilio por muerte",),
            ),
            MenuItem(
                "10",
                "Atención de Emergencias (EMI), Seguro de vida y Brigadistas",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("Atención de Emergencias (EMI)", "Seguro de vida o invalidez", "brigadistas"),
            ),
            MenuItem(
                "11",
                "¿A quién solicitar información sobre auxilios y beneficios?",
                source_file="Auxilios_y_beneficios_Prebel_20260310.md",
                section_keywords=("¿A quién puedo solicitar información sobre los auxilios", "¿A quién puedo solicitar información sobre los beneficios"),
            ),
        ),
    ),
    "glosario": MenuNode(
        node_id="glosario",
        title="4. Glosario y Business Partner · Selecciona un tema",
        parent_id="root",
        items=(
            MenuItem(
                "1",
                "¿Quién es mi Business Partner de Gestión Humana?",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Business Partner de Gestión Humana",),
            ),
            MenuItem(
                "2",
                "Licencias y ausentismo (maternidad, paternidad, luto, permisos)",
                next_node="licencias",
            ),
            MenuItem(
                "3",
                "Accidente e incidente de trabajo",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Accidente de trabajo", "Incidente de trabajo"),
            ),
            MenuItem(
                "4",
                "Proceso Disciplinario y Espacio de concertación",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Proceso Disciplinario", "Espacio de concertación"),
            ),
            MenuItem(
                "5",
                "Onboarding, Grupos Primarios, Pacto Colectivo, GPS y Guion de Líderes",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Onboarding", "Grupos Primarios", "Pacto Colectivo", "GPS", "GUION DE LIDERES"),
            ),
        ),
    ),
    "licencias": MenuNode(
        node_id="licencias",
        title="Licencias y ausentismo · Selecciona una opción",
        parent_id="glosario",
        items=(
            MenuItem(
                "1",
                "Licencia remunerada y no remunerada (permisos)",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Licencia remunerada", "Licencia no remunerada"),
            ),
            MenuItem(
                "2",
                "Licencia de maternidad (18 semanas)",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Licencia de maternidad",),
            ),
            MenuItem(
                "3",
                "Licencia de paternidad (2 semanas)",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Licencia de paternidad",),
            ),
            MenuItem(
                "4",
                "Licencia de luto (5 días hábiles)",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Licencia de luto",),
            ),
            MenuItem(
                "5",
                "Suspensión de contrato e incapacidades",
                source_file="Glosario_Business_Partner_20260922.md",
                section_keywords=("Suspensión de contrato", "Ausentismo → Incapacidades"),
            ),
        ),
    ),
    "contactos_urgencias": MenuNode(
        node_id="contactos_urgencias",
        title="5. Contactos, Urgencias, ARL y Aclaraciones",
        parent_id="root",
        items=(
            MenuItem(
                "1",
                "Directorio oficial de contactos de Gestión Humana",
                source_file="Aclaraciones_y_Contactos_Prebel_2026.md",
                section_keywords=("Directorio y matriz de contactos",),
            ),
            MenuItem(
                "2",
                "Canales de urgencias, emergencias médicas (EMI) y ARL",
                source_file="Aclaraciones_y_Contactos_Prebel_2026.md",
                section_keywords=("Canales de urgencias",),
            ),
            MenuItem(
                "3",
                "¿Qué significan los códigos PA, PO, PI y PP?",
                source_file="Aclaraciones_y_Contactos_Prebel_2026.md",
                section_keywords=("códigos de nómina PA",),
            ),
            MenuItem(
                "4",
                "Plazos de incapacidades (3 días vs 5 días hábiles)",
                source_file="Aclaraciones_y_Contactos_Prebel_2026.md",
                section_keywords=("plazos de incapacidades",),
            ),
            MenuItem(
                "5",
                "Registro de mascotas, Pacto Colectivo y empleados directos",
                source_file="Aclaraciones_y_Contactos_Prebel_2026.md",
                section_keywords=("Registro de mascotas", "Alcance de beneficios"),
            ),
            MenuItem(
                "6",
                "Privacidad, datos personales y alcance del chatbot",
                source_file="Aclaraciones_y_Contactos_Prebel_2026.md",
                section_keywords=("Seguridad, datos personales",),
            ),
        ),
    ),
}


def resolve_menu_chunks(kb: KnowledgeBase, item: MenuItem) -> list[KnowledgeChunk]:
    """Fetch exact chunks from KnowledgeBase matching a leaf MenuItem."""
    if not item.source_file or not item.section_keywords:
        return []
    matched: list[KnowledgeChunk] = []
    seen_ids: set[str] = set()
    kw_norms = [strip_accents(k) for k in item.section_keywords]
    for chunk in kb.chunks:
        if chunk.source_file != item.source_file:
            continue
        sec_norm = strip_accents(chunk.section_path)
        if any(kw in sec_norm for kw in kw_norms):
            if chunk.chunk_id not in seen_ids:
                seen_ids.add(chunk.chunk_id)
                matched.append(chunk)
    return matched


ROOT_EMOJIS = {
    "1": "📄 ",
    "2": "💳 ",
    "3": "🎁 ",
    "4": "🤝 ",
    "5": "📞 ",
}


def format_menu_text(node: MenuNode, channel: str = "web") -> str:
    """Format a MenuNode cleanly for Web or WhatsApp/Terminal."""
    bold = "*" if channel == "whatsapp" else "**"
    if node.node_id == "root":
        lines = [
            f"✨ {bold}{node.title}{bold} ✨",
            "",
            f"¡Hola! 👋 Soy {bold}SARHA{bold}, Servicios Automatizados de Recursos Humanos Ágiles. "
            "Tu asistente virtual para encontrar orientación, consultar información y acceder de forma sencilla a los servicios de Recursos Humanos. 😊",
            "",
            f"Responde con el {bold}número{bold} de la opción que deseas consultar (o escribe tu pregunta directamente): 👇",
            "",
        ]
    else:
        lines = [f"📋 {bold}{node.title}{bold}", ""]

    for item in node.items:
        emoji = ROOT_EMOJIS.get(item.number, "") if node.node_id == "root" else ""
        lines.append(f"{bold}{item.number}.{bold} {emoji}{item.label}")

    if node.parent_id:
        lines.append(f"{bold}0.{bold} ↩️ Volver al menú anterior ({bold}00.{bold} 🏠 Menú principal)")
    lines.append("")
    if node.node_id == "root":
        lines.append(
            "🔒 Aviso de privacidad: Herramienta con Inteligencia Artificial para fines informativos (Ley 1581 de 2012). "
            "Por tu seguridad, no compartas en este chat tu cédula, desprendibles, salarios ni historias clínicas."
        )
        lines.append("")
    lines.append("📌 Recuerda: este asistente responde únicamente con base en los documentos cargados.")
    return "\n".join(lines)
