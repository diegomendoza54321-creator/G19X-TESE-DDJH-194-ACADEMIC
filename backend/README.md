# Backend — MotorRevisionLegal

API en FastAPI con autenticación privada (RF-00), carga y extracción de texto de contratos en PDF y DOCX, y análisis de cláusulas mediante servidor local de IA (llama-server con Phi-3 GGUF) en loopback.

## Entorno de desarrollo

Se probó con Python 3.14 sobre Windows. Node.js es requerido solo para el frontend (ver `frontend/package.json`).

## Instalación

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Variables de entorno

El backend lee dos variables de entorno mediante `os.environ.get`. **No se carga `.env` automáticamente.**

| Variable | Valor predeterminado | Descripción |
|---|---|---|
| `URL_SERVIDOR_IA` | `http://127.0.0.1:9931` | URL del servidor local de IA (llama-server). Solo se aceptan hosts `127.0.0.1` o `localhost`. |
| `LIMITE_CONTEXTO_IA` | `2048` | Límite de contexto en tokens (debe ser entero positivo). |

Plantilla en `backend/.env.example`. Ejemplo de establecimiento en PowerShell antes de iniciar el backend:

```powershell
$env:URL_SERVIDOR_IA="http://127.0.0.1:9931"
$env:LIMITE_CONTEXTO_IA="2048"
```

## Servidor local de IA (llama-server)

El análisis de cláusulas requiere `llama-server` (llama.cpp) en marcha en `127.0.0.1:9931` con un modelo GGUF (Phi-3 recomendado) y contexto 2048:

```powershell
.\llama-server.exe -m model\Phi-3-mini-4k-instruct-q4_0.gguf --host 127.0.0.1 --port 9931 -c 2048
```

El backend rechaza cualquier URL cuyo host no sea `127.0.0.1` ni `localhost` (conexión estrictamente local, sin red externa). Si `llama-server` no está disponible, el endpoint de análisis responde con error `modelo_no_disponible` (503).

## Autenticación privada (RF-00)

Toda la API salvo `GET /salud` y `POST /login` exige sesión. El login
entrega un token opaco en cookie `HttpOnly` (`sesion_mrl`, 12 horas).
Contraseñas con PBKDF2-HMAC-SHA256 y sal única; la base SQLite vive en
`backend/datos.db` o en la ruta indicada por `MOTORREVISIONLEGAL_DB`.

**No existe registro público.** Las cuentas las crea quien opere el
servidor en la máquina local:

```powershell
.venv\Scripts\python.exe backend\crear_usuario.py revisor
```

### `POST /login`, `POST /logout`, `GET /yo`

Login con formulario (`usuario`, `contrasena`). Ante credenciales
incorrectas el mensaje es siempre genérico: `Usuario o contraseña
incorrectos` (RF-00.3), sin revelar qué falló. Sin sesión válida la API
responde `401` con motivo `Se requiere iniciar sesión...`.

### `POST /analizar-con-ia`

Requiere sesión. Recibe `texto` y `tipo_confirmado`, y llama al servidor local de IA para generar hallazgos.

### `GET /analizar-con-ia/estado`

Requiere sesión. Devuelve si el servidor local de IA está ocupado (`/slots`).

## Ejecutar la API

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Queda disponible en `http://127.0.0.1:8000`. Documentación interactiva en
`http://127.0.0.1:8000/docs`.

## Ejecutar las pruebas

```powershell
.venv\Scripts\python.exe -m pytest backend
```

## Endpoints

### `GET /salud`

Comprueba que el servicio responde.

```json
{ "estado": "ok", "servicio": "MotorRevisionLegal" }
```

### `POST /extraer`

Recibe un archivo en el campo `archivo` y devuelve el texto extraído.

**Ejemplo:**

```powershell
curl -F "archivo=@contrato.pdf" http://127.0.0.1:8000/extraer
```

**Respuesta exitosa (200):**

```json
{
  "ok": true,
  "texto": "CONTRATO DE PRESTACION DE SERVICIOS...",
  "formato": "pdf",
  "num_paginas": 3,
  "codigo": null,
  "motivo": null
}
```

**Respuesta con fallo:**

```json
{
  "ok": false,
  "texto": null,
  "formato": null,
  "num_paginas": null,
  "codigo": "extraccion_incompleta",
  "motivo": "La extracción resultó incompleta: 1 de 2 páginas no contienen..."
}
```

## Reglas que cumple este bloque

| Regla | Comportamiento |
|---|---|
| RF-01.1, RF-01.2 | Acepta PDF con texto seleccionable y DOCX |
| RF-01.3 | Rechaza otros formatos con mensaje claro → `400` |
| RF-01.4 | Rechaza archivos vacíos y los que superan 10 MB → `400` |
| RF-02.1, RF-02.2 | Extrae el texto completo, incluida la tablas del DOCX |
| RF-02.3 | Ante fallo devuelve un motivo en español |
| RF-02.4 | **Nunca devuelve texto parcial**: `texto` es `null` ante fallo |
| RPJ-06 | Ante extracción incompleta detiene el flujo y lo informa |
| RNF-03.3 | No registra el contenido de los contratos en logs |

### Códigos de estado

| Estado | Significado |
|---|---|
| `400` | Problema del archivo enviado: formato, tamaño o archivo vacío |
| `422` | El archivo se recibió pero no pudo procesarse: corrupto, sin texto o extracción incompleta |

### Códigos de motivo

`formato_no_soportado`, `tamano_excedido`, `archivo_vacio`,
`archivo_no_leible`, `sin_texto`, `extraccion_incompleta`.

## Limitaciones del análisis de IA

- El análisis se realiza en español.
- El contexto es de 2048 tokens; contratos extensos pueden excederlo. En ese caso el análisis se detiene y no se generan hallazgos inventados.
- Las citas textuales se validan contra el documento original; no se aceptan citas inventadas.
- Los hallazgos son orientativos y requieren revisión jurídica humana.

## Decisiones tomadas y pendientes

**Tomadas en este bloque** (todas reversibles y documentadas en el código):

- Extracción de PDF con `pypdf`, elegida por ser Python puro y no requerir
  binarios del sistema. `pdfplumber` y `PyMuPDF` quedan como alternativas a
  evaluar.
- Tamaño máximo de 10 MB. **Pendiente de confirmar.**
- **Extracción incompleta** = el PDF declara N páginas y alguna no aporta
  texto (umbral `MIN_CARACTERES_POR_PAGINA = 20`). Corresponde al caso CG-02
  del plan de pruebas. Es una decisión de producto: conviene confirmarla.
- En DOCX se extraen párrafos y tablas; `num_paginas` se devuelve `null`
  porque un DOCX no declara páginas sin renderizarse.
- El servidor de IA corre localmente en `127.0.0.1:9931` (loopback). La URL y el límite de contexto se leen de variables de entorno.

**Pendientes, no resueltas aquí:** validación jurídica de criterios, historial, estrategia de despliegue.

## Estructura

```text
backend/
├── requirements.txt
├── pytest.ini
├── crear_usuario.py  ← alta local de usuarios autorizados (RF-00.5)
├── .env.example      ← plantilla de variables de entorno (no se carga automáticamente)
├── app/
│   ├── __init__.py
│   ├── analisis_ia.py   # cliente del servidor local de IA (URL y contexto por env var)
│   ├── auth.py          # sesiones SQLite, PBKDF2 (RF-00)
│   ├── citas.py         # validación de citas textuales
│   ├── clasificacion.py # clasificación local de tipo de contrato
│   ├── extraccion.py    # extracción de texto PDF/DOCX (RF-01, RF-02)
│   └── main.py          # endpoints de la API
└── tests/
    ├── conftest.py         # genera PDF/DOCX sintéticos
    ├── test_analisis_ia.py # pruebas de análisis y configuración por env var
    ├── test_api.py         # pruebas de /extraer (con sesión)
    ├── test_auth.py        # pruebas de autenticación (RF-00)
    ├── test_citas.py       # pruebas de citas textuales
    └── test_extraccion.py  # pruebas del módulo de extracción
```

> La guía de instalación completa está en [`README.md`](../README.md).
