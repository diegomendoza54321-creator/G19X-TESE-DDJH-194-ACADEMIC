# Frontend — MotorRevisionLegal

Interfaz web de la herramienta. **Bloque implementado: pantalla de carga y
extracción de texto.**

Pantalla en español para elegir un PDF con texto seleccionable o un DOCX,
enviarlo al backend y mostrar el texto extraído o el motivo del fallo.

**Sin IA y sin criterios jurídicos** en este bloque.

## Requisitos verificados

| Herramienta | Versión comprobada |
|---|---|
| Node.js | 24.22.0 |
| npm | 11.19.1 |

## Instalación

Desde la raíz del repositorio:

```powershell
cd frontend
npm.cmd install
```

## Ejecución

El backend debe estar levantado primero:

```powershell
# terminal 1, desde la raíz
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload

# terminal 2
cd frontend
npm.cmd run dev
```

Abre `http://localhost:5173`.

## Compilación de producción

```powershell
cd frontend
npm.cmd run build
```

Los archivos quedan en `frontend/dist`.

## Cómo se conecta al backend

El backend FastAPI **no tiene CORS configurado** (decisión pendiente). En
lugar de añadir middleware al backend, el dev server de Vite redirige las
rutas `/salud` y `/extraer` a `http://127.0.0.1:8000`. Ver `vite.config.ts`.

Para un despliegue de producción esto hay que resolverlo de otra forma:
servir el frontend desde el mismo origen que la API o configurar CORS en el
backend. **Pendiente de definir.**

## Comandos de npm

| Comando | Qué hace |
|---|---|
| `npm.cmd run dev` | Servidor de desarrollo con recarga en vivo |
| `npm.cmd run build` | Compila TypeScript y genera `dist/` |
| `npm.cmd run preview` | Sirve `dist/` localmente |
| `npm.cmd run typecheck` | Comprueba los tipos sin generar salida |

## Qué cubre y qué no

| Requisito | Estado |
|---|---|
| RF-01 — carga de PDF y DOCX | ✅ Implementado en esta pantalla |
| RF-02 — muestra texto extraído o avisa del fallo | ✅ Implementado en esta pantalla |
| RF-06 — interfaz y mensajes en español | ✅ Implementado |
| RF-07 — navegación e Inicio/Resultados/Historial | ⬜ Pendiente, una sola vista |
| RF-07 — tema claro y oscuro con memoria | ⬜ Pendiente, solo se respeta el tema del sistema |

El aviso de no asesoría jurídica (RPJ-05) aparece a pie de página. En el MVP
final debe ser permanente y visible también en el informe de hallazgos.

## Estructura

```
frontend/
├── package.json
├── vite.config.ts        ← proxy hacia el backend
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── index.html            ← lang="es"
└── src/
    ├── main.tsx
    ├── App.tsx           ← pantalla de carga y extracción
    ├── App.css
    └── index.css
```

## Notas

- El proyecto se generó a mano en lugar de con `npm create vite`, porque
  `create-vite` 9 lanza un prompt interactivo de linter que interrumpe los
  comandos no interactivos. No hay linter instalado; **convención de estilo
  pendiente de definir** (RNF-04.1).
- `node_modules/` y `dist/` están cubiertos por el `.gitignore` de esta
  carpeta y por el de la raíz.
