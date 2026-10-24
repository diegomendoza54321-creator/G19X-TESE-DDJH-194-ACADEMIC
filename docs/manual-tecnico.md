# Manual Técnico

**Proyecto:** MotorRevisionLegal  
**Estado:** Completado para el flujo implementado en el prototipo. Algunos puntos se marcan como no verificados.

---

## 1. Descripción general del sistema

MotorRevisionLegal es una aplicación web con backend FastAPI (Python) y frontend React/TypeScript/Vite. El backend expone una API privada con sesiones SQLite, extrae texto de PDF/DOCX, clasifica el tipo de contrato de forma local y analiza cláusulas contra un servidor local `llama-server` (llama.cpp). El historial de análisis se persiste en SQLite aislado por usuario. No se envía texto de contratos a servicios externos.

---

## 2. Estructura del repositorio

```
MotorRevisionLegal/
├── backend/
│   ├── app/
│   │   ├── analisis_ia.py   # Cliente del servidor local de IA
│   │   ├── auth.py          # Sesiones SQLite, PBKDF2 (RF-00)
│   │   ├── citas.py         # Validación de citas textuales
│   │   ├── clasificacion.py # Clasificación local de tipo de contrato
│   │   ├── extraccion.py    # Extracción de texto PDF/DOCX (RF-01, RF-02)
│   │   ├── historial.py     # Persistencia/consulta del historial
│   │   └── main.py          # Endpoints de la API
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── crear_usuario.py     # Alta local de usuarios (RF-00.5)
│   ├── .env.example
│   └── tests/
├── frontend/
│   ├── src/App.tsx          # Interfaz principal
│   └── package.json
├── docs/
└── README.md
```

---

## 3. Backend

### 3.1 Módulos principales

- `app/main.py`: instancia FastAPI y endpoints; valida sesión y deriva `usuario_id` de la cookie.
- `app/auth.py`: usuarios, sesiones opacas en cookie HttpOnly, PBKDF2-HMAC-SHA256 (210 000 iteraciones), SQLite.
- `app/historial.py`: inserta y lista análisis por `usuario_id`; ordena por `fecha DESC, id DESC`.
- `app/extraccion.py`: valida formato/tamaño y extrae texto de PDF (pypdf) y DOCX (python-docx); no devuelve texto parcial.
- `app/clasificacion.py`: clasificación local determinista del tipo de contrato (prestación de servicios o proveedor).
- `app/analisis_ia.py`: construye prompts, llama a `llama-server`, valida JSON y citas; lee `URL_SERVIDOR_IA` y `LIMITE_CONTEXTO_IA`.
- `app/citas.py`: normaliza y verifica que las citas existan literalmente en el texto.

### 3.2 Endpoints de la API

- `GET /salud` — comprobación pública del servicio.
- `POST /login` — inicia sesión con `usuario` y `contrasena`.
- `POST /logout` — cierra la sesión actual (requiere sesión).
- `GET /yo` — devuelve el usuario de la sesión (requiere sesión).
- `POST /extraer` — recibe un PDF o DOCX y devuelve el texto extraído (requiere sesión).
- `POST /clasificar` — propone el tipo de contrato del texto extraído (requiere sesión).
- `POST /analizar-con-ia` — analiza cláusulas con IA local (requiere sesión y tipo confirmado).
- `GET /analizar-con-ia/estado` — ocupación del análisis local (requiere sesión).
- `GET /historial` — devuelve los análisis del usuario autenticado (requiere sesión).

### 3.3 Variables de entorno

- `MOTORREVISIONLEGAL_DB`: ruta SQLite (por defecto `backend/datos.db`).
- `URL_SERVIDOR_IA`: URL del servidor local; solo se aceptan hosts `127.0.0.1` o `localhost` (por defecto `http://127.0.0.1:9931`).
- `LIMITE_CONTEXTO_IA`: entero positivo (por defecto `2048`).

El proyecto no carga `.env` automáticamente; las variables deben estar en el entorno.

### 3.4 Ejecución de pruebas

Desde la raíz del repositorio:

```
.venv\Scripts\python.exe -m pytest backend
```

Última colección verificada: 101 pruebas (`test_analisis_ia` 28, `test_api` 10, `test_auth` 17, `test_citas` 28, `test_extraccion` 14, `test_historial` 4).

---

### 3.5 Base de datos

SQLite con tablas `usuarios`, `sesiones` y `analisis`. La tabla `analisis` almacena `usuario_id`, `fecha`, `tipo_confirmado`, `num_hallazgos` y `hallazgos` (JSON). El filtrado por usuario se realiza en SQL con parámetro. No se guardan contrato, prompt ni archivo original.

---

## 4. Frontend

### 4.1 Componentes principales

La interfaz principal está en `frontend/src/App.tsx` (componente único). Gestiona sesión, navegación (`inicio`, `analizar`, `resultados`, `historial`), tema claro/oscuro (persistido en `localStorage`), carga/extracción, clasificación, análisis y visualización del historial.

### 4.2 Comunicación con el backend

El frontend llama a rutas relativas (`/login`, `/yo`, `/extraer`, `/clasificar`, `/analizar-con-ia`, `/analizar-con-ia/estado`, `/historial`, `/logout`). El servidor de desarrollo de Vite redirige al backend; no se requiere CORS en desarrollo.

---

## 5. Integración con la API de IA

- `analisis_ia.py` lee `URL_SERVIDOR_IA` y `LIMITE_CONTEXTO_IA`.
- Construye mensajes con criterios base y criterios condicionales según el tipo confirmado.
- Llama a `llama-server` en loopback (`/v1/chat/completions`), con endpoints auxiliares (`/slots`, `/tokenize`).
- Parsea la respuesta JSON del modelo y convierte cada hallazgo.
- `citas.py` valida que la cita exista literalmente en el texto; los hallazgos con citas inventadas se descartan.
- No se envía texto a servicios externos.

---

## 6. Despliegue (verificado parcialmente)

Comandos documentados en `README.md` y verificados en el entorno de desarrollo Windows:

1. Crear entorno: `python -m venv .venv`
2. Instalar dependencias: `.venv\Scripts\python.exe -m pip install -r backend\requirements.txt`
3. Crear usuario: `.venv\Scripts\python.exe backend\crear_usuario.py <usuario>`
4. Variables de entorno en PowerShell (`$env:URL_SERVIDOR_IA`, `$env:LIMITE_CONTEXTO_IA`).
5. Arrancar backend: `.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload`
6. Arrancar frontend: `cd frontend; npm install; npm run dev`
7. Arrancar `llama-server` en `127.0.0.1:9931` (no incluido en el repositorio).

No se ha verificado un despliegue de producción ni la validación completa del contexto de 4096 tokens.

---

## 7. Decisiones técnicas

- Sesiones con token opaco en cookie HttpOnly; solo se guarda el hash del token.
- Sin registro público; las cuentas se crean localmente.
- No se guardan archivos originales ni texto de contratos en logs.
- La extracción no devuelve texto parcial ante fallos.
- Las citas se validan literalmente contra el documento.

---

## 8. Problemas conocidos y deuda técnica

- El manual de despliegue de producción no está verificado.
- La validación end-to-end del contexto de 4096 tokens en `llama-server` no se completó (solo arranque).
- El frontend concentra toda la interfaz en un único componente (`App.tsx`).
- La sección **Resultados** de la navegación no muestra aún un informe separado del análisis reciente.

---

*Manual técnico completado con base en el código y la documentación verificados.*
