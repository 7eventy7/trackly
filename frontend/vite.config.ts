import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 11888,
    host: '0.0.0.0', // This allows access from other machines
    strictPort: true, // This ensures it only uses the specified port
    fs: {
      // Allow serving files from one level up, where the config folder is
      allow: ['..']
    }
  },
  // Alias /config to point to the config directory in development
  resolve: {
    alias: {
      '/config': path.resolve(__dirname, '../config')
    }
  }
})