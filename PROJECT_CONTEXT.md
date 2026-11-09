# PROJECT_CONTEXT.md

## Objetivo del sistema

MotorRevisionLegal es una herramienta web de revisión de cláusulas contractuales (prototipo funcional). Apoya la revisión de contratos de prestación de servicios y de proveedores: extrae texto del documento, propone su tipo, permite confirmar o corregir la clasificación y genera un informe de hallazgos respaldado por fragmentos del contrato original. El acceso es privado (sin registro público). Los hallazgos son orientativos y requieren revisión humana; no emite dictámenes jurídicos.

## Stack tecnológico

- Backend: Python 3.14, FastAPI, Uvicorn, python-multipart.
- Frontend: React 19, TypeScript, Vite (Node.js).
- Base de datos: SQLite (auth, historial).
- IA local: llama-server (llama.cpp) con modelo Phi-3 GGUF en `127.0.0.1:9931`.
- Pruebas: pytest, httpx, httpx2, fpdf2 (backend); 109 pruebas registradas.
- Control de versiones: Git + GitHub.

## Arquitectura

- API FastAPI expone endpoints para autenticación, extracción, clasificación y análisis.
- El backend llama a llama-server vía HTTP local (`/v1/chat/completions`, `/slots`, `/apply-template`, `/tokenize`).
- No se envía texto de contratos a servicios externos; solo loopback.
- Variables de entorno: `URL_SERVIDOR_IA` (default `http://127.0.0.1:9931`), `LIMITE_CONTEXTO_IA` (default `2048`). No se carga `.env` automáticamente.
- El análisis usa lock global, valida slots, cuenta tokens, genera con `max_tokens` calculado y valida JSON/citas.

## Estructura de carpetas

```
MotorRevisionLegal/
├── backend/
│   ├── app/          # analisis_ia.py, auth.py, citas.py, clasificacion.py, extraccion.py, main.py
│   ├── tests/
│   ├── requirements.txt, pytest.ini, crear_usuario.py, .env.example
├── frontend/         # React + Vite
├── docs/             # MVP, PRD, requisitos, arquitectura, bitácora, manuales, etc.
├── .venv/
├── README.md
└── PROJECT_CONTEXT.md
```

## Módulos principales

- `backend/app/main.py`: endpoints de la API y modelos de request/response.
- `backend/app/extraccion.py`: extracción de texto PDF/DOCX.
- `backend/app/clasificacion.py`: clasificación local del tipo de contrato (RF-03).
- `backend/app/analisis_ia.py`: cliente de llama-server, construcción de prompt, inferencia, parseo y validación de hallazgos.
- `backend/app/citas.py`: validación literal de citas textuales.
- `backend/app/auth.py`: sesiones SQLite, PBKDF2-SHA256.
- `backend/app/historial.py`: persistencia de análisis por usuario.
- `backend/crear_usuario.py`: alta local de usuarios autorizados.

## Flujos de negocio

1. Usuario autorizado inicia sesión (sin registro público).
2. Carga un contrato PDF con texto seleccionable o DOCX.
3. Se extrae el texto; si falla o es incompleto, el análisis se detiene.
4. Se propone el tipo de contrato (prestación de servicios o proveedor) con justificación.
5. El usuario confirma o corrige la clasificación.
6. Se ejecuta el análisis contra llama-server con criterios por tipo (criterios.json).
7. Se generan hallazgos con cita textual validada; se descartan citas no literales.
8. Se muestra el informe (categorías sin hallazgos se ocultan).
9. Historial permite consultar análisis anteriores.

## Dependencias externas

- `llama-server` (llama.cpp) + modelo GGUF Phi-3 en `127.0.0.1:9931` (contexto 2048 por defecto).
- Python 3.14, Node.js.
- Bibliotecas: fastapi, uvicorn, python-multipart, pypdf, python-docx, pytest, httpx, httpx2, fpdf2.

## Estado actual del desarrollo

- Prototipo funcional: backend, frontend, análisis local de IA y pruebas automatizadas.
- Pruebas backend: 102 registradas; `test_analisis_ia.py` con 35 pasando tras añadir `response_format` JSON Schema al POST real.
- Se verificó que llama-server acepta JSON Schema y que la respuesta pasa `json.loads` y el parser del proyecto.
- Cambio reciente: se añadió `response_format` con JSON Schema al flujo real (`backend/app/analisis_ia.py`); la prueba real con `analizar_con_ia` devolvió 0 hallazgos y 1 descartado, sin 502.

## Pendientes conocidos

- Investigar por qué el hallazgo fue descartado por `filtrar_hallazgos` (posible filtro de cita).
- Validar con más contratos sintéticos.
- Limpiar archivos temporales y artefactos (`*.db`, scripts `_diag*`, `head_bitacora.txt`).
- README tiene cambios preexistentes sin commit.
- Confirmar en endpoint real con autenticación que el flujo completo devuelva hallazgos válidos.

## Últimos cambios relevantes

- Se eliminaron entradas duplicadas (009–016) de `docs/bitacora.md`, dejando una entrada por número alineada con el índice.
- Se añadió `response_format` JSON Schema al POST real a `/v1/chat/completions` en `backend/app/analisis_ia.py`.
- Se mantuvo la validación del parser y las pruebas existentes; se añadieron pruebas para parseo y flujo de análisis.
- No se realizaron stage, commit ni push.
