# Prebel Empleado Digital - Chatbot de Gestión Humana
**EstudIA | Inteligencia Artificial | Capa 2 | Reto Empresarial 7: Prebel S.A.S. BIC**

Solución de autogestión de trámites, auxilios, créditos y consultas frecuentes para los colaboradores (operativos, administrativos, impulso y mercadeo) de Prebel a través de WhatsApp y Landing Page informativa.

---

## Estructura del Proyecto y Trabajo en Equipo

Este repositorio está dividido en 3 frentes de trabajo modulares para el equipo:

```text
PREBEL/
├── docs/             # [OFICIAL] Bases de conocimiento y directrices de Prebel
├── brain/            # [COMPUTADOR 1] Agente Claude, prompts y guardrails
├── server/           # [COMPUTADOR 2] API backend (FastAPI), Webhook y conexión WhatsApp
├── landing/          # [COMPUTADOR 3] Landing page web y presentación del reto
├── .gitignore        # Exclusiones de Git
└── requirements.txt  # Dependencias generales
```

### Roles y Responsabilidades
- **Computador 1 (brain/):** Agente sobre la API de Claude (Anthropic) con los documentos de `docs/` en contexto completo y caché de prompts, System Prompt, anti-alucinaciones y test suite.
- **Computador 2 (server/):** API REST / Webhook, integración con WhatsApp Cloud API / Evolution API, y Docker para el servidor on-premise de Prebel.
- **Computador 3 (landing/):** Landing page corporativa de presentación, enlace directo a WhatsApp (`wa.me`) y demo visual para directivos.

---

## Puesta en marcha (cerebro)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y pegar ANTHROPIC_API_KEY
python test_cli.py     # consola interactiva
python test_eval.py    # batería de pruebas
```
