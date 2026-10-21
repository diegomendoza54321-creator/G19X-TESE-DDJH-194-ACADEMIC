# MotorRevisionLegal

Herramienta web de revisiÃ³n de clÃ¡usulas contractuales â€” Proyecto de Residencias Profesionales.

---

## DescripciÃ³n

MotorRevisionLegal apoya la revisiÃ³n de contratos de prestaciÃ³n de servicios y de proveedores. Extrae el texto del documento, propone su tipo, permite que la persona usuaria confirme o corrija esa clasificaciÃ³n y genera un informe de hallazgos respaldado por fragmentos del contrato original.

El acceso es privado: solo pueden entrar cuentas autorizadas. No existe registro pÃºblico.

**Los hallazgos son orientativos y requieren revisiÃ³n humana. La herramienta no emite dictÃ¡menes jurÃ­dicos ni garantiza la validez de ningÃºn contrato.**

---

## Funciones

### Incluidas en el alcance

- Cargar contratos en formato **PDF con texto seleccionable** o **DOCX**.
- Proponer el tipo de contrato (prestaciÃ³n de servicios o proveedor) con una justificaciÃ³n breve basada en el texto.
- Permitir que la persona usuaria **confirme o corrija la clasificaciÃ³n** antes de iniciar el anÃ¡lisis.
- Aplicar una lista de verificaciÃ³n base y criterios condicionales segÃºn el tipo confirmado (pendiente: criterios condicionales por tipo no implementados en este prototipo).
- Identificar posibles ambigÃ¼edades, omisiones, contradicciones aparentes y riesgos contractuales.
- Generar hallazgos respaldados por citas textuales del documento original.
- Presentar por cada hallazgo: explicaciÃ³n, posible consecuencia, recomendaciÃ³n y limitaciones del anÃ¡lisis.
- Mostrar el informe en pantalla. Las categorÃ­as sin hallazgos se ocultan; si no hay ninguno, se indica que no se identificaron hallazgos con los criterios aplicados.
- Consultar anÃ¡lisis anteriores desde la secciÃ³n **Historial** (pendiente: no implementado en este prototipo).
- Interfaz con **tema claro y oscuro**; la preferencia se recuerda en el navegador.
- NavegaciÃ³n con: **Inicio**, **Analizar contrato**, **Resultados** e **Historial**. Las secciones *CÃ³mo funciona* y *Criterios* pueden incluirse tambiÃ©n.

### Limitaciones conocidas

- No inventa citas, clÃ¡usulas ni obligaciones que no estÃ©n en el documento.
- No determina la validez legal ni la ejecutabilidad de ningÃºn contrato.
- Requiere archivos PDF con texto seleccionable. Los PDF escaneados sin capa de texto no estÃ¡n soportados.
- Si la extracciÃ³n del texto falla o resulta incompleta, el anÃ¡lisis se detiene y no se generan hallazgos.
- Alcance inicial: contratos de prestaciÃ³n de servicios y de proveedores en espaÃ±ol. No soporta otros tipos ni idiomas.

### Fuera del alcance inicial

- Descarga o exportaciÃ³n del informe.
- Compartir el informe por correo u otro medio.
- Registro pÃºblico de nuevos usuarios.
- PDF escaneados (OCR).
- ComparaciÃ³n entre versiones de un contrato.
- IntegraciÃ³n con sistemas ERP u otras plataformas externas.
- GeneraciÃ³n automÃ¡tica de contratos o clÃ¡usulas.
- Firma electrÃ³nica.

---

## Estado del proyecto

> **Fase actual:** Prototipo funcional (backend, frontend, anÃ¡lisis local de IA y pruebas automatizadas).

El prototipo incluye backend (FastAPI), frontend (React/Vite), clasificaciÃ³n local de tipo de contrato, extracciÃ³n de texto de PDF/DOCX y anÃ¡lisis de clÃ¡usulas contra un servidor local `llama-server` (llama.cpp) con modelo Phi-3 GGUF en `127.0.0.1:9931`. Las pruebas backend pasan con `pytest`.

Algunos elementos del alcance inicial siguen pendientes: **historial de anÃ¡lisis** y **criterios de verificaciÃ³n condicionales por tipo de contrato**. No se prometen como terminados.

---

## TecnologÃ­as

