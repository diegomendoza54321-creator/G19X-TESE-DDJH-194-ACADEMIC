import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Proxy de desarrollo: el navegador llama a rutas relativas (/salud, /extraer)
// y Vite las redirige al backend FastAPI, evitando configurar CORS.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true,
    proxy: { "/salud": "http://127.0.0.1:8000",
             "/extraer": "http://127.0.0.1:8000" } }
});

