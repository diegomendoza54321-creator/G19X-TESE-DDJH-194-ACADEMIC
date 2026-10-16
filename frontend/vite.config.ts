import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Proxy de desarrollo: reenvía las rutas de API al backend FastAPI,
// evitando configurar CORS.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true,
    proxy: {
      "/salud": "http://127.0.0.1:8000",
      "/yo": "http://127.0.0.1:8000",
      "/login": "http://127.0.0.1:8000",
      "/logout": "http://127.0.0.1:8000",
      "/extraer": "http://127.0.0.1:8000",
      "/clasificar": "http://127.0.0.1:8000"
    } }
});

