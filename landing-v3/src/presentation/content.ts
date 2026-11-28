// Contenido del pitch de SARHA. Cada dato está verificado contra el código y los documentos del repo:
//   · Ficha del Reto 7 (docs/Descripcion_Reto_ChatBot_5.pdf) y respuestas de Prebel (docs/Reto_Prebel_Respuestas_Equipos.pdf).
//   · Backend Sarha_Empleado_Digital_Prebel: menú (app/menu.py), índice BM25 (app/knowledge.py), Twilio (app/twilio_whatsapp.py),
//     métricas anónimas (app/metrics.py) y pruebas (tests/).
//   · Pruebas de server/tests y brain/tests.
// Si cambia una cifra en el código, actualízala aquí.

/** Integrantes del equipo. Las filas con nombre vacío no se muestran: hay espacio para 6. */
export const TEAM: { name: string; role: string }[] = [
  { name: "Mauricio", role: "Programador" },
  { name: "Juan", role: "Diseñador" },
  { name: "Evelio", role: "Documentador" },
  { name: "Cristian", role: "Comunicador e investigador" },
  { name: "", role: "" }, // Integrante 5: escribir nombre y rol
  { name: "", role: "" }, // Integrante 6: escribir nombre y rol
];

/** Cifras del proyecto (verificadas el 28-11-2026). */
export const FACTS = {
  collaborators: "1.300", // docs/Aclaraciones_y_Contactos_Prebel_2026.md
  docs: 5, // documentos indexados por app/knowledge.py (excluye instrucciones y política ética)
  sections: 120, // secciones que indexa hoy app/knowledge.py
  testsBot: 18, // Sarha_Empleado_Digital_Prebel/tests
  testsServer: 33, // server/tests + brain/tests
  responsibles: 10, // matriz de escalamiento (respuesta 1.1 de Prebel)
  waDisplay: "+1 (227) 240-5417",
};

export const NOTES: Record<string, string> = {
  gancho: `GANCHO (5–10 s)
Pausa, miren al público:
«¿A quién le pregunta un trabajador de Prebel, a las 6 de la mañana, cómo retirar sus cesantías?» (2 segundos de silencio)
«Hoy, a nadie con certeza.»

EQUIPO (15–20 s)
«Somos [nombres del equipo], del programa EstudIA. Tomamos el Reto 7 de Prebel S.A.S. BIC y construimos SARHA: Servicios Automatizados de Recursos Humanos Ágiles.»
Cada integrante dice su nombre y su rol: 3 segundos por persona.`,
  problema: `PROBLEMA (40–45 s)
«Este es un problema de dos lados. De un lado, los cerca de 1.300 colaboradores de Prebel —administrativos, operativos, de impulso y mercadeo y practicantes— tienen dudas todos los días sobre certificados, cesantías, vacaciones, incapacidades, créditos o auxilios, y no saben cómo gestionarlas ni a quién acudir.
Del otro lado está Gestión Humana: cada caso le corresponde a un responsable distinto según el tema y el público —son 10 personas, sin un correo único— y la herramienta de hoy, un GPT público en ChatGPT, no le da métricas: no sabe qué se pregunta ni qué queda sin respuesta.
Y ese GPT vive por fuera de WhatsApp, el canal que todos usan, y por fuera de la infraestructura de Prebel.»`,
  solucion: `SOLUCIÓN (≈20 s)
«Por eso creamos a SARHA. Le escribes “Hola” por WhatsApp y te muestra un menú de cinco opciones: Vinculación y Nómina, Créditos, Auxilios, Business Partner, y Contactos y urgencias. Si prefieres, le escribes tu duda con tus palabras, o le hablas desde la web.
SARHA responde solo con los documentos oficiales, cita la fuente y te dice a quién acudir. Si algo no está en los documentos, no inventa.»`,
  proceso: `CÓMO LLEGAMOS (≈20 s)
«Indexamos los 5 documentos oficiales de Gestión Humana en 120 secciones. Construimos un motor de búsqueda propio, que funciona sin internet y recuerda en qué parte del menú va cada celular. Lo cubrimos con 51 pruebas automáticas, todas en verde. Y lo probamos en vivo con una línea real de WhatsApp conectada por Twilio y Meta.
Queda listo para el servidor de Prebel con Docker: para actualizarlo, Gestión Humana edita sus documentos, sin tocar código.»`,
  web: `LA WEB DE SARHA (≈20 s)
«Además del WhatsApp, SARHA tiene su web. Allí puedes hablarle con la voz, escribirle en un chat que usa el mismo motor de WhatsApp, o saltar a WhatsApp con un clic. Y deja claro cómo cuida tus datos: qué hace, qué no hace, los canales de urgencia y a quién te lleva según tu tema.»`,
  funciona: `CÓMO FUNCIONA (≈25 s)
«Por dentro son tres capas. Los canales: WhatsApp, el chat de la web y la voz. El motor de SARHA, en Python: maneja el menú, busca en los documentos y responde con la fuente y el responsable. Y los datos: los documentos oficiales, montados en Docker en el servidor de Prebel.
El chat y WhatsApp se responden con búsqueda local, sin IA externa ni suscripción. La voz usa Gemini Live de Google con un token temporal: la clave nunca llega al navegador.
Y tiene controles: si la pregunta no está, da el mensaje oficial; si la respuesta es larga, la divide para WhatsApp; y no pide ni guarda datos personales.»`,
  valor: `PROPUESTA DE VALOR (20–30 s)
«¿Qué cambia con SARHA? El colaborador pregunta donde ya está: WhatsApp o la web. Recibe solo información oficial, con la fuente y el responsable. Gestión Humana, por fin, sabe qué se pregunta y qué falta en sus documentos, con un reporte anónimo. Y todo corre en el servidor de Prebel, sin costo de suscripción.»`,
  cierre: `CIERRE (10–15 s) + PASO A LA DEMO
«¿Recuerdan la pregunta del comienzo? ¿A quién le pregunta un trabajador de Prebel, a las 6 de la mañana, cómo retirar sus cesantías? Hoy esa pregunta ya tiene respuesta: a SARHA, desde su WhatsApp.»
«Se lo mostramos en vivo.» → Botón «Ver la web», luego «Habla con SARHA» y escriban: Hola → 1 → 2 → 1 (retiro de cesantías por compra de vivienda). Después pregunten «¿Cuál es el salario mínimo actual?» para mostrar que no inventa.
Invitación: «Escaneen el código y escríbanle “Hola”.»`,
};
