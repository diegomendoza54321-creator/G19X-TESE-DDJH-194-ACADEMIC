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
- Aplicar una lista de verificación base y criterios condicionales según el tipo confirmado (la lista base está implementada y se integra al prompt).
- Identificar posibles ambigüedades, omisiones, contradicciones aparentes y riesgos contractuales.
- Generar hallazgos respaldados por citas textuales del documento original.
- Presentar por cada hallazgo: explicación, posible consecuencia, recomendación y limitaciones del análisis.
- Mostrar el informe en pantalla. Las categorías sin hallazgos se ocultan; si no hay ninguno, se indica que no se identificaron hallazgos con los criterios aplicados.
- Consultar análisis anteriores desde la sección **Historial** (disponible en el prototipo).
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

### Desarrollo con asistencia de IA
Desarrollado con asistencia de IA durante el proceso de desarrollo.

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

## 1. Requisitos previos y ruta de trabajo

Se necesita Windows con:

- **Python 3.14** (incluye `pip`). Durante la instalación, marcar "Add Python to PATH".
- **Node.js** (solo para el frontend; versión indicada en `frontend/package.json`).
- **llama.cpp** con el ejecutable `llama-server` y un modelo GGUF (recomendado: Phi-3 mini 4K instruct, cuantificado q4_0).

Todos los comandos de este documento se ejecutan desde la **raíz del repositorio** (donde está este `README.md`), en PowerShell, a menos que se indique lo contrario.

Estructura esperada:

```
MotorRevisionLegal/
├── backend/
│   ├── app/
│   │   ├── analisis_ia.py
│   │   ├── auth.py
│   │   ├── citas.py
│   │   ├── clasificacion.py
│   │   ├── extraccion.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── crear_usuario.py
│   ├── .env.example
│   └── tests/
├── frontend/
│   └── package.json
├── docs/
├── .gitignore
└── README.md
```

---

## 2. Crear el entorno virtual e instalar dependencias del backend

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Esto instala las dependencias listadas en `backend/requirements.txt`:
- `fastapi`, `uvicorn[standard]`, `python-multipart` (API)
- `pypdf`, `python-docx` (extracción de texto)
- `pytest`, `httpx`, `httpx2`, `fpdf2` (pruebas)

---

## 3. Preparar llama.cpp y el modelo GGUF

El análisis de cláusulas depende de **llama-server** (de llama.cpp) ejecutándose en `127.0.0.1:9931`.

### Archivos necesarios

- Ejecutable `llama-server` de llama.cpp.
- **Dato del entorno comprobado (no es requisito general):** en la máquina de desarrollo se verificó la presencia de `D:\llama.cpp\llama-server.exe` con la versión `0.7.0-dev (build 11683, commit a8d9a7e1e)`, compilado con Clang 20.1.8 para Windows x86_64. El proyecto no exige esta versión ni build concretos; cualquier binario compatible de llama.cpp que responda en `127.0.0.1:9931` es válido.
- Modelo GGUF. El proyecto recomienda **Phi-3 mini 4K instruct, cuantificado q4_0** (por ejemplo: `model\Phi-3-mini-4k-instruct-q4_0.gguf`) como referencia. El repositorio **no incluye** ni especifica una URL de descarga ni una versión concreta de llama.cpp ni del modelo; el usuario debe proporcionar ambos archivos y ajustar la ruta `-m` al modelo que tenga disponible.

### Arrancar llama-server

Desde la carpeta que contenga `llama-server.exe` y el modelo:

```powershell
.\llama-server.exe -m 'C:\Modelos\modelo.gguf' --host 127.0.0.1 --port 9931 -c 2048
```

Parámetros clave:

- `-m`: ruta al archivo `.gguf` del modelo (requerido, sin valor predeterminado en el repositorio). Sustituya `'C:\Modelos\modelo.gguf'` por la ruta real de su archivo GGUF.
- `--host 127.0.0.1`: escucha solo en loopback (sin red externa).
- `--port 9931`: puerto que el backend espera por defecto.
- `-c 2048`: contexto de 2048 tokens.


### Comprobar que llama-server responde

Una vez arrancado, en otra terminal de PowerShell:

```powershell
curl.exe -sS http://127.0.0.1:9931/v1/models | Select-Object -First 1
```

o, alternativamente:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:9931/v1/models
```

Debe devolver una lista de modelos cargados por el servidor. Si no responde, el backend no puede conectar y el endpoint de análisis devolverá `modelo_no_disponible` (HTTP 503).
Si no se dispone de `llama-server`, el backend arranca igualmente, pero el endpoint de análisis responderá con error de conexión (`modelo_no_disponible`, HTTP 503) hasta que `llama-server` esté en marcha.

---

## 4. Configurar variables de entorno (`URL_SERVIDOR_IA` y `LIMITE_CONTEXTO_IA`)

Las variables de entorno se pueden establecer directamente en PowerShell antes de iniciar el backend. No es necesario copiar `backend/.env.example` a `.env`, ya que el proyecto no carga `.env` automáticamente. Ejecuta cualquiera de las siguientes opciones en una terminal PowerShell:

```powershell
# Opción 1: Establecer una sola variable
$env:URL_SERVIDOR_IA = "http://127.0.0.1:9931"

# Opción 2: Establecer ambas variables
$env:URL_SERVIDOR_IA = "http://127.0.0.1:9931"
$env:LIMITE_CONTEXTO_IA = "2048"
```

Al iniciar el backend, las variables estarán disponibles. Ejemplo:

```powershell
# Desde la raíz del repositorio
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

El archivo `backend/.env.example` sirve solo como referencia de nombres de variables; su contenido no se lee de forma automática.

El archivo `backend/.env.example` es una **plantilla de referencia**:

```
URL_SERVIDOR_IA=http://127.0.0.1:9931
LIMITE_CONTEXTO_IA=2048
```

**`.env` no se carga automáticamente.** El backend lee las variables directamente del entorno del sistema operativo mediante `os.environ.get`.

Opción A: crear archivo `.env`:

```powershell
copy backend\.env.example backend\.env
# Editar backend\.env si es necesario
```

Opción B: establecer en PowerShell antes de iniciar el backend:

```powershell
$env:URL_SERVIDOR_IA="http://127.0.0.1:9931"
$env:LIMITE_CONTEXTO_IA="2048"
```

Validación:
- `URL_SERVIDOR_IA`: solo se aceptan hosts `127.0.0.1` o `localhost`. Cualquier otro host provoca error al iniciar el backend.
- `LIMITE_CONTEXTO_IA`: debe ser un entero positivo (por defecto `2048`).

---
## 5. Crear el primer usuario

No existe registro público. Las cuentas las crea quien opera el servidor en la máquina local ejecutando `backend/crear_usuario.py`:

```powershell
.venv\Scripts\python.exe backend\crear_usuario.py revisor
```

El script solicitará la contraseña sin mostrarla en pantalla.

Argumentos reales de `crear_usuario.py`:
- `usuario` (posicional): nombre de usuario único.
- `--contrasena "..."`: pasar la contraseña directamente (solo recomendado para pruebas).
- `--reestablecer`: cambiar la contraseña de un usuario existente y revocar sus sesiones activas.
- `--bd <ruta>`: especificar una ruta SQLite distinta a la predeterminada.

---

## 6. Iniciar backend y frontend en terminales separadas

### Backend

Desde la raíz del repositorio, con el entorno virtual activado:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

La API queda disponible en `http://127.0.0.1:8000`. Documentación interactiva en `http://127.0.0.1:8000/docs`.

### Frontend

Desde la carpeta `frontend`:

```powershell
cd frontend
npm install
npm run dev
```

Vite queda disponible en `http://localhost:5173` (o el puerto que asigne).

Compruebe que ambos servicios responden antes de usar la aplicación.

---

## 7. Ejecutar las pruebas automatizadas

Desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe -m pytest backend
```

Se ejecutan 94 pruebas cubriendo autenticación, extracción, citas, análisis de IA y configuración por variables de entorno.

---

## 8. Cerrar procesos y errores comunes de arranque

### Cerrar procesos

- Backend (`uvicorn`): `Ctrl+C` en su terminal.
- Frontend (`npm run dev` / Vite): `Ctrl+C` en su terminal.
- `llama-server`: `Ctrl+C` en su terminal.

### Errores comunes

| Error | Causa probable | Solución |
|-------|---------------|----------|
| `modelo_no_disponible` (503) | `llama-server` no está en marcha en `127.0.0.1:9931` | Arrancar `llama-server` con los parámetros del paso 3. |
| Host no permitido | `URL_SERVIDOR_IA` apunta a un host distinto de `127.0.0.1` o `localhost` | Corregir la variable de entorno a un host loopback. |
| `LIMITE_CONTEXTO_IA` debe ser un entero positivo | Valor no entero, cero o negativo | Asignar un valor entero mayor a 0 (por defecto `2048`). |
| Contratos extensos exceden el contexto | El documento supera los 2048 tokens | Usar un texto más corto; el análisis se detiene sin inventar hallazgos. |

---

## 9. Limitaciones reales

- **Modelo local:** todo el análisis se ejecuta contra `llama-server` en `127.0.0.1:9931`; no se envía texto a servicios externos.
- **Contexto 2048 tokens:** contratos extensos pueden excederlo; en ese caso el análisis se detiene y no se generan hallazgos inventados. Con el valor predeterminado de 2048, el prompt fijo con criterios ocupa aproximadamente 1.794–1.800 caracteres. La capacidad estimada para el texto del contrato es de aproximadamente 3.400–3.500 caracteres con la heurística conservadora de 3,5 caracteres por token; es una estimación, no una medición con el tokenizador de Phi-3. En esta máquina existe `D:\llama.cpp\llama-server.exe` (versión 0.7.0-dev, build 11683, commit a8d9a7e1e) y el modelo `D:\Modelos\Phi-3-mini-4k-instruct-q4.gguf` (contexto de entrenamiento 4096). Una instancia temporal en el puerto 9932 aceptó `-c 4096`; `/v1/models` y `/slots` reportaron contexto 4096, y el backend leyó `LIMITE_CONTEXTO_IA=4096`. Sin embargo, una solicitud sintética de 2.000 caracteres llegó al servidor pero la generación no produjo tokens ni completó, por lo que 4096 está comprobada a nivel de arranque, no validada de extremo a extremo.
- **Idioma español:** el análisis está disponible solo en español.
- **Citas textuales:** se validan contra el documento original; no se aceptan citas inventadas.
- **Revisión jurídica humana:** los hallazgos son orientativos y requieren revisión humana. La herramienta no emite dictámenes jurídicos ni garantiza la validez de ningún contrato.

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

*Última actualización: alineación con el prototipo funcional (backend, frontend, análisis local de IA, historial de análisis, variables de entorno y pruebas).*

