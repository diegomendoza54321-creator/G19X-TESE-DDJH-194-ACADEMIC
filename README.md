# MotorRevisionLegal

Herramienta web de revisión de cláusulas contractuales — Proyecto de Residencias Profesionales.

---

## Descripción

MotorRevisionLegal apoya la revisión de contratos de prestación de servicios y de proveedores. Extrae el texto del documento, propone su tipo, permite que la persona usuaria confirme o corrija esa clasificación y genera un informe de hallazgos respaldado por fragmentos del contrato original.

El acceso es privado: solo pueden entrar cuentas autorizadas. No existe registro público.

**Los hallazgos son orientativos y requieren revisión humana. La herramienta no emite dictámenes jurídicos ni garantiza la validez de ningún contrato.**

---

## Funciones

### Incluidas en el alcance

- Cargar contratos en formato **PDF con texto seleccionable** o **DOCX**.
- Proponer el tipo de contrato (prestación de servicios o proveedor) con una justificación breve basada en el texto.
- Permitir que la persona usuaria **confirme o corrija la clasificación** antes de iniciar el análisis.
- Aplicar una lista de verificación base y criterios condicionales según el tipo confirmado (pendiente: criterios condicionales por tipo no implementados en este prototipo).
- Identificar posibles ambigüedades, omisiones, contradicciones aparentes y riesgos contractuales.
- Generar hallazgos respaldados por citas textuales del documento original.
- Presentar por cada hallazgo: explicación, posible consecuencia, recomendación y limitaciones del análisis.
- Mostrar el informe en pantalla. Las categorías sin hallazgos se ocultan; si no hay ninguno, se indica que no se identificaron hallazgos con los criterios aplicados.
- Consultar análisis anteriores desde la sección **Historial** (pendiente: no implementado en este prototipo).
- Interfaz con **tema claro y oscuro**; la preferencia se recuerda en el navegador.
- Navegación con: **Inicio**, **Analizar contrato**, **Resultados** e **Historial**. Las secciones *Cómo funciona* y *Criterios* pueden incluirse también.

### Limitaciones conocidas

- No inventa citas, cláusulas ni obligaciones que no estén en el documento.
- No determina la validez legal ni la ejecutabilidad de ningún contrato.
- Requiere archivos PDF con texto seleccionable. Los PDF escaneados sin capa de texto no están soportados.
- Si la extracción del texto falla o resulta incompleta, el análisis se detiene y no se generan hallazgos.
- Alcance inicial: contratos de prestación de servicios y de proveedores en español. No soporta otros tipos ni idiomas.

### Fuera del alcance inicial

- Descarga o exportación del informe.
- Compartir el informe por correo u otro medio.
- Registro público de nuevos usuarios.
- PDF escaneados (OCR).
- Comparación entre versiones de un contrato.
- Integración con sistemas ERP u otras plataformas externas.
- Generación automática de contratos o cláusulas.
- Firma electrónica.

---

## Estado del proyecto

> **Fase actual:** Prototipo funcional (backend, frontend, análisis local de IA y pruebas automatizadas).

El prototipo incluye backend (FastAPI), frontend (React/Vite), clasificación local de tipo de contrato, extracción de texto de PDF/DOCX y análisis de cláusulas contra un servidor local `llama-server` (llama.cpp) con modelo Phi-3 GGUF en `127.0.0.1:9931`. Las pruebas backend pasan con `pytest`.

Algunos elementos del alcance inicial siguen pendientes: **historial de análisis** y **criterios de verificación condicionales por tipo de contrato**. No se prometen como terminados.

---

## Tecnologías

| Componente | Tecnología | Estado |
|---|---|---|
| Backend | Python 3.14 + FastAPI | Implementado |
| Frontend | React 19 + TypeScript + Vite | Implementado |
| Estilos | CSS (tema claro/oscuro) | Implementado |
| Base de datos | SQLite | Implementado |
| Extracción de texto | pypdf, python-docx | Implementado |
| IA / LLM | llama-server (llama.cpp) con Phi-3 GGUF local | Implementado (loopback) |
| Autenticación | Sesiones SQLite, PBKDF2-SHA256 | Implementado |
| Pruebas backend | pytest, httpx, httpx2, fpdf2 | Implementado |
| Control de versiones | Git + GitHub | En uso |

### Decisiones de arquitectura

- El servidor de IA corre localmente en `127.0.0.1:9931` (loopback, sin red externa). Nunca se envía texto de contratos a servicios de terceros.
- La URL del servidor y el límite de contexto se leen de variables de entorno (`URL_SERVIDOR_IA`, `LIMITE_CONTEXTO_IA`) con valores predeterminados `http://127.0.0.1:9931` y `2048`.
- El archivo `backend/.env.example` es una plantilla; `.env` **no se carga automáticamente**. Las variables deben establecerse en el entorno antes de iniciar el backend.

---

## Requisitos previos e instalación rápida

### Requisitos previos

- **Windows** con Python 3.14 y pip.
- **Node.js** (para el frontend; versión usada en desarrollo: verificar `frontend/package.json`).

