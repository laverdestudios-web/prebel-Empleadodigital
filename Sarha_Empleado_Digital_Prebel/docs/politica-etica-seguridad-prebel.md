# 🛡️ Marco de Ética, Responsabilidad, Privacidad y Manejo de Datos
**Proyecto:** Gestión Humana Más Cerca de Ti *(Asistente Virtual / Voz: Sara)*  
**Organización:** Prebel S.A.S. BIC — Reto Empresarial 7 (EstudIA)  
**Cobertura:** Colaboradores directos de Prebel (~1,300 empleados: `PA`, `PO`, `PI`, `PP`)  
**Normativa de referencia:** Ley Estatutaria 1581 de 2012 (Habeas Data Colombia), Decreto 1377 de 2013 y directrices oficiales de Prebel S.A.S. BIC.

---

## 1. Hallazgos Críticos del Nuevo Documento de Prebel (Impacto Directo en el Proyecto)

Al cruzar las respuestas oficiales del equipo de Prebel (*Preguntas de los equipos · Bloque 18, piso 2*) con la arquitectura que venimos construyendo, hay **5 ajustes obligatorios** para evitar rechazos de TI, Legal o Gestión Humana durante la presentación:

> [!WARNING]
> **1. Restricción crítica sobre Imágenes y Documentos en WhatsApp (Sección 2.4 y 5.1):**  
> Prebel excluyó expresamente la **"Recepción de historias clínicas, incapacidades y documentos personales"** y exige que el colaborador **no comparta datos personales en el chat** (cédula, salarios, desprendibles).  
> * **Acción técnica:** Si habilitas reconocimiento de audio e imágenes en Twilio, el bot **NO debe recibir ni procesar fotos de incapacidades, fórmulas médicas o cédulas**. El audio debe usarse exclusivamente para accesibilidad (transcribir la pregunta hablada del operario y responderle en texto), y ante cualquier foto/documento sensible el bot debe bloquear su procesamiento, borrar el archivo temporal de inmediato y responder con el aviso de seguridad indicando el canal autorizado.

> [!IMPORTANT]
> **2. Actualización de Contactos Oficiales (Secciones 1.1, 3.3, 3.9 y 3.10):**  
> Hay cambios importantes frente a los Markdown iniciales:
> * **Cesantías e Incapacidades de Impulso y Mercadeo:** Ahora la responsable es **Johanna Puentes** (`johanna.puentes@prebel.com.co` | WhatsApp corporativo: `3104589490`), reemplazando a Lucía Mejía.
> * **Nómina de Impulso y Mercadeo y Practicantes:** Figura **Cristina Giraldo** (`cristina.giraldo@prebel.com.co`).
> * **Configuración desacoplada:** Prebel recomienda almacenar esta matriz de contactos, horarios y valores de auxilios en un **archivo de configuración parametrizable** (ej. JSON/YAML), sin quemar correos directamente en el código.

3. **Identidad y Nombre del Bot (Sección 1.6):** El nombre oficial aprobado por Prebel es **"Gestión Humana Más Cerca de Ti"**. En la presentación pueden presentar a *"Sara"* como la interfaz de voz de *"Gestión Humana Más Cerca de Ti"* para respetar la marca interna.
4. **Cero almacenamiento de chats en fase inicial (Sección 5.3):** No está autorizado guardar historiales de conversación ligados a usuarios en esta etapa. Toda métrica debe ser agregada y **anonimizada** (Sección 4.5).
5. **Disclaimer sin atarse a un único proveedor (Sección 5.5):** El aviso obligatorio debe decir que funciona con inteligencia artificial sin amarrarlo a "ChatGPT", dejando la selección final del proveedor APIficado a revisión conjunta con TI y Legal de Prebel (Sección 5.4).

---

## 2. Principios Éticos de Inteligencia Artificial Responsable

1. **Transparencia y No Suplantación Humana:**  
   El colaborador siempre sabrá desde el primer mensaje que interactúa con un sistema automatizado de Inteligencia Artificial de apoyo informativo, nunca con un analista humano.
