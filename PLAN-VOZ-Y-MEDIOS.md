# Plan: voz de SARHA + imágenes y audios en WhatsApp

Repos revisados en GitHub el 2026-11-28 (estrellas, licencia y actividad verificadas con la API de GitHub).

## 1. Voz de SARHA para la presentación (hablar con ella en vivo)

Objetivo: en la landing, un botón «Habla con SARHA». Se le pregunta en voz alta («¿quién eres?», «¿qué haces?») y responde con su voz, en español, usando la misma base de conocimiento.

| Opción | Repo | ★ | Licencia | Qué aporta | Costo |
|---|---|---|---|---|---|
| **A (recomendada para la demo)** | [google-gemini/live-api-web-console](https://github.com/google-gemini/live-api-web-console) | 2,6k | Apache-2.0 | Plantilla React oficial de la Gemini Live API: conversación por voz en tiempo real, en español, que se puede interrumpir, con voces prediseñadas. Ya usamos Gemini, así que se le conecta el mismo `system_prompt.md` y, como herramienta (*function calling*), `responder_pregunta()` | API de Gemini (hay que revisar la cuota gratis del modelo Live) |
| B (100 % local) | [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | 17,5k | BSD-2 | Arma la cadena micrófono → transcripción → cerebro → voz, con detección de turnos. Cada pieza es intercambiable | $0 en el servidor, pero hay más trabajo y más latencia |
| B alterna | [livekit/agents](https://github.com/livekit/agents) | 15,4k | Apache-2.0 | Lo mismo que Pipecat, con un servidor WebRTC propio | $0 autoalojado |

Voz local (para la opción B, o para que SARHA lea las respuestas en la web):

| Repo | ★ | Licencia | Español | Nota |
|---|---|---|---|---|
| [hexgrad/kokoro](https://github.com/hexgrad/kokoro) (Kokoro-82M) | 10,4k | Apache-2.0 | Sí (`lang_code='e'`, voz femenina `ef_dora`) | Liviano, corre en CPU |
| [resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox) | 28,2k | MIT | Sí (Multilingual V3) | La más natural; puede clonar una voz a partir de unos segundos de audio. Mejor con GPU |
| [OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl) | 6,4k | **GPL-3.0** | Sí (es_MX, es_CO) | Muy rápido en CPU. Ojo con la GPL si Prebel redistribuye el código. El `rhasspy/piper` original está archivado |

Descartados: `coqui-ai-TTS` (XTTS tiene licencia no comercial) y LivePortrait (animar la foto: su licencia es mixta y depende de InsightFace, que no es comercial). Para que SARHA «hable» visualmente: un anillo alrededor de su foto que reacciona al volumen de la voz, hecho por código, sin video.

## 2. WhatsApp (Twilio): entender imágenes y audios

Twilio ya entrega todo en el webhook: `NumMedia`, `MediaUrl0`, `MediaContentType0` (`audio/ogg` en notas de voz, `image/jpeg` en fotos). El archivo se descarga con autenticación básica (Account SID + Auth Token).

| Necesidad | Solución | Repo | ★ | Licencia |
|---|---|---|---|---|
| **Escuchar notas de voz** | Transcribir el `.ogg` y pasar el texto a `responder_pregunta()` | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) (modelo `large-v3-turbo` o `small` según la CPU) | 27,1k | MIT |
| Servidor de voz listo en Docker | Un solo contenedor con transcripción (faster-whisper) y voz (Kokoro y Piper), compatible con la API de OpenAI | [speaches-ai/speaches](https://github.com/speaches-ai/speaches) | 3,8k | MIT |
| Alternativa sin Python | Whisper en C++, muy liviano | [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp) | 55,6k | MIT |
| **Entender imágenes** | Gemini ya es multimodal: se le manda la foto (por ejemplo, de una incapacidad o un formulario) con la pregunta. No hace falta otro repo | (el `brain/` actual) | — | — |
| Enviar audios (opcional) | Generar el audio con Kokoro (vía speaches), convertirlo a `.ogg` u `.mp3` y responder con `MediaUrl` en el TwiML. El archivo tiene que estar en una URL pública | speaches / kokoro | — | — |

### Flujo propuesto en `server/`
```
Twilio webhook → ¿NumMedia > 0?
  ├─ audio/*  → descargar → faster-whisper (es) → texto → responder_pregunta()
  ├─ image/*  → descargar → Gemini (imagen + "¿qué necesita el colaborador?") → responder_pregunta()
  └─ texto    → responder_pregunta()
```

### Advertencias
- **Datos personales:** una foto de incapacidad o una nota de voz tienen datos de salud. La transcripción local (faster-whisper) no saca el audio del servidor. Las imágenes que se mandan a Gemini sí salen hacia Google: hay que decírselo a Prebel.
- **Recurso del servidor:** faster-whisper `small` corre bien en CPU. `large-v3` necesita GPU o es lento. Hay que preguntarle a Alexander qué servidor va a dar Prebel.