| Componente | TecnologÃ­a | Estado |
|---|---|---|
| Backend | Python 3.14 + FastAPI | Implementado |
| Frontend | React 19 + TypeScript + Vite | Implementado |
| Estilos | CSS (tema claro/oscuro) | Implementado |
| Base de datos | SQLite | Implementado |
| ExtracciÃ³n de texto | pypdf, python-docx | Implementado |
| IA / LLM | llama-server (llama.cpp) con Phi-3 GGUF local | Implementado (loopback) |
| AutenticaciÃ³n | Sesiones SQLite, PBKDF2-SHA256 | Implementado |
| Pruebas backend | pytest, httpx, httpx2, fpdf2 | Implementado |
| Control de versiones | Git + GitHub | En uso |

### Decisiones de arquitectura

- El servidor de IA corre localmente en `127.0.0.1:9931` (loopback, sin red externa). Nunca se envÃ­a texto de contratos a servicios de terceros.
- La URL del servidor y el lÃ­mite de contexto se leen de variables de entorno (`URL_SERVIDOR_IA`, `LIMITE_CONTEXTO_IA`) con valores predeterminados `http://127.0.0.1:9931` y `2048`.
- El archivo `backend/.env.example` es una plantilla; `.env` **no se carga automÃ¡ticamente**. Las variables deben establecerse en el entorno antes de iniciar el backend.

---

## 1. Requisitos previos y ruta de trabajo

Se necesita Windows con:

- **Python 3.14** (incluye `pip`). Durante la instalaciÃ³n, marcar "Add Python to PATH".
- **Node.js** (solo para el frontend; versiÃ³n indicada en `frontend/package.json`).
- **llama.cpp** con el ejecutable `llama-server` y un modelo GGUF (recomendado: Phi-3 mini 4K instruct, cuantificado q4_0).

Todos los comandos de este documento se ejecutan desde la **raÃ­z del repositorio** (donde estÃ¡ este `README.md`), en PowerShell, a menos que se indique lo contrario.

Estructura esperada:

```
MotorRevisionLegal/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ analisis_ia.py
â”‚   â”‚   â”œâ”€â”€ auth.py
â”‚   â”‚   â”œâ”€â”€ citas.py
â”‚   â”‚   â”œâ”€â”€ clasificacion.py
â”‚   â”‚   â”œâ”€â”€ extraccion.py
â”‚   â”‚   â””â”€â”€ main.py
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â”œâ”€â”€ pytest.ini
â”‚   â”œâ”€â”€ crear_usuario.py
â”‚   â”œâ”€â”€ .env.example
â”‚   â””â”€â”€ tests/
â”œâ”€â”€ frontend/
â”‚   â””â”€â”€ package.json
â”œâ”€â”€ docs/
â”œâ”€â”€ .gitignore
â””â”€â”€ README.md
```

---

## 2. Crear el entorno virtual e instalar dependencias del backend

Desde la raÃ­z del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Esto instala las dependencias listadas en `backend/requirements.txt`:
- `fastapi`, `uvicorn[standard]`, `python-multipart` (API)
- `pypdf`, `python-docx` (extracciÃ³n de texto)
- `pytest`, `httpx`, `httpx2`, `fpdf2` (pruebas)

---## 3. Preparar llama.cpp y el modelo GGUF

El anÃ¡lisis de clÃ¡usulas depende de **llama-server** (de llama.cpp) ejecutÃ¡ndose en `127.0.0.1:9931`.

### Archivos necesarios

- Ejecutable `llama-server` de llama.cpp.
- **Dato del entorno comprobado (no es requisito general):** en la máquina de desarrollo se verificó la presencia de `D:\llama.cpp\llama-server.exe` con la versión `0.7.0-dev (build 11683, commit a8d9a7e1e)`, compilado con Clang 20.1.8 para Windows x86_64. El proyecto no exige esta versión ni build concretos; cualquier binario compatible de llama.cpp que responda en `127.0.0.1:9931` es válido.
- Modelo GGUF. El proyecto recomienda **Phi-3 mini 4K instruct, cuantificado q4_0** (por ejemplo: `model\Phi-3-mini-4k-instruct-q4_0.gguf`) como referencia. El repositorio **no incluye** ni especifica una URL de descarga ni una versión concreta de llama.cpp ni del modelo; el usuario debe proporcionar ambos archivos y ajustar la ruta `-m` al modelo que tenga disponible.

### Arrancar llama-server

Desde la carpeta que contenga `llama-server.exe` y el modelo:

```powershell
.\llama-server.exe -m 'C:\Modelos\modelo.gguf' --host 127.0.0.1 --port 9931 -c 2048
```

ParÃ¡metros clave:

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
Si no se dispone de `llama-server`, el backend arranca igualmente, pero el endpoint de anÃ¡lisis responderÃ¡ con error de conexiÃ³n (`modelo_no_disponible`, HTTP 503) hasta que `llama-server` estÃ© en marcha.

---

## 4. Configurar variables de entorno (`URL_SERVIDOR_IA` y `LIMITE_CONTEXTO_IA`)

El archivo `backend/.env.example` es una **plantilla de referencia**:

```
URL_SERVIDOR_IA=http://127.0.0.1:9931
LIMITE_CONTEXTO_IA=2048
```

**`.env` no se carga automÃ¡ticamente.** El backend lee las variables directamente del entorno del sistema operativo mediante `os.environ.get`.

OpciÃ³n A: crear archivo `.env`:

```powershell
copy backend\.env.example backend\.env
# Editar backend\.env si es necesario
```

OpciÃ³n B: establecer en PowerShell antes de iniciar el backend:

```powershell
$env:URL_SERVIDOR_IA="http://127.0.0.1:9931"
$env:LIMITE_CONTEXTO_IA="2048"
```

ValidaciÃ³n:
- `URL_SERVIDOR_IA`: solo se aceptan hosts `127.0.0.1` o `localhost`. Cualquier otro host provoca error al iniciar el backend.
- `LIMITE_CONTEXTO_IA`: debe ser un entero positivo (por defecto `2048`).

---## 5. Crear el primer usuario

No existe registro pÃºblico. Las cuentas las crea quien opera el servidor en la mÃ¡quina local ejecutando `backend/crear_usuario.py`:

```powershell
.venv\Scripts\python.exe backend\crear_usuario.py revisor
```

El script solicitarÃ¡ la contraseÃ±a sin mostrarla en pantalla.

Argumentos reales de `crear_usuario.py`:
- `usuario` (posicional): nombre de usuario Ãºnico.
- `--contrasena "..."`: pasar la contraseÃ±a directamente (solo recomendado para pruebas).
- `--reestablecer`: cambiar la contraseÃ±a de un usuario existente y revocar sus sesiones activas.
- `--bd <ruta>`: especificar una ruta SQLite distinta a la predeterminada.

---

## 6. Iniciar backend y frontend en terminales separadas

### Backend

Desde la raÃ­z del repositorio, con el entorno virtual activado:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

La API queda disponible en `http://127.0.0.1:8000`. DocumentaciÃ³n interactiva en `http://127.0.0.1:8000/docs`.

### Frontend

Desde la carpeta `frontend`:

```powershell
cd frontend
npm install
npm run dev
```

Vite queda disponible en `http://localhost:5173` (o el puerto que asigne).

Compruebe que ambos servicios responden antes de usar la aplicaciÃ³n.

---

## 7. Ejecutar las pruebas automatizadas

Desde la raÃ­z del repositorio:

```powershell
.venv\Scripts\python.exe -m pytest backend
```

Se ejecutan 94 pruebas cubriendo autenticaciÃ³n, extracciÃ³n, citas, anÃ¡lisis de IA y configuraciÃ³n por variables de entorno.

---

## 8. Cerrar procesos y errores comunes de arranque

### Cerrar procesos

- Backend (`uvicorn`): `Ctrl+C` en su terminal.
- Frontend (`npm run dev` / Vite): `Ctrl+C` en su terminal.
- `llama-server`: `Ctrl+C` en su terminal.

### Errores comunes

| Error | Causa probable | SoluciÃ³n |
|-------|---------------|----------|
| `modelo_no_disponible` (503) | `llama-server` no estÃ¡ en marcha en `127.0.0.1:9931` | Arrancar `llama-server` con los parÃ¡metros del paso 3. |
| Host no permitido | `URL_SERVIDOR_IA` apunta a un host distinto de `127.0.0.1` o `localhost` | Corregir la variable de entorno a un host loopback. |
| `LIMITE_CONTEXTO_IA` debe ser un entero positivo | Valor no entero, cero o negativo | Asignar un valor entero mayor a 0 (por defecto `2048`). |
| Contratos extensos exceden el contexto | El documento supera los 2048 tokens | Usar un texto mÃ¡s corto; el anÃ¡lisis se detiene sin inventar hallazgos. |

---

## 9. Limitaciones reales

- **Modelo local:** todo el anÃ¡lisis se ejecuta contra `llama-server` en `127.0.0.1:9931`; no se envÃ­a texto a servicios externos.
- **Contexto 2048 tokens:** contratos extensos pueden excederlo; en ese caso el anÃ¡lisis se detiene y no se generan hallazgos inventados.
- **Idioma espaÃ±ol:** el anÃ¡lisis estÃ¡ disponible solo en espaÃ±ol.
- **Citas textuales:** se validan contra el documento original; no se aceptan citas inventadas.
- **RevisiÃ³n jurÃ­dica humana:** los hallazgos son orientativos y requieren revisiÃ³n humana. La herramienta no emite dictÃ¡menes jurÃ­dicos ni garantiza la validez de ningÃºn contrato.

---## Estructura del proyecto

```
MotorRevisionLegal/
â”œâ”€â”€ backend/           # API y lÃ³gica de anÃ¡lisis (Python / FastAPI)
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ analisis_ia.py   # Cliente del servidor local de IA (llama-server)
â”‚   â”‚   â”œâ”€â”€ auth.py          # Sesiones SQLite, PBKDF2 (RF-00)
â”‚   â”‚   â”œâ”€â”€ citas.py         # ValidaciÃ³n de citas textuales
â”‚   â”‚   â”œâ”€â”€ clasificacion.py # ClasificaciÃ³n local de tipo de contrato
â”‚   â”‚   â”œâ”€â”€ extraccion.py    # ExtracciÃ³n de texto PDF/DOCX (RF-01, RF-02)
â”‚   â”‚   â””â”€â”€ main.py          # Endpoints de la API
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â”œâ”€â”€ pytest.ini
â”‚   â”œâ”€â”€ crear_usuario.py     # Alta local de usuarios autorizados (RF-00.5)
â”‚   â”œâ”€â”€ .env.example         # Plantilla de variables de entorno
â”‚   â””â”€â”€ tests/               # Pruebas automatizadas (pytest)
â”œâ”€â”€ frontend/          # Interfaz de usuario (React / TypeScript / Vite)
â”œâ”€â”€ docs/              # DocumentaciÃ³n del proyecto
â”‚   â”œâ”€â”€ MVP.md
â”‚   â”œâ”€â”€ PRD.md
â”‚   â”œâ”€â”€ requisitos.md
â”‚   â”œâ”€â”€ arquitectura.md
â”‚   â”œâ”€â”€ plan-de-pruebas.md
â”‚   â”œâ”€â”€ bitacora.md
â”‚   â”œâ”€â”€ entregables.md
â”‚   â”œâ”€â”€ guia-instalacion.md
â”‚   â”œâ”€â”€ manual-usuario.md
â”‚   â””â”€â”€ manual-tecnico.md
â”œâ”€â”€ .gitignore
â””â”€â”€ README.md
```

---

## DocumentaciÃ³n

| Documento | DescripciÃ³n |
|---|---|
| [docs/MVP.md](docs/MVP.md) | Alcance del MVP: funciones, flujo, criterios de aceptaciÃ³n y condiciones de tÃ©rmino |
| [docs/PRD.md](docs/PRD.md) | Documento de requisitos del producto |
| [docs/requisitos.md](docs/requisitos.md) | Requisitos funcionales y no funcionales |
| [docs/arquitectura.md](docs/arquitectura.md) | Arquitectura propuesta del sistema |
| [docs/plan-de-pruebas.md](docs/plan-de-pruebas.md) | Plan de pruebas y casos de prueba |
| [docs/bitacora.md](docs/bitacora.md) | BitÃ¡cora de avance del proyecto |
| [docs/entregables.md](docs/entregables.md) | Lista de control de entregables de la residencia |
| [docs/guia-instalacion.md](docs/guia-instalacion.md) | GuÃ­a de instalaciÃ³n y arranque |
| [docs/manual-usuario.md](docs/manual-usuario.md) | Manual de usuario |
| [docs/manual-tecnico.md](docs/manual-tecnico.md) | Manual tÃ©cnico |

---

## Residencias profesionales

Este proyecto se desarrolla como parte de un programa de residencias profesionales. Los entregables acadÃ©micos requeridos y su estado actual se describen en [`docs/entregables.md`](docs/entregables.md).

---

*Ãšltima actualizaciÃ³n: alineaciÃ³n con el prototipo funcional (backend, frontend, anÃ¡lisis local de IA, variables de entorno y pruebas). Pendientes: historial de anÃ¡lisis y criterios condicionales por tipo de contrato.*

