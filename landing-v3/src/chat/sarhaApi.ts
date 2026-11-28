// Cliente del chatbot de SARHA (POST /api/chat de Sarha_Empleado_Digital_Prebel): el mismo que responde en WhatsApp.
import { SARHA_API_URL } from "../config";

export type MenuOption = { number: string; label: string };
export type ChatReply = {
  answer: string;
  sources: { title?: string; source?: string; section?: string }[];
  mode: string;
  is_out_of_scope: boolean;
  suggested_questions: string[];
  menu_options: MenuOption[];
};

/** Un session_id por pestaña del navegador: así funciona el menú numérico (1–5, 0, 00). No identifica a la persona. */
function sessionId() {
  const KEY = "sarha-session";
  let id = sessionStorage.getItem(KEY);
  if (!id) {
    id = `web-${crypto.randomUUID()}`;
    sessionStorage.setItem(KEY, id);
  }
  return id;
}

export async function askSarha(message: string, signal?: AbortSignal): Promise<ChatReply> {
  const r = await fetch(`${SARHA_API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, channel: "web", session_id: sessionId() }),
    signal,
  });
  if (!r.ok) throw new Error(`El servidor de SARHA respondió ${r.status}`);
  return (await r.json()) as ChatReply;
}
