# CLAUDE.md

Chatbot de Gestión Humana de Prebel S.A.S. BIC (Reto 7, EstudIA). Idioma del proyecto: español.

## Arquitectura
- `brain/`: agente sobre la API de Claude (SDK `anthropic`). Sin base vectorial: `knowledge.py` concatena los
  documentos de `docs/` (~23k tokens) y `agent.py` los envía como bloque de `system` con `cache_control`.
- `server/`: webhook de WhatsApp (pendiente). Debe llamar `responder_pregunta(pregunta, historial)` de
  `brain/agent.py` y guardar el historial por número de teléfono.
- `landing/`: landing page (pendiente).
- `docs/`: fuente oficial. Los datos deben replicarse tal cual; no editar sin aprobación de Prebel.

## Comandos
- `pip install -r requirements.txt`
- `python brain/knowledge.py`: tamaño de la base de conocimiento.
- `python test_cli.py`: consola interactiva (requiere `ANTHROPIC_API_KEY` en `.env`).
- `python test_eval.py`: batería de pruebas contra la API real (consume tokens).

## Reglas
- Variables de entorno propias con prefijo `PREBEL_` (no `CLAUDE_*`: colisiona con Claude Code).
- No poner contenido variable (fechas, IDs, datos del usuario) en los bloques de `system`: invalida la caché.
- Los textos de contingencia y el descargo de responsabilidad son obligatorios y literales
  (ver `docs/Instrucciones_Tono_Ejemplos_Restricciones.md`).
