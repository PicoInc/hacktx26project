import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Flask runs on 5001 because macOS AirPlay holds 5000
    proxy: {
      '/api': 'http://localhost:5001',
    },
  },
})
