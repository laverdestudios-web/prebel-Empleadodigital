# Prompt para integrar cambios sin romper nada (Antigravity IDE / cualquier agente)

> Copia todo lo que está debajo de la línea y pégalo como primer mensaje al agente de Antigravity. Es autocontenido: el agente no necesita contexto previo.

---

Eres el agente de integración del repositorio `laverdestudios-web/prebel-Empleadodigital` (Reto 7 EstudIA, Prebel S.A.S. BIC: SARHA, asistente de Gestión Humana por WhatsApp y web). Trabajo en equipo con 4 personas. Tu tarea: **integrar mis cambios locales a la rama de integración sin romper el trabajo de los demás.** Habla en español y explícame cada paso antes de hacerlo.

## 1. Estado del repositorio (léelo antes de tocar nada)

- **Rama de integración: `sarha-landing-v3`**. Ahí ya está todo junto (PR #2 hacia `main`). **No trabajes sobre `main` ni hagas push a `main`.**
- Estructura y dueño de cada parte:

| Carpeta | Qué es | Motor de IA |
|---|---|---|
| `landing-v3/` | Landing en React + Vite + GSAP: zoom al ojo (130 cuadros MAGI-2 en `public/sarha/zoom/`), voz en vivo con Gemini Live (`api/liveToken.ts`, `src/voice/`), chat escrito que usa `POST /api/chat` del backend de Sarha (`src/chat/`, `ChatPanel.tsx`), secciones de ética y privacidad | Gemini Live (token efímero; la key nunca va al navegador) |
| `landing/` | Landing v2 estática (HTML/CSS/JS) | — |
| `Sarha_Empleado_Digital_Prebel/` | Proyecto completo de WhatsApp con **Twilio**, web v2, menú numérico, autogestión, métricas y pitch (de maoescabe-png) | BM25 local + LLM opcional |
| `server/` | Webhook de WhatsApp (FastAPI) y chat de pruebas `/prueba` | `brain/chatbot_groq.py` (Gemini o Groq vía API compatible con OpenAI) |
| `brain/` | Cerebro RAG: `agent.py` + `vectorstore.py` (Gemini embeddings), `chatbot_groq.py`, `contacts_config.json`, `system_prompt.md` | Gemini |
| `docs/` | **Fuente oficial de Prebel.** No se editan sin aprobación de Prebel. Incluye las aclaraciones oficiales de 2026 | — |

- Reglas del reto (no negociables): responder **solo** con `docs/`, cero alucinaciones, mensaje oficial de «no disponible», no pedir ni guardar datos personales (Ley 1581), costo de suscripción **$0**.
- La rama `claude/lucid-hypatia-8jwfm1` (pasar el cerebro a la API de Claude, que es de pago) **NO está integrada a propósito**. No la fusiones.

## 2. Procedimiento (en este orden; para y avísame si algo falla)

1. **Guarda mi trabajo antes de nada.**
   ```bash
   git status
   git stash push -u -m "respaldo antes de integrar"   # solo si hay cambios sin commit
   ```
2. **Trae lo último y crea mi rama desde la integración:**
   ```bash
   git fetch origin
   git switch -c integra-<mi-nombre> origin/sarha-landing-v3
   git stash pop   # si hiciste stash en el paso 1
   ```
   Si mi trabajo ya estaba en commits de otra rama: `git merge <mi-rama>` estando en `integra-<mi-nombre>`.
3. **Resuelve conflictos con estas reglas:**
   - Si el conflicto está en una carpeta que **no** es mía, conserva la versión de `sarha-landing-v3` y pregúntame.
   - **Nunca borres** `brain/vectorstore.py`, `brain/ingester.py`, `brain/agent.py`, `brain/chatbot_groq.py`, `server/app.py` ni nada de `landing-v3/`: otros módulos dependen de ellos.
   - En `requirements.txt` y `.gitignore`: **une** las dos versiones, sin quitar líneas.
   - En `docs/`: si hay dos versiones de un mismo dato, gana la más reciente y oficial (`docs/Aclaraciones_y_Contactos_Prebel_2026.md` prevalece).
   - No cambies de proveedor de IA ni de modelo sin preguntarme.
4. **Prueba que nada se rompió** (todo debe pasar como antes):
   ```bash
   python -m venv venv && source venv/bin/activate          # Windows: venv\Scripts\activate
   pip install -r requirements.txt -r server/requirements.txt -r server/requirements-dev.txt
   python -m pytest -q server/tests brain/tests              # hoy: 33 pasan
   cd Sarha_Empleado_Digital_Prebel && pip install -r requirements.txt && python -m pytest -q tests && cd ..
   #   hoy: 18 pasan
   cd landing-v3 && npm install && npm run build && cd ..    # debe terminar en "built"
   ```
   Si una prueba que antes pasaba ahora falla, **no hagas push**: muéstrame el error y propón el arreglo.
5. **Revisa que no subes secretos:**
   ```bash
   git diff --cached --stat
   git diff origin/sarha-landing-v3 | grep -nE "AIza|sk-ant-|gsk_|AC[a-f0-9]{32}|AUTH_TOKEN=.+"
   ```
   No subas `.env`, llaves de Gemini, Groq ni Twilio, ni archivos de más de 10 MB. Las claves van solo en `.env` (ya está en `.gitignore`); en el repo solo va `.env.example` vacío.
6. **Commit y push de MI rama** (no de `sarha-landing-v3` directamente):
   ```bash
   git add <solo mis archivos>
   git commit -m "<qué integré, en español>"
   git push -u origin integra-<mi-nombre>
   ```
7. **Abre un Pull Request de `integra-<mi-nombre>` hacia `sarha-landing-v3`** (no hacia `main`). En la descripción pon: qué cambió, qué pruebas corriste con sus resultados, y qué quedó pendiente.

## 3. Cómo probar a mano
- Landing: `cd landing-v3 && npm run dev` → abrir en **Chrome** (la voz necesita `GEMINI_API_KEY` en `.env` de la raíz y permitir el micrófono).
- Chat de pruebas del servidor: `uvicorn server.app:app --reload` → `http://localhost:8000/prueba`.
- Proyecto Twilio: ver `Sarha_Empleado_Digital_Prebel/README` y su `.env.example`.

## 4. Al terminar, dame un resumen con
- Archivos que cambié y por qué.
- Conflictos que hubo y cómo los resolviste.
- Resultado exacto de las pruebas (antes / después).
- Link del Pull Request.