### Instalación del backend

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### Instalación del frontend

```powershell
cd frontend
npm install

---

## Arranque del servidor local de IA (llama-server)

El análisis de cláusulas requiere que `llama-server` (llama.cpp) esté en marcha escuchando en `127.0.0.1:9931` con un modelo GGUF (Phi-3 recomendado) y contexto de 2048 tokens.

Ejemplo de arranque (ajustar la ruta al modelo GGUF):

```powershell
.\llama-server.exe -m model\Phi-3-mini-4k-instruct-q4_0.gguf --host 127.0.0.1 --port 9931 -c 2048
```

Si no se dispone de `llama-server`, el backend arranca igualmente pero el endpoint de análisis responderá con error de conexión al servidor local (`modelo_no_disponible`, 503).

---

## Variables de entorno del backend

El archivo `backend/.env.example` es una plantilla:

```
URL_SERVIDOR_IA=http://127.0.0.1:9931
LIMITE_CONTEXTO_IA=2048
```

`.env` **no se carga automáticamente**. Copiar `.env.example` a `.env` y editar, o establecer las variables en PowerShell antes de iniciar el backend:

```powershell
$env:URL_SERVIDOR_IA="http://127.0.0.1:9931"
$env:LIMITE_CONTEXTO_IA="2048"
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

---

## Arranque del backend

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Queda disponible en `http://127.0.0.1:8000`. Documentación interactiva en `http://127.0.0.1:8000/docs`.

---

## Arranque del frontend

Desde la carpeta `frontend`:

```powershell
npm run dev
```

Queda disponible en `http://localhost:5173` (o el puerto que Vite asigne).

---

## Crear el primer usuario

No existe registro público. Las cuentas las crea quien opera el servidor en la máquina local ejecutando el script `crear_usuario.py`:

```powershell
.venv\Scripts\python.exe backend\crear_usuario.py revisor
```

El script solicitará la contraseña sin mostrarla en pantalla. También se puede pasar con `--contrasena` (solo recomendado para pruebas) o reestablecer con `--reestablecer`.

---

## Ejecutar las pruebas

Desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe -m pytest backend
```

---

## Estructura del proyecto

```
MotorRevisionLegal/
├── backend/           # API y lógica de análisis (Python / FastAPI)
│   ├── app/
│   │   ├── analisis_ia.py   # Cliente del servidor local de IA (llama-server)
│   │   ├── auth.py          # Sesiones SQLite, PBKDF2 (RF-00)
│   │   ├── citas.py         # Validación de citas textuales
│   │   ├── clasificacion.py # Clasificación local de tipo de contrato
│   │   ├── extraccion.py    # Extracción de texto PDF/DOCX (RF-01, RF-02)
│   │   └── main.py          # Endpoints de la API
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── crear_usuario.py     # Alta local de usuarios autorizados (RF-00.5)
│   ├── .env.example         # Plantilla de variables de entorno
│   └── tests/               # Pruebas automatizadas (pytest)
├── frontend/          # Interfaz de usuario (React / TypeScript / Vite)
├── docs/              # Documentación del proyecto
│   ├── MVP.md
│   ├── PRD.md
│   ├── requisitos.md
│   ├── arquitectura.md
│   ├── plan-de-pruebas.md
│   ├── bitacora.md
│   ├── entregables.md
│   ├── guia-instalacion.md
│   ├── manual-usuario.md
│   └── manual-tecnico.md
├── .gitignore
└── README.md
```

---

## Documentación

| Documento | Descripción |
|---|---|
| [docs/MVP.md](docs/MVP.md) | Alcance del MVP: funciones, flujo, criterios de aceptación y condiciones de término |
| [docs/PRD.md](docs/PRD.md) | Documento de requisitos del producto |
| [docs/requisitos.md](docs/requisitos.md) | Requisitos funcionales y no funcionales |
| [docs/arquitectura.md](docs/arquitectura.md) | Arquitectura propuesta del sistema |
| [docs/plan-de-pruebas.md](docs/plan-de-pruebas.md) | Plan de pruebas y casos de prueba |
| [docs/bitacora.md](docs/bitacora.md) | Bitácora de avance del proyecto |
| [docs/entregables.md](docs/entregables.md) | Lista de control de entregables de la residencia |
| [docs/guia-instalacion.md](docs/guia-instalacion.md) | Guía de instalación y arranque |
| [docs/manual-usuario.md](docs/manual-usuario.md) | Manual de usuario |
| [docs/manual-tecnico.md](docs/manual-tecnico.md) | Manual técnico |

---

## Residencias profesionales

Este proyecto se desarrolla como parte de un programa de residencias profesionales. Los entregables académicos requeridos y su estado actual se describen en [`docs/entregables.md`](docs/entregables.md).

---

*Última actualización: alineación con el prototipo funcional (backend, frontend, análisis local de IA, variables de entorno y pruebas). Pendientes: historial de análisis y criterios condicionales por tipo de contrato.*
