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
      // Allow serving files from one level up to access data and config directories
      allow: ['..', '/data']
    }
  },
  // Alias both /config and /data paths
  resolve: {
    alias: {
      '/data': '/data'  // Use absolute path since it's mounted at root in container
    }
  }
})