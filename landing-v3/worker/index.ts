// Cloudflare Worker (plan gratis): sirve la landing (dist/) y entrega el token efímero de voz.
// La API key vive como secreto del Worker: `npx wrangler secret put GEMINI_API_KEY`.
import { createLiveToken } from "../api/liveToken.ts";

interface Env {
  GEMINI_API_KEY: string;
  ASSETS: { fetch: (req: Request) => Promise<Response> };
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    if (url.pathname.endsWith("/api/live-token")) {
      if (req.method !== "POST") return new Response(null, { status: 405 });
      // Solo la propia página puede pedir tokens
      const origin = req.headers.get("Origin");
      if (origin && new URL(origin).host !== url.host) return new Response("Origen no permitido", { status: 403 });
      try {
        const token = await createLiveToken(env.GEMINI_API_KEY);
        return Response.json({ token }, { headers: { "Cache-Control": "no-store" } });
      } catch (e) {
        return Response.json({ error: e instanceof Error ? e.message : "error" }, { status: 500 });
      }
    }
    return env.ASSETS.fetch(req);
  },
};
