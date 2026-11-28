// Netlify Function: entrega el token efímero de voz (Gemini Live) en /api/live-token.
// Es el equivalente en Netlify de worker/index.ts (Cloudflare). La API key vive como variable de entorno
// de Netlify (GEMINI_API_KEY) y nunca llega al navegador.
import { createLiveToken } from "../../api/liveToken.ts";

export default async (req: Request): Promise<Response> => {
  if (req.method !== "POST") return new Response(null, { status: 405 });

  // Solo la propia página puede pedir tokens
  const origin = req.headers.get("Origin");
  if (origin && new URL(origin).host !== new URL(req.url).host) {
    return new Response("Origen no permitido", { status: 403 });
  }

  const key = process.env.GEMINI_API_KEY;
  if (!key) return Response.json({ error: "Falta GEMINI_API_KEY en las variables de entorno de Netlify" }, { status: 500 });

  try {
    const token = await createLiveToken(key);
    return Response.json({ token }, { headers: { "Cache-Control": "no-store" } });
  } catch (e) {
    return Response.json({ error: e instanceof Error ? e.message : "error" }, { status: 500 });
  }
};

export const config = { path: "/api/live-token" };
