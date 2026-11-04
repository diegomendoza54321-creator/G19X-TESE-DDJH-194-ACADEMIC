# Manual TÃ©cnico

**Proyecto:** MotorRevisionLegal  
**Estado:** Completado para el flujo implementado en el prototipo. Algunos puntos se marcan como no verificados.

---

## 1. DescripciÃ³n general del sistema

MotorRevisionLegal es una aplicaciÃ³n web con backend FastAPI (Python) y frontend React/TypeScript/Vite. El backend expone una API privada con sesiones SQLite, extrae texto de PDF/DOCX, clasifica el tipo de contrato de forma local y analiza clÃ¡usulas contra un servidor local `llama-server` (llama.cpp). El historial de anÃ¡lisis se persiste en SQLite aislado por usuario. No se envÃ­a texto de contratos a servicios externos.

---

## 2. Estructura del repositorio

```
MotorRevisionLegal/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ analisis_ia.py   # Cliente del servidor local de IA
â”‚   â”‚   â”œâ”€â”€ auth.py          # Sesiones SQLite, PBKDF2 (RF-00)
â”‚   â”‚   â”œâ”€â”€ citas.py         # ValidaciÃ³n de citas textuales
â”‚   â”‚   â”œâ”€â”€ clasificacion.py # ClasificaciÃ³n local de tipo de contrato
â”‚   â”‚   â”œâ”€â”€ extraccion.py    # ExtracciÃ³n de texto PDF/DOCX (RF-01, RF-02)
â”‚   â”‚   â”œâ”€â”€ historial.py     # Persistencia/consulta del historial
â”‚   â”‚   â””â”€â”€ main.py          # Endpoints de la API
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â”œâ”€â”€ pytest.ini
â”‚   â”œâ”€â”€ crear_usuario.py     # Alta local de usuarios (RF-00.5)
â”‚   â”œâ”€â”€ .env.example
â”‚   â””â”€â”€ tests/
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ src/App.tsx          # Interfaz principal
â”‚   â””â”€â”€ package.json
â”œâ”€â”€ docs/
â””â”€â”€ README.md
```

---

## 3. Backend

### 3.1 MÃ³dulos principales

- `app/main.py`: instancia FastAPI y endpoints; valida sesiÃ³n y deriva `usuario_id` de la cookie.
- `app/auth.py`: usuarios, sesiones opacas en cookie HttpOnly, PBKDF2-HMAC-SHA256 (210 000 iteraciones), SQLite.
- `app/historial.py`: inserta y lista anÃ¡lisis por `usuario_id`; ordena por `fecha DESC, id DESC`.
- `app/extraccion.py`: valida formato/tamaÃ±o y extrae texto de PDF (pypdf) y DOCX (python-docx); no devuelve texto parcial.
- `app/clasificacion.py`: clasificaciÃ³n local determinista del tipo de contrato (prestaciÃ³n de servicios o proveedor).
- `app/analisis_ia.py`: construye prompts, llama a `llama-server`, valida JSON y citas; lee `URL_SERVIDOR_IA` y `LIMITE_CONTEXTO_IA`.
- `app/citas.py`: normaliza y verifica que las citas existan literalmente en el texto.

### 3.2 Endpoints de la API

- `GET /salud` â€” comprobaciÃ³n pÃºblica del servicio.
- `POST /login` â€” inicia sesiÃ³n con `usuario` y `contrasena`.
- `POST /logout` â€” cierra la sesiÃ³n actual (requiere sesiÃ³n).
- `GET /yo` â€” devuelve el usuario de la sesiÃ³n (requiere sesiÃ³n).
- `POST /extraer` â€” recibe un PDF o DOCX y devuelve el texto extraÃ­do (requiere sesiÃ³n).
- `POST /clasificar` â€” propone el tipo de contrato del texto extraÃ­do (requiere sesiÃ³n).
- `POST /analizar-con-ia` â€” analiza clÃ¡usulas con IA local (requiere sesiÃ³n y tipo confirmado).
- `GET /analizar-con-ia/estado` â€” ocupaciÃ³n del anÃ¡lisis local (requiere sesiÃ³n).
- `GET /historial` â€” devuelve los anÃ¡lisis del usuario autenticado (requiere sesiÃ³n).

