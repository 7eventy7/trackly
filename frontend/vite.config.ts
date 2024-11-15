import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 11888,
    host: '0.0.0.0',
    fs: {
      strict: false,
      allow: ['..']
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~data': path.resolve(__dirname, '../data')
    }
  },
  // Add static file serving configuration
  publicDir: path.resolve(__dirname, '../'),
  base: '/'
})