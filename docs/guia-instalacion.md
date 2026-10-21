# Guía de Instalación — MotorRevisionLegal

**Proyecto:** MotorRevisionLegal  
**Estado:** Guía de instalación y arranque para el prototipo funcional.

Esta guía documenta los pasos para instalar y arrancar el backend, el frontend y el servidor local de IA (llama-server) en un entorno de desarrollo Windows.

---

## 1. Requisitos previos

| Componente | Notas |
|---|---|
| Sistema operativo | Windows |
| Python | 3.14 (probado con Python 3.14.4) |
| pip | Incluido con Python |
| Node.js | Verificar `frontend/package.json` | Solo para el frontend |

### Descargar e instalar

- **Python:** https://www.python.org/downloads/ (marcar "Add Python to PATH" durante la instalación).
- **Node.js:** https://nodejs.org/ (requerido solo si se va a usar el frontend).

---

## 2. Obtener el código fuente

Clonar el repositorio:

```powershell
git clone https://github.com/diegomendoza54321-creator/G19X-TESE-DDJH-194-ACADEMIC.git
cd G19X-TESE-DDJH-194-ACADEMIC
```

---

## 3. Instalación del backend

Desde la raíz del repositorio, crear el entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Dependencias instaladas (ver `backend/requirements.txt`):
- `fastapi`, `uvicorn[standard]`, `python-multipart` (API)
- `pypdf`, `python-docx` (extracción de texto)
- `pytest`, `httpx`, `httpx2`, `fpdf2` (pruebas)

---

## 4. Instalación del frontend

Desde la carpeta `frontend`:

```powershell
cd frontend
npm install
```

---

## 5. Configuración de variables de entorno

El archivo `backend/.env.example` es una plantilla de referencia:

```
URL_SERVIDOR_IA=http://127.0.0.1:9931
LIMITE_CONTEXTO_IA=2048
```

**`.env` no se carga automáticamente.** El backend lee las variables directamente del entorno del sistema operativo mediante `os.environ.get`.

### Opción A: Crear archivo `.env`

```powershell
copy backend\.env.example backend\.env
# Editar backend\.env si es necesario
```

### Opción B: Establecer en PowerShell antes de iniciar el backend

```powershell
$env:URL_SERVIDOR_IA="http://127.0.0.1:9931"
$env:LIMITE_CONTEXTO_IA="2048"
```

### Validación de las variables

- `URL_SERVIDOR_IA`: solo se aceptan hosts `127.0.0.1` o `localhost`. Cualquier otro host provoca error al iniciar el backend.
- `LIMITE_CONTEXTO_IA`: debe ser un entero positivo (por defecto `2048`).

---

## 6. Arrancar el servidor local de IA (llama-server)

El análisis de cláusulas depende de `llama-server` (llama.cpp) escuchando en `127.0.0.1:9931`.

### Requisitos

- Ejecutable `llama-server` de llama.cpp.
- Modelo GGUF (recomendado: Phi-3 mini 4K instruct, cuantificado q4_0).

### Comando de arranque (ejemplo)

```powershell
.\llama-server.exe -m model\Phi-3-mini-4k-instruct-q4_0.gguf --host 127.0.0.1 --port 9931 -c 2048
```

Parámetros clave:
- `-m`: ruta al archivo `.gguf` del modelo.
- `--host 127.0.0.1`: escucha solo en loopback (sin red externa).
- `--port 9931`: puerto que el backend espera por defecto.
- `-c 2048`: contexto de 2048 tokens.

### Si no hay llama-server disponible

El backend arranca igualmente, pero el endpoint de análisis responderá con error de conexión (`modelo_no_disponible`, HTTP 503) hasta que `llama-server` esté en marcha.

---

## 7. Ejecutar la API (backend)

Desde la raíz del repositorio, con el entorno virtual activado:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

La API queda disponible en `http://127.0.0.1:8000`. Documentación interactiva en `http://127.0.0.1:8000/docs`.

---

## 8. Ejecutar el frontend

Desde la carpeta `frontend`:

```powershell
npm run dev
```

Vite queda disponible en `http://localhost:5173` (o el puerto que asigne).

---

## 9. Crear el primer usuario

No existe registro público. Las cuentas las crea quien opera el servidor en la máquina local ejecutando `backend/crear_usuario.py`:

```powershell
.venv\Scripts\python.exe backend\crear_usuario.py revisor
```

El script solicitará la contraseña sin mostrarla en pantalla.

Opciones útiles:
- `--contrasena "..."`: pasar la contraseña directamente (solo recomendado para pruebas).
- `--reestablecer`: cambiar la contraseña de un usuario existente y revocar sus sesiones.
- `--bd <ruta>`: especificar una ruta SQLite distinta a la predeterminada.

---

## 10. Ejecutar las pruebas

Desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe -m pytest backend
```

Se ejecutan 94 pruebas cubriendo autenticación, extracción, citas, análisis de IA y configuración por variables de entorno.

---

## 11. Limitaciones conocidas

- **Idioma:** el análisis está disponible solo en español.
- **Contexto:** 2048 tokens. Contratos extensos pueden excederlo; en ese caso el análisis se detiene y no se generan hallazgos inventados.
- **Citas textuales:** se validan contra el documento original. No se aceptan citas inventadas.
- **PDF escaneados:** no se soportan (no hay capa de texto / OCR).
- **Extracción incompleta:** si alguna página del PDF no aporta texto, el análisis se detiene.
- **Hallazgos orientativos:** requieren revisión jurídica humana. La herramienta no emite dictámenes jurídicos ni garantiza la validez de ningún contrato.

---

## 12. Uso de asistentes de IA en el desarrollo

Este proyecto fue desarrollado con la asistencia de herramientas de IA para generación y revisión de código y documentación. Todo el código y la documentación fueron revisados y validados por la persona desarrolladora. El uso de asistentes de IA **no sustituye la revisión humana**, especialmente en el análisis jurídico de contratos, que debe ser validado por un profesional habilitado.

---

*Última actualización: alineada con el prototipo funcional (backend, frontend, análisis local de IA, variables de entorno y pruebas). Pendientes: historial de análisis y criterios condicionales por tipo de contrato.*