### 3.3 Variables de entorno

- `MOTORREVISIONLEGAL_DB`: ruta SQLite (por defecto `backend/datos.db`).
- `URL_SERVIDOR_IA`: URL del servidor local; solo se aceptan hosts `127.0.0.1` o `localhost` (por defecto `http://127.0.0.1:9931`).
- `LIMITE_CONTEXTO_IA`: entero positivo (por defecto `2048`).

El proyecto no carga `.env` automÃ¡ticamente; las variables deben estar en el entorno.

### 3.4 EjecuciÃ³n de pruebas

Desde la raÃ­z del repositorio:

```
.venv\Scripts\python.exe -m pytest backend
```

Ãšltima colecciÃ³n verificada: 102 pruebas (`test_analisis_ia` 29, `test_api` 10, `test_auth` 17, `test_citas` 28, `test_extraccion` 14, `test_historial` 4).

---

### 3.5 Base de datos

SQLite con tablas `usuarios`, `sesiones` y `analisis`. La tabla `analisis` almacena `usuario_id`, `fecha`, `tipo_confirmado`, `num_hallazgos` y `hallazgos` (JSON). El filtrado por usuario se realiza en SQL con parÃ¡metro. No se guardan contrato, prompt ni archivo original.

---

## 4. Frontend

### 4.1 Componentes principales

La interfaz principal estÃ¡ en `frontend/src/App.tsx` (componente Ãºnico). Gestiona sesiÃ³n, navegaciÃ³n (`inicio`, `analizar`, `resultados`, `historial`), tema claro/oscuro (persistido en `localStorage`), carga/extracciÃ³n, clasificaciÃ³n, anÃ¡lisis y visualizaciÃ³n del historial.

### 4.2 ComunicaciÃ³n con el backend

El frontend llama a rutas relativas (`/login`, `/yo`, `/extraer`, `/clasificar`, `/analizar-con-ia`, `/analizar-con-ia/estado`, `/historial`, `/logout`). El servidor de desarrollo de Vite redirige al backend; no se requiere CORS en desarrollo.

---

## 5. IntegraciÃ³n con la API de IA

- `analisis_ia.py` lee `URL_SERVIDOR_IA` y `LIMITE_CONTEXTO_IA`.
- Construye mensajes con criterios base y criterios condicionales segÃºn el tipo confirmado.
- Llama a `llama-server` en loopback (`/v1/chat/completions`), con endpoints auxiliares (`/slots`, `/tokenize`).
- Parsea la respuesta JSON del modelo y convierte cada hallazgo.
- `citas.py` valida que la cita exista literalmente en el texto; los hallazgos con citas inventadas se descartan.
- No se envÃ­a texto a servicios externos.

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

No se ha verificado un despliegue de producciÃ³n ni la validaciÃ³n completa del contexto de 4096 tokens.

---

## 7. Decisiones tÃ©cnicas

- Sesiones con token opaco en cookie HttpOnly; solo se guarda el hash del token.
- Sin registro pÃºblico; las cuentas se crean localmente.
- No se guardan archivos originales ni texto de contratos en logs.
- La extracciÃ³n no devuelve texto parcial ante fallos.
- Las citas se validan literalmente contra el documento.

---

## 8. Problemas conocidos y deuda tÃ©cnica

- El manual de despliegue de producciÃ³n no estÃ¡ verificado.
- La validaciÃ³n end-to-end del contexto de 4096 tokens en `llama-server` no se completÃ³ (solo arranque).
- El frontend concentra toda la interfaz en un Ãºnico componente (`App.tsx`).
- La secciÃ³n **Resultados** de la navegaciÃ³n no muestra aÃºn un informe separado del anÃ¡lisis reciente.

---

*Manual tÃ©cnico completado con base en el cÃ³digo y la documentaciÃ³n verificados.*
