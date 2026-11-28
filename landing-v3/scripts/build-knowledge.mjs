// Junta los documentos oficiales de ../docs en un solo texto para la voz de SARHA.
// Correr después de cambiar un documento: `npm run knowledge`. Genera api/knowledge.generated.ts
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const docs = join(here, "..", "..", "docs");

// Las 4 bases autorizadas por Prebel + las respuestas oficiales de Prebel al reto (contactos y aclaraciones).
const FILES = [
  "Vinculacion_y_nomina_20260310.md",
  "Creditos_Prebel_20260310.md",
  "Auxilios_y_beneficios_Prebel_20260310.md",
  "Glosario_Business_Partner_20260922.md",
  "Aclaraciones_y_Contactos_Prebel_2026.md",
];

const body = FILES.map((f) => `\n\n===== DOCUMENTO: ${f} =====\n\n${readFileSync(join(docs, f), "utf8").trim()}`).join("");
const out = `// Archivo generado por scripts/build-knowledge.mjs. No editar a mano.\nexport const KNOWLEDGE = ${JSON.stringify(body)};\n`;
writeFileSync(join(here, "..", "api", "knowledge.generated.ts"), out);
console.log(`knowledge: ${FILES.length} documentos, ${body.length} caracteres`);
