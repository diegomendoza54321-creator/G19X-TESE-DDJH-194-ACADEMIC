# Backend — MotorRevisionLegal

API en FastAPI. **Bloques implementados: autenticación privada (RF-00) y
carga y extracción de texto** de contratos en PDF y DOCX.

No hay IA ni criterios jurídicos en este bloque: la extracción es el paso
previo y quedó aislada a propósito para poder verificarse sin depender de
decisiones que siguen pendientes (proveedor de IA, validación jurídica de
criterios).

## Requisitos verificados

| Herramienta | Versión comprobada |
|---|---|
| Python | 3.14.4 (Windows) |
| pip | 26.0.1 |

Node.js **no** está instalado en el equipo: el frontend no puede arrancar
todavía. Eso no afecta a este bloque.

## Instalación

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

## Autenticación privada (RF-00)

Toda la API salvo `GET /salud` y `POST /login` exige sesión. El login
entrega un token opaco en cookie `HttpOnly` (`sesion_mrl`, 12 horas).
Contraseñas con PBKDF2-SHA256 y sal única; la base SQLite vive en
`backend/datos.db` (ignorada por git) o en `MOTORREVISIONLEGAL_DB`.

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

**Pendientes, no resueltas aquí:** proveedor de IA, validación jurídica de
criterios, historial, estrategia de despliegue.

## Estructura

```text
backend/
├── requirements.txt
├── pytest.ini
├── crear_usuario.py  ← alta local de usuarios autorizados (RF-00.5)
├── app/
│   ├── __init__.py
│   ├── auth.py         ← sesiones SQLite, PBKDF2 (RF-00)
│   ├── extraccion.py   ← lógica de extracción (RF-01, RF-02)
│   └── main.py         ← endpoints de la API
└── tests/
    ├── conftest.py         ← genera PDF/DOCX sintéticos
    ├── test_extraccion.py  ← pruebas del módulo
    ├── test_api.py         ← pruebas de /extraer (con sesión)
    └── test_auth.py        ← pruebas de autenticación (RF-00)
```

> La guía de instalación oficial sigue siendo
> [`docs/guia-instalacion.md`](../docs/guia-instalacion.md), que continúa
> pendiente de verificar en un entorno limpio. Este README documenta lo
> verificado hasta ahora.
