import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 11888,
    host: '0.0.0.0', // This allows access from other machines
    strictPort: true, // This ensures it only uses the specified port
  },
})