import react from '@vitejs/plugin-react'
import { existsSync, readFileSync } from 'node:fs'
import { defineConfig, type Plugin } from 'vite'
import { createLiveToken } from './api/liveToken.ts'

/** Lee GEMINI_API_KEY del entorno o del .env de la raíz del repo (nunca llega al navegador). */
function apiKey() {
  if (process.env.GEMINI_API_KEY) return process.env.GEMINI_API_KEY
  for (const p of ['../.env', '.env']) {
    if (!existsSync(p)) continue
    const m = readFileSync(p, 'utf8').match(/^GEMINI_API_KEY=["']?([^"'\n]+)/m)
    if (m) return m[1].trim()
  }
  return ''
}

/** /api/live-token en desarrollo y en `vite preview`. En producción lo sirve worker/index.ts */
function liveTokenApi(): Plugin {
  const handler = async (req: import('node:http').IncomingMessage, res: import('node:http').ServerResponse, next: () => void) => {
    if (!req.url?.endsWith('/api/live-token')) return next()
    if (req.method !== 'POST') {
      res.statusCode = 405
      return res.end()
    }
    try {
      const key = apiKey()
      if (!key) throw new Error('Falta GEMINI_API_KEY en PREBEL/.env')
      const token = await createLiveToken(key)
      res.setHeader('Content-Type', 'application/json')
      res.setHeader('Cache-Control', 'no-store')
      res.end(JSON.stringify({ token }))
    } catch (e) {
      res.statusCode = 500
      res.end(JSON.stringify({ error: e instanceof Error ? e.message : 'error' }))
    }
  }
  return {
    name: 'sarha-live-token',
    configureServer: (s) => void s.middlewares.use(handler),
    configurePreviewServer: (s) => void s.middlewares.use(handler),
  }
}

// base './' para que la carpeta dist/ funcione servida desde cualquier ruta (Docker, Nginx, Cloudflare)
export default defineConfig({
  base: './',
  plugins: [react(), liveTokenApi()],
})
