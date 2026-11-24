# Módulo Brain (Cerebro del asistente)
Agente de Gestión Humana sobre la API de Claude (Anthropic).

- `config.py`: modelo, esfuerzo, caché y lista de documentos oficiales.
- `knowledge.py`: carga los documentos de `docs/` como un único bloque de contexto.
- `system_prompt.md`: instrucciones de alcance, tono y mensaje obligatorio.
- `agent.py`: `PrebelAgent.ask(pregunta, history)` y `responder_pregunta()` para el servidor.

No hay base vectorial: los documentos (~25k tokens) se envían completos en cada consulta
y quedan en la caché de prompts de Anthropic, por lo que releerlos cuesta ~10% del precio normal.