2. **Cero Alucinación y Fidelidad Documental (Criterio #1 de Evaluación):**  
   El asistente solo responde con base en los 4 documentos oficiales autorizados y actualizados por Prebel. Tiene estrictamente prohibido usar internet, conocimiento general externo, suposiciones o deducciones. Si el dato no existe en el corpus, responde con el mensaje oficial de contingencia.
3. **Principio de No Sustitución (Human-in-the-Loop):**  
   El bot orienta sobre procedimientos, requisitos y responsables, pero **jamás toma decisiones laborales, administrativas, médicas o disciplinarias**, ni ejecuta trámites transaccionales.
4. **Equidad, Accesibilidad e Inclusión:**  
   Diseñado para atender sin barreras tanto al personal administrativo (`PA`) como al operativo (`PO`), de impulso y mercadeo (`PI`) y practicantes (`PP`). El soporte de notas de voz en WhatsApp e interfaz oral en la presentación busca democratizar el acceso para colaboradores operativos en planta o en campo.
5. **Distinción entre Empleados Directos y Temporales:**  
   El asistente debe aclarar oportunamente cuando aplique que los beneficios extralegales y auxilios documentados aplican exclusivamente a colaboradores con **vinculación directa con Prebel S.A.S. BIC**, evitando generar falsas expectativas en personal temporal o externo (Sección 2.2).

---

## 3. Política de Privacidad, Protección de Datos (Ley 1581 de 2012) y Seguridad TI

### 3.1. Marco Legal Colombiano Aplicable
En cumplimiento de la **Ley Estatutaria 1581 de 2012** y el **Decreto 1377 de 2013** (Régimen General de Protección de Datos Personales en Colombia):
* **Autorización Previa y Finalidad (Sección 5.2):** Los colaboradores directos de Prebel ya cuentan con autorización de tratamiento de datos firmada con la compañía. El uso del chatbot se circunscribe estrictamente a la finalidad informativa de autogestión de Gestión Humana.
* **Minimización de Datos (*Privacy by Design*):** El chatbot está diseñado para **NO solicitar, recolectar ni almacenar Datos Personales Identificables (PII) ni Datos Sensibles** (número de cédula, salario, historias clínicas, diagnósticos médicos o estados de cuenta individuales).

### 3.2. Política de Procesamiento Efímero (No Retención)
* **Conversaciones (Sección 5.3):** Durante el prototipo y fase inicial, el sistema opera en **modo sin estado persistente de historial por usuario**. El contexto de público (`PA`, `PO`, `PI`, `PP`) se mantiene únicamente en memoria volátil (RAM) durante la sesión activa y se descarta al finalizar.
* **Audios (Notas de voz en Twilio):** Si el usuario envía un audio, se descarga en memoria o archivo temporal cifrado, se transcribe localmente (ej. con `faster-whisper`) para extraer la consulta en texto y el archivo de audio se **elimina inmediatamente (`unlink`)** tras procesar la pregunta. No se almacenan grabaciones de voz biométricas ni notas de voz en disco.
* **Imágenes (Multimedia en Twilio):** El bot no solicita ni almacena imágenes de documentos personales (incapacidades, cédulas, fórmulas). Si un usuario envía una imagen, se le responde con la advertencia de privacidad y la ruta oficial autorizada sin guardar el archivo en servidores propios.

### 3.3. Autenticación y Seguridad de Canal (Sección 2.3)
* **El número de teléfono celular NO es mecanismo de autenticación suficiente** para consultar o entregar información individual de nómina, saldos de cesantías o créditos.
* Por este motivo, el chatbot **nunca consulta ni expone información privada individual** y toda solicitud personal se redirige a los canales corporativos verificados (correo corporativo, Prebelnet o contacto directo con el responsable de GH).

### 3.4. Reportes y Analítica Anonimizada (Sección 4.5)
Para el piloto se generará un **reporte mensual 100% anonimizado y agregado** (sin números de teléfono, nombres, ni texto literal que contenga datos personales), registrando únicamente:
* Cantidad total de consultas recibidas.
* Porcentaje de consultas resueltas vs. no resueltas.
* Temáticas más consultadas (por categoría).
* Preguntas frecuentes sin cobertura documental (para actualizar la base RAG).
* Casos escalados agrupados por público (`PA`/`PO`/`PI`/`PP`) y área responsable.
* Inconsistencias detectadas en la documentación vigente.

### 3.5. Gobernanza de Modelos IA y Despliegue (Sección 5.4 y 6.5)
* **Arquitectura RAG Actualizable:** Las actualizaciones normativas o de montos se cargan modificando la base de conocimiento vectorial sin necesidad de reentrenar modelos de lenguaje (Sección 6.3).
* **Seguridad de API y Privacidad Empresarial:** Para el paso a producción, Prebel (TI y Legal) definirá el proveedor APIficado o infraestructura aprobada (nube corporativa de Prebel o servidor *on-premise*), garantizando contractualmente políticas de **Zero Data Retention** (los textos enviados a inferencia no se utilizan para entrenar modelos públicos de terceros). En escenarios de restricción total de salida a internet, la arquitectura permite sustituir tanto los embeddings/TTS como el LLM por modelos locales contenerizados en Docker (*on-premise*).

---

## 4. Alcance Operativo, Matriz de Escalamiento y Urgencias

### 4.1. Temas Permitidos vs. Temas Definitivamente Excluidos

| ✅ Permitido (Alcance Documentado) | 🚫 Definitivamente Excluido (Secciones 1.5, 2.4, 2.5, 3.8) |
| :--- | :--- |
| Orientación sobre auxilios, beneficios y montos 2026 | Consulta de salarios, desprendibles de nómina o datos personales |
| Requisitos y condiciones de créditos (educación, salud, mascotas, vivienda) | Consulta de saldos individuales (vacaciones, cesantías, créditos) |
| Procedimientos de vinculación, certificados, EPS, pensiones, caja | Recepción de historias clínicas, incapacidades o documentos personales |
| Paso a paso de retiro de cesantías por causal | Aprobación de créditos, auxilios, permisos o vacaciones |
| Conceptos del Glosario Business Partner, licencias y ausentismo | Decisiones disciplinarias o conceptos jurídicos personalizados |
| Enrutamiento al responsable de GH según público (`PA`/`PO`/`PI`/`PP`) y sede | Diagnósticos médicos o psicológicos / Convivencia laboral y acoso |
| Canales de emergencia médica, accidentes y salud mental | Entrega de formularios de crédito, Reglamento Interno, dotación, fondo de empleados |

### 4.2. Reglas de Horario y Protocolo de Urgencias (Secciones 1.2, 1.4 y 4.6)
* **Disponibilidad 24/7 informativa:** El bot responde consultas documentales las 24 horas, los 7 días de la semana.
* **Fuera de horario laboral y festivos:** Cuando un trámite requiera atención humana, el bot informará que la gestión será atendida dentro del horario hábil de Gestión Humana, **sin prometer respuesta inmediata**.
* **Protocolo de Urgencias (Sin restricción de horario):** Ante emergencias médicas, accidentes laborales o crisis psicológicas, el bot entrega de inmediato los canales oficiales:

| Situación Crítica | Canal Oficial Inmediato |
| :--- | :--- |
| **Emergencia médica en sede (Productora, Comercial, Rionegro)** | Servicio **EMI**, gestionado a través de un **brigadista** de la sede. |
| **Accidente o incidente de trabajo** | Reportar de inmediato a la **Business Partner**, personal de **SST** y al **jefe directo** (para reporte a ARL). |
| **Acompañamiento psicológico urgente** | **Red de Amor**: línea `604 3607080` (opción 3) — extensivo a grupo familiar. |
| **Programa Desahogadero (Bienestar)** | Bienestar y RSE: `3104057760`. |

### 4.3. Matriz Maestra de Escalamiento Configurable (Actualizada)

*(Debe almacenarse en archivo de configuración externo, ej. `config/contacts.json`, no quemada en código).*

| Responsable | Proceso / Temática / Público | Correo Oficial | Teléfono / WhatsApp |
| :--- | :--- | :--- | :--- |
| **Angela Quintero** | Vinculación, certificados y seguridad social — **Personal Operativo (`PO`)** | `angela.quintero@prebel.com.co` | `3234830720` |
| **Michell Román** | Vinculación, certificados y seguridad social — **Administrativo (`PA`) e Impulso/Mercadeo (`PI`)** | `michell.roman@prebel.com.co` | `3147710112` |
| **Shirley Silgado** | Nómina **Administrativa (`PA`)** | `shirley.silgado@prebel.com.co` | No documentado |
| **Yasmín Yepes** | Nómina **Operativa (`PO`)** | `yasmin.yepes@prebel.com.co` | No documentado |
| **Johanna Puentes** | **Cesantías** e incapacidades **Impulso y Mercadeo (`PI`)** | `johanna.puentes@prebel.com.co` | WhatsApp corp.: `3104589490` |
| **Cristina Giraldo** | Nómina **Impulso y Mercadeo (`PI`) y Practicantes (`PP`)** | `cristina.giraldo@prebel.com.co` | No documentado |
| **Stefanny Pulgarín** | **Bienestar, RSE, créditos, auxilios, beneficios y registro de mascotas** | `stefanny.pulgarin@prebel.com.co` | `3104057760` |
| **Linda Salamanca** | Consulta de vacaciones — **Impulso y Mercadeo (`PI`)** | `linda.salamanca@prebel.com.co` | `3102150234` |
| **Nathalia León** | **Business Partner** — Sede Productora y Sede Rionegro | — | — |
| **Laura Jaramillo** | **Business Partner** — Sede Comercial y fuera de sede | `laura.jaramillo@prebel.com.co` | — |

---

## 5. Textos Legales y Avisos Listos para Implementar

### A. Saludo Inicial + Aviso de Transparencia y Privacidad (WhatsApp)
```text
¡Hola! 👋 Soy el asistente virtual de Gestión Humana Más Cerca de Ti de Prebel S.A.S. BIC.

Estoy aquí 24/7 para orientarte con información oficial sobre:
1️⃣ Vinculación y Nómina
2️⃣ Créditos y Condiciones
3️⃣ Auxilios y Beneficios

🔒 Aviso de privacidad: Esta herramienta funciona con Inteligencia Artificial con fines estrictamente informativos (Ley 1581 de 2012). Por tu seguridad, no compartas en este chat tu número de cédula, desprendibles, salarios ni historias clínicas.

¿En qué trámite o beneficio puedo ayudarte hoy?
```

### B. Aviso Automático ante Envío de Documentos, Fotos Sensibles o Solicitud de Datos Privados
```text
🔒 Por tu seguridad y en cumplimiento de las políticas de protección de datos de Prebel, este asistente no recibe documentos personales, historias clínicas, incapacidades ni consulta saldos o salarios individuales.

Para radicar tu documento o recibir atención personalizada, comunícate directamente con el canal autorizado de Gestión Humana correspondiente a tu nómina. Si me indicas tu público (Administrativo PA, Operativo PO, Impulso y Mercadeo PI o Practicante PP), con gusto te doy el contacto y correo exacto.
```

### C. Disclaimer Obligatorio Actualizado al Final de Cada Respuesta (Sección 5.5)
```text
---
ℹ️ Este asistente de Gestión Humana Más Cerca de Ti funciona con inteligencia artificial y puede cometer errores. Su contenido es meramente orientativo con base en los documentos autorizados por Prebel. Te recomendamos validar la información o resolver dudas específicas con Stefanny Pulgarín (Bienestar y RSE) o Michell Román (Asistente de Gestión Humana).
```

### D. Nota Legal para la Landing Page de Presentación (Voz / Sara)
> *"Prototipo académico y empresarial desarrollado en el marco del programa EstudIA (Reto 7 — Prebel S.A.S. BIC). Las respuestas generadas utilizan arquitectura RAG sobre documentación interna no sensible autorizada. El sistema no almacena conversaciones personales, no solicita datos sensibles (Ley 1581 de 2012) y la arquitectura está preparada para despliegue en infraestructura privada/APIficada aprobada por TI y Legal de Prebel."*

---

## 6. Escudo de Respuestas para Preguntas de TI, Legal y Directivos en la Presentación

| Pregunta probable de Prebel | Respuesta recomendada (Basada en este marco) |
| :--- | :--- |
| **"¿Qué pasa si un operario manda una foto de su incapacidad o su cédula por WhatsApp?"** | *"Aplicamos un filtro estricto de privacidad: el bot no almacena documentos personales ni historias clínicas, descarta el archivo temporal de forma inmediata y le responde al colaborador con el correo y WhatsApp oficial exacto (`incapacidades@prebel.com.co`, Prebelnet o Johanna Puentes según su nómina) para que radique de forma segura."* |
| **"¿Dónde quedan guardados los chats de los empleados?"** | *"Cumpliendo la directriz de la fase inicial, las conversaciones no se almacenan en bases de datos ligadas a personas. Solo registramos métricas estadísticas anonimizadas (temas consultados y preguntas sin cobertura) para mejorar la documentación de GH."* |
| **"¿La IA puede inventar montos de auxilios o prometer un crédito?"** | *"No. El modelo opera con temperatura casi cero (0.1), arquitectura RAG anclada exclusivamente a los 4 documentos aprobados y bloqueo estricto de alucinaciones. Ante cualquier pregunta fuera del alcance (salarios, acoso, saldos individuales), responde con la frase oficial de contingencia y nunca aprueba trámites."* |
| **"¿Pueden entrenarse modelos públicos con la información interna de Prebel?"** | *"No. La base documental es información interna no sensible y vive en una base vectorial local bajo control de Prebel. Para producción, la conexión se realiza mediante API corporativa con cláusula de no retención/no entrenamiento, o 100% on-premise con modelos locales en Docker sobre el servidor de Prebel."* |
| **"¿Cómo cumplen con la Ley 1581 de 2012 (Habeas Data)?"** | *"Por tres vías: (1) Los colaboradores ya autorizaron el tratamiento de datos con Prebel; (2) Aplicamos minimización total de datos (el bot no pide cédula ni PII y prohíbe usar el número celular como autenticación); (3) Mostramos aviso transparente de uso de IA y privacidad desde el primer contacto."* |
