import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Flask's default port. On macOS, either turn off AirPlay Receiver (it holds 5000) or run
  // `flask run --port 5001` and set VITE_API_PROXY=http://127.0.0.1:5001 in frontend/.env.local.
  // 127.0.0.1, not localhost: Node may resolve localhost to IPv6 (::1) while Flask listens on IPv4.
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_PROXY || 'http://127.0.0.1:5000'

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': apiTarget,
      },
    },
  }
})
