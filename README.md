# Prebel Empleado Digital - Chatbot de Gestión Humana
**EstudIA | Inteligencia Artificial | Capa 2 | Reto Empresarial 7: Prebel S.A.S. BIC**

Solución de autogestión de trámites, auxilios, créditos y consultas frecuentes para los colaboradores (operativos, administrativos, impulso y mercadeo) de Prebel a través de WhatsApp y Landing Page informativa.

---

## Estructura del Proyecto y Trabajo en Equipo

Este repositorio está dividido en 3 frentes de trabajo modulares para el equipo:

```text
PREBEL/
├── docs/             # [OFICIAL] Bases de conocimiento y directrices de Prebel
├── brain/            # [COMPUTADOR 1] Cerebro RAG, vectorización, prompts y guardrails
├── server/           # [COMPUTADOR 2] API backend (FastAPI), Webhook y conexión WhatsApp
├── landing/          # [COMPUTADOR 3] Landing page web y presentación del reto
├── .gitignore        # Exclusiones de Git
└── requirements.txt  # Dependencias generales
```

### Roles y Responsabilidades
- **Computador 1 (brain/):** Ingesta semántica de `docs/`, base vectorial ChromaDB ($0 costo), System Prompt, anti-alucinaciones y test suite.
- **Computador 2 (server/):** API REST / Webhook, integración con WhatsApp Cloud API / Evolution API, y Docker para el servidor on-premise de Prebel.
- **Computador 3 (landing/):** Landing page corporativa de presentación, enlace directo a WhatsApp (`wa.me`) y demo visual para directivos.
