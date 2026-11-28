# Landing SARHA · Prebel

Landing de SARHA, el asistente virtual de Recursos Humanos de Prebel. Es HTML, CSS y JavaScript sin librerías: se abre `index.html` y funciona, incluso sin internet. Se adapta a computador, tablet y celular.

## Cómo abrirla

- Doble clic en `index.html`, o
- desde esta carpeta: `python3 -m http.server 8080` y abrir http://localhost:8080

## Archivos

| Archivo | Qué tiene | Cuándo tocarlo |
|---|---|---|
| `index.html` | Todo el texto y la estructura de la página | Cambiar textos, servicios, preguntas frecuentes |
| `css/estilos.css` | Colores, letras, tarjetas, botones, panel de chat y las versiones para celular | Cambiar el aspecto |
| `js/landing.js` | Abrir y cerrar el panel de chat, botones de tema y el año del pie | Para conectar el chatbot o WhatsApp |
| `img/logo-prebel.png` | Logo de Prebel (300×63). Se usa arriba y en el pie; en el pie el CSS lo vuelve blanco | |
| `img/sarha-avatar-grande.jpg` | Avatar de SARHA (540×540) para la esfera del inicio | |
| `img/sarha-avatar-mini.jpg` | Avatar pequeño (220×220) para el botón flotante y el panel de chat | |

## Secciones de la página (en orden, dentro de `index.html`)

| Sección | `id` | Contenido |
|---|---|---|
| Barra superior | (`header.topbar`) | Logo Prebel + SARHA, menú y botón «Habla con SARHA». Se queda fija al bajar |
| Inicio | `#inicio` | «Hola, soy SARHA», botones y la esfera con el avatar y 2 tarjetas flotantes |
| Servicios | `#servicios` | 8 tarjetas de áreas de consulta (`.service-card`) |
| Cómo funciona | `#como-funciona` | 3 pasos (`.step`) |
| Preguntas frecuentes | `#preguntas` | 5 preguntas desplegables (`<details>`) |
| Llamado final | `#habla-con-sarha` | Banner con degradado y botón |
| Franja + pie | (`.brand-stripe`, `footer`) | 5 colores de Prebel, logo, lema y © con el año automático |
| Chat flotante | `#chatLaunch`, `#chatPanel` | Botón con avatar y panel con 5 temas. **Por ahora es solo una maqueta: no está conectado al chatbot** |

## Paleta (en `:root` de `css/estilos.css`)

Institucionales de Prebel: `--slate #575F6A`, `--blue #5A84AC`, `--green #6EA190`, `--cyan #85BFD3`, `--teal #56736F`, `--coral #E39581`. Si se cambia un color ahí, cambia en toda la página.

Letras: Georgia para títulos e Inter (o la del sistema) para el texto.

## Cómo funciona el chat (`js/landing.js`)

- `setChat(true|false)` abre o cierra el panel.
- Todo botón con el atributo `data-open-chat` abre el panel. Hay 3: el del inicio, el de preguntas frecuentes y el del banner final.
- Los botones `data-topic="..."` del panel solo cambian el texto. **Ahí se conecta el chatbot.** Lo más simple es abrir WhatsApp con el tema ya escrito:

```js
window.open('https://wa.me/57XXXXXXXXXX?text=' + encodeURIComponent('Hola SARHA, necesito info de ' + button.dataset.topic));
```

## Cómo agregar algo

- **Un servicio:** copiar una línea `<article class="service-card">…</article>` dentro de `.cards`.
- **Una pregunta frecuente:** copiar un bloque `<details><summary>Pregunta</summary><p>Respuesta</p></details>` dentro de `.faq-list`.
- **Un tema en el chat:** agregar `<button data-topic="Tema">Tema</button>` dentro de `.chat-actions`.

## Para trabajar en equipo

- Hacer `git pull` antes de editar. Si dos personas cambian la misma parte al mismo tiempo, Git marca un conflicto.
- Commits pequeños, uno por cambio (por ejemplo: «Landing: agrega pregunta de cesantías»).

## Origen

Se reconstruyó desde `landing_sarha_prebel_v2 segunda fase.html` (un solo archivo de 130 KB con las imágenes incrustadas en base64). El CSS, el JS y las imágenes se separaron sin cambiar nada, así que se ve exactamente igual.

Análisis con Craft Anything 0.6.1 (`js-app-map`, modo profundo): página estática, 1 función (`setChat`), 5 tipos de evento de clic, 0 llamadas a servidores, sin cookies ni almacenamiento.
