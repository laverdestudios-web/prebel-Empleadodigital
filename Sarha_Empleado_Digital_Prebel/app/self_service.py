"""Guided self-service ('Autogestión') workflows backed by configurable config/contacts.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.config import BASE_DIR

CONTACTS_CONFIG_PATH = BASE_DIR / "config" / "contacts.json"


def load_contacts_config() -> dict:
    """Load the external configurable escalation & contacts matrix (never hardcoded)."""
    if CONTACTS_CONFIG_PATH.exists():
        return json.loads(CONTACTS_CONFIG_PATH.read_text(encoding="utf-8"))
    return {"contacts": {}, "urgencies": {}, "schedule": {}, "sla_ans": {}}


def _contact_str(key: str, default: str = "") -> str:
    cfg = load_contacts_config().get("contacts", {})
    item = cfg.get(key)
    if not item:
        return default
    parts = [item.get("name", "")]
    if item.get("email"):
        parts.append(item["email"])
    if item.get("phone"):
        parts.append(f"Celular: {item['phone']}")
    if item.get("whatsapp"):
        parts.append(f"WhatsApp: {item['whatsapp']}")
    return " · ".join(p for p in parts if p)


def _contact_email(key: str, default: str = "") -> str:
    cfg = load_contacts_config().get("contacts", {})
    return cfg.get(key, {}).get("email", default) or default


def _contact_wa(key: str, default: str = "") -> str:
    cfg = load_contacts_config().get("contacts", {})
    return cfg.get(key, {}).get("whatsapp", default) or default


@dataclass(frozen=True)
class SelfServiceOption:
    id: str
    label: str


PROCEDURES: dict[str, dict[str, object]] = {
    "certificado_laboral": {
        "title": "Certificado Laboral",
        "description": "Genera la guía exacta según tu tipo de nómina (sin almacenar datos personales).",
        "variants": [
            {"id": "operativo", "label": "Personal operativo (PO)"},
            {"id": "impulso", "label": "Personal Impulso y mercado (PI)"},
            {"id": "administrativo", "label": "Personal administrativo (PA)"},
        ],
    },
    "incapacidad": {
        "title": "Reporte de Incapacidad",
        "description": "Consulta el canal oficial autorizado y los plazos establecidos.",
        "variants": [
            {"id": "administrativo", "label": "Nómina administrativa (PA)"},
            {"id": "operativo", "label": "Nómina operativa (PO)"},
            {"id": "impulso", "label": "Nómina impulso y mercadeo (PI)"},
        ],
    },
    "cesantias": {
        "title": "Retiro de Cesantías",
        "description": "Checklist de documentos y carta modelo según el motivo del retiro.",
        "variants": [
            {"id": "compra_vivienda", "label": "Compra de vivienda"},
            {"id": "reforma_vivienda", "label": "Reforma de vivienda"},
            {"id": "impuesto_predial", "label": "Pago de impuesto predial"},
            {"id": "credito_hipotecario", "label": "Pago de crédito hipotecario"},
            {"id": "gastos_notariales", "label": "Gastos notariales (solo escrituras)"},
            {"id": "estudio", "label": "Estudio (directamente con el fondo)"},
        ],
    },
    "vacaciones": {
        "title": "Consulta de Días de Vacaciones",
        "description": "Verifica dónde consultar tu saldo de vacaciones según tu nómina.",
        "variants": [
            {"id": "administrativo", "label": "Nómina administrativa (PA)"},
            {"id": "operativo", "label": "Nómina operativa (PO)"},
            {"id": "impulso", "label": "Nómina impulso y mercado (PI)"},
        ],
    },
}


def list_procedures() -> list[dict[str, object]]:
    """Return available self-service procedures for the UI."""
    return [
        {
            "id": proc_id,
            "title": data["title"],
            "description": data["description"],
            "variants": data["variants"],
        }
        for proc_id, data in PROCEDURES.items()
    ]


def build_self_service_guide(
    procedure_id: str,
    variant_id: str,
    employee_name: str = "[Tu nombre completo]",
    document_id: str = "[Tu número de cédula]",
    email: str = "[Tu correo electrónico]",
    phone: str = "[Tu celular]",
    target_entity: str = "[Entidad o persona destinataria]",
) -> dict[str, object]:
    """Generate exact checklist, configurable contact channel, and draft message."""
    name = employee_name.strip() or "[Tu nombre completo]"
    doc = document_id.strip() or "[Tu número de cédula]"
    mail = email.strip() or "[Tu correo electrónico]"
    cel = phone.strip() or "[Tu celular]"
    entity = target_entity.strip() or "[Entidad o persona destinataria]"
    privacy_note = (
        "Por tu seguridad (Ley 1581 de 2012), no necesitas ingresar tus datos personales aquí; "
        "puedes copiar la plantilla con marcadores y completarla directamente en el canal oficial."
    )

    if procedure_id == "certificado_laboral":
        if variant_id == "operativo":
            return {
                "title": "Solicitud de Certificado Laboral · Personal operativo (PO)",
                "contact": _contact_str("certificados_operativo"),
                "privacy_note": privacy_note,
                "checklist": [
                    "Nombre completo",
                    "Número de cédula de ciudadanía",
                    "Correo electrónico",
                    "Celular",
                    "Entidad o persona a la que va dirigido (Nota: no puede ir dirigido a 'quien pueda interesar')",
                ],
                "template": (
                    f"Cordial saludo Angela,\n\n"
                    f"Solicito amablemente mi certificado laboral con los siguientes datos:\n"
                    f"- Nombre completo: {name}\n"
                    f"- Cédula de ciudadanía: {doc}\n"
                    f"- Correo electrónico: {mail}\n"
                    f"- Celular: {cel}\n"
                    f"- Dirigido a: {entity}\n\n"
                    f"Muchas gracias."
                ),
                "source": "Vinculacion_y_nomina_20260310.md → 1.1 Personal operativo",
            }
        if variant_id == "impulso":
            return {
                "title": "Solicitud de Certificado Laboral · Personal Impulso y mercado (PI)",
                "contact": _contact_str("certificados_admin_impulso"),
                "privacy_note": privacy_note,
                "checklist": [
                    "Nombre completo",
                    "Número de cédula de ciudadanía",
                    "Correo electrónico",
                    "Celular",
                ],
                "template": (
                    f"Cordial saludo Michell,\n\n"
                    f"Solicito amablemente mi certificado laboral con los siguientes datos:\n"
                    f"- Nombre completo: {name}\n"
                    f"- Cédula de ciudadanía: {doc}\n"
                    f"- Correo electrónico: {mail}\n"
                    f"- Celular: {cel}\n\n"
                    f"Muchas gracias."
                ),
                "source": "Vinculacion_y_nomina_20260310.md → 1.2 Personal Impulso y mercado",
            }
        return {
            "title": "Certificado Laboral · Personal administrativo (PA)",
            "contact": f"Prebelnet (opción Certificado laboral) · Con funciones: {_contact_str('certificados_admin_impulso')}",
            "privacy_note": privacy_note,
            "checklist": [
                "Descárgalo directamente desde Prebelnet en la opción 'certificado laboral'.",
                "Si no tienes habilitada la opción en Prebelnet, comunícate con la mesa de servicios.",
                "Si requieres certificado laboral con funciones, solicítalo a Michell Román.",
            ],
            "template": (
                f"Cordial saludo Michell,\n\n"
                f"Solicito amablemente mi certificado laboral con funciones:\n"
                f"- Nombre completo: {name}\n"
                f"- Cédula de ciudadanía: {doc}\n"
                f"- Correo electrónico: {mail}\n"
                f"- Celular: {cel}\n\n"
                f"Muchas gracias."
            ),
            "source": "Vinculacion_y_nomina_20260310.md → 1.3 Personal administrativo",
        }

    if procedure_id == "incapacidad":
        ces_email = _contact_email("cesantias_e_incapacidades_impulso")
        ces_wa = _contact_wa("cesantias_e_incapacidades_impulso")
        op_email = _contact_email("incapacidades_operativo")
        channels = {
            "administrativo": (
                "Prebelnet → botón 'Reportes de incapacidades' en la pantalla de inicio.",
                "Vinculacion_y_nomina_20260310.md → 8. Incapacidades",
            ),
            "operativo": (
                f"Correo: {op_email}",
                "Vinculacion_y_nomina_20260310.md → 8. Incapacidades",
            ),
            "impulso": (
                f"Correo: {ces_email} o WhatsApp corporativo: {ces_wa}",
                "Vinculacion_y_nomina_20260310.md → 8. Incapacidades",
            ),
        }
        contact, src = channels.get(variant_id, channels["operativo"])
        return {
            "title": "Reporte de Incapacidad Médica",
            "contact": contact,
            "privacy_note": "No envíes fotos de incapacidades ni historias clínicas por el chatbot; radícalas únicamente por el canal oficial indicado.",
            "checklist": [
                "Plazo auxilio de incapacidad: 3 días hábiles desde la expedición del certificado por parte de la EPS.",
                "Plazo general de entrega: máximo 5 días hábiles después de la ocurrencia del evento.",
                "Solo se aceptan incapacidades expedidas por ARL, EPS o IPS autorizadas por medio de transcripción.",
                "Si no se entrega dentro de los 30 días siguientes desde el inicio, la empresa se reserva el derecho de no reconocerla ni pagarla.",
            ],
            "template": (
                f"Cordial saludo,\n\n"
                f"Adjunto soporte de incapacidad médica:\n"
                f"- Nombre completo: {name}\n"
                f"- Cédula: {doc}\n"
                f"- Celular de contacto: {cel}\n\n"
                f"Quedo atento(a) a la confirmación de recibido."
            ),
            "source": src,
        }

    if procedure_id == "cesantias":
        ces_email = _contact_email("cesantias_e_incapacidades_impulso")
        ces_wa = _contact_wa("cesantias_e_incapacidades_impulso")
        ces_contact = f"Escaneado a {ces_email} y físico a nómina · Dudas: WhatsApp {ces_wa}"
        common_letter = (
            f"Señores Gestión Humana Prebel,\n\n"
            f"Yo, {name}, identificado(a) con cédula {doc} y número de contacto {cel}, "
            f"solicito el retiro de mis cesantías (indicar si son las causadas en el fondo y/o en el presente año) "
            f"por motivo de: {variant_id.replace('_', ' ')}.\n\n"
            f"Adjunto los documentos requeridos.\n\nFirma: ______________________"
        )
        cesantias_map = {
            "compra_vivienda": {
                "contact": ces_contact,
                "checklist": [
                    "Carta dirigida a Gestión Humana especificando motivo y cesantías a retirar (fondo y/o presente año), firmada y con número de contacto.",
                    "Promesa de compraventa firmada en notaría.",
                    "Certificado del inmueble o matrícula inmobiliaria (vigencia no mayor a 1 mes).",
                    f"Enviar documentación escaneada a {ces_email} y física a nómina.",
                ],
            },
            "reforma_vivienda": {
                "contact": ces_contact,
                "checklist": [
                    "Carta dirigida a Gestión Humana firmada y con número de contacto.",
                    "Impuesto predial vigente a nombre del empleado (o registro civil de matrimonio / declaración extra juicio actualizada si está a nombre del cónyuge).",
                    "Cotizaciones a nombre del empleado y foto del lugar a remodelar.",
                    "Si requiere oficial de obra: cotización, inscripción en cámara de comercio (RUT) y cuenta de cobro con firma autenticada en notaría.",
                ],
            },
            "impuesto_predial": {
                "contact": ces_contact,
                "checklist": [
                    "Carta dirigida a Gestión Humana firmada y con número de contacto.",
                    "Factura del impuesto predial a nombre del empleado (o cónyuge con registro civil de matrimonio / declaración extra juicio actualizada).",
                ],
            },
            "credito_hipotecario": {
                "contact": ces_contact,
                "checklist": [
                    "Carta dirigida a Gestión Humana firmada y con número de contacto.",
                    "Certificado donde se muestre la deuda con la entidad a nombre del empleado (o cónyuge con soporte).",
                ],
            },
            "gastos_notariales": {
                "contact": ces_contact,
                "checklist": [
                    "Carta dirigida a Gestión Humana firmada y con número de contacto.",
                    "Liquidación notarial de los gastos (aplica solo para escrituras).",
                ],
            },
            "estudio": {
                "contact": "Directamente con tu Fondo de Cesantías (Prebel no es intermediario)",
                "checklist": [
                    "Fotocopia legible del documento de identificación.",
                    "Recibo de matrícula o certificación de la institución educativa.",
                    "Si es para cónyuge: registro civil de matrimonio o declaración extra juicio actualizada.",
                    "Si es para hijos: fotocopia del registro civil de nacimiento.",
                ],
            },
        }
        info = cesantias_map.get(variant_id, cesantias_map["compra_vivienda"])
        return {
            "title": f"Retiro de Cesantías · {variant_id.replace('_', ' ').title()}",
            "contact": info["contact"],
            "privacy_note": privacy_note,
            "checklist": info["checklist"],
            "template": common_letter if variant_id != "estudio" else "Este trámite se realiza directamente en tu Fondo de Cesantías.",
            "source": "Vinculacion_y_nomina_20260310.md → 2. Requisitos retiro de cesantías",
        }

    vac_map = {
        "administrativo": (
            "Prebelnet → clic en 'solicitud de vacaciones' (al lado de tu nombre aparecen los días disponibles).",
            ["Ingresa a Prebelnet", "Haz clic en 'solicitud de vacaciones'", "Consulta tus días disponibles al lado de tu nombre"],
        ),
        "operativo": (
            "Jefes, coordinadores o líderes (el área de nómina les reporta el pasivo cada quincena).",
            ["Consulta directamente con tu jefe, coordinador o líder de área."],
        ),
        "impulso": (
            _contact_str("vacaciones_impulso"),
            ["Comunícate con Linda Salamanca por correo o celular indicando tu nombre y cédula."],
        ),
    }
    contact, checklist = vac_map.get(variant_id, vac_map["administrativo"])
    return {
        "title": "Consulta de Días de Vacaciones",
        "contact": contact,
        "privacy_note": privacy_note,
        "checklist": checklist,
        "template": f"Cordial saludo,\n\nSoy {name} (C.C. {doc}) y quisiera consultar mi saldo actual de días de vacaciones disponibles.\n\nMuchas gracias.",
        "source": "Vinculacion_y_nomina_20260310.md → 7. Dias de vacaciones",
    }
