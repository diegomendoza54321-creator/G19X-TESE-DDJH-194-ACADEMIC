# Arquitectura del Sistema

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.2 — Alineación con PRD v0.2 y requisitos v0.2  
**Estado:** Implementada y validada (prototipo funcional completo)

---

## 1. Visión general

La aplicación sigue una arquitectura cliente-servidor. El frontend web se comunica con el backend a través de una API REST. El backend coordina la extracción de texto, la clasificación, el análisis con IA local y la persistencia del historial. El acceso está protegido por autenticación; solo los usuarios con cuenta autorizada pueden usar la herramienta.

```
┌──────────────────────────────────────────────┐
│               FRONTEND WEB                   │
│         React + TypeScript (confirmado)       │
│         Tailwind CSS (confirmado)             │
│                                               │
│  - Pantalla de inicio de sesión               │
│  - Navegación: Inicio, Analizar contrato,     │
│    Resultados, Historial                      │
│    (+ Cómo funciona y Criterios opcionales)   │
│  - Tema claro / oscuro (preferencia en        │
│    localStorage del navegador)                │
│  - Carga de archivo                           │
│  - Confirmación / corrección del tipo         │
│  - Visualización del informe                  │
│  - Consulta del historial propio              │
└───────────────────┬──────────────────────────┘
                    │ HTTPS / REST
                    ▼
┌──────────────────────────────────────────────┐
│               BACKEND (API)                  │
│         Python + FastAPI (confirmado)         │
│                                               │
│  - Verificación de credenciales               │
│  - Recepción del archivo                      │
│  - Extracción de texto                        │
│    (fallo o incompleto → detención,           │
│     sin hallazgos parciales)                  │
│  - Clasificación del tipo de contrato          │
│    (determinista y local, sin IA)             │
│  - Orquestación del análisis con IA local     │
│  - Validación de citas                        │
│  - Construcción del informe                   │
│  - Registro y consulta del historial          │
│  - Gestión de sesión activa                   │
└───────────┬───────────────────┬──────────────┘
            │                   │
            ▼                   ▼
┌───────────────────┐  ┌─────────────────────────┐
│   BASE DE DATOS   │  │     SERVICIO DE IA       │
│   SQLite (confirmado)│  │     llama-server local │
│                   │  │     (confirmado)         │
│  - Cuentas de     │  │                          │
│    usuario        │  │  Analiza el texto con    │
│  - Historial de   │  │  modelo Phi-3 GGUF.      │
│    análisis       │  │  No se envía texto a     │
│  - Informes       │  │  servicios externos.     │
│    anteriores     │  │                          │
└───────────────────┘  └─────────────────────────┘
```

> **Nota:** Las tecnologías mostradas están confirmadas e implementadas.
>
> **Decisión de alcance (RF-03):** la clasificación del tipo de contrato es determinista y local, basada en señales textuales explicables del propio documento. No usa IA ni envía el contrato a terceros. El análisis (RF-04) usa `llama-server` local con modelo Phi-3 GGUF en `127.0.0.1:9931`.

---

## 2. Componentes y responsabilidades

### 2.1 Frontend

**Tecnología confirmada:** React + TypeScript con Tailwind CSS  
**Estado:** Implementado y validado

| Responsabilidad | Descripción |
|---|---|
| Pantalla de inicio de sesión | Solicita nombre de usuario y contraseña. No ofrece registro público. Muestra error genérico ante credenciales incorrectas. |
| Navegación principal | Expone las secciones: Inicio, Analizar contrato, Resultados e Historial. Cómo funciona y Criterios pueden incluirse. |
| Tema claro / oscuro | Permite cambiar el tema. Guarda la preferencia en el almacenamiento local del navegador y la aplica en visitas posteriores sin interrumpir la sesión. |
| Carga de archivo | Permite seleccionar o arrastrar un archivo PDF o DOCX. |
| Confirmación de clasificación | Muestra la clasificación propuesta por el backend con su justificación. El usuario la confirma o selecciona el otro tipo antes de continuar. |
| Visualización del informe | Renderiza los hallazgos con citas, explicaciones, consecuencias, recomendaciones y limitaciones. Muestra solo las categorías con hallazgos; si no hay ninguno, muestra el mensaje general acordado. |
| Avisos de uso | Muestra el aviso visible de que el informe no constituye asesoría jurídica. |
| Consulta del historial | Presenta la lista de análisis anteriores del usuario autenticado. Permite abrir un informe previo. No expone ni ofrece descargar el archivo original del contrato. |
| Manejo de errores | Informa al usuario ante archivo no soportado, extracción fallida, error de red u otras condiciones de error. |

---

### 2.2 Backend

**Tecnología confirmada:** Python + FastAPI  
**Estado:** Implementado y validado

| Responsabilidad | Descripción |
|---|---|
| Verificación de credenciales | Valida usuario y contraseña contra las cuentas almacenadas. Rechaza el acceso si no coinciden; devuelve error genérico. |
| Gestión de sesión activa | Mantiene y valida la sesión del usuario autenticado mediante **token opaco en cookie HttpOnly con hash PBKDF2** (implementado en `auth.py`). |
| Recepción del archivo | Endpoint para recibir el archivo cargado desde el frontend. |
| Extracción de texto | Procesa el archivo (PDF o DOCX) y extrae el texto. Si la extracción falla o resulta incompleta, notifica al frontend y detiene el flujo sin generar hallazgos. |
| Clasificación del tipo de contrato | Determina localmente y de forma determinista el tipo de contrato (prestación de servicios o proveedor) con una justificación breve basada en reglas del texto, sin usar IA ni enviar texto a terceros. |
| Orquestación del análisis | Con el tipo confirmado por el usuario, selecciona la lista de verificación y criterios correspondientes, y coordina la llamada a `llama-server` local. |
| Validación de citas | Verifica que cada cita generada por la IA exista literalmente en el texto extraído antes de incluirla en el informe. |
| Construcción del informe | Estructura los hallazgos verificados con citas, explicaciones, consecuencias, recomendaciones y limitaciones. |
| Registro del historial | Guarda un registro del análisis completado asociado al usuario autenticado. No guarda el archivo original del contrato. Los campos están definidos en `historial.py`; la política de conservación está pendiente. |
| Consulta del historial | Devuelve al frontend la lista de análisis del usuario autenticado y el contenido de un análisis anterior solicitado. Nunca devuelve análisis de otro usuario. |
| Exposición de endpoints | Define las rutas de la API consumidas por el frontend. |

---

### 2.3 Servicio de IA

**Tecnología confirmada:** `llama-server` (llama.cpp) local con modelo Phi-3 GGUF  
**Estado:** Implementado y validado en `127.0.0.1:9931`

| Responsabilidad | Descripción |
|---|---|
| Propuesta de clasificación | (No aplicable en RF-03) La clasificación del tipo de contrato se realiza localmente y de forma determinista en el backend, sin usar el servicio de IA. |
| Análisis semántico | Identifica posibles ambigüedades, omisiones, contradicciones aparentes y riesgos a partir del texto y la lista de verificación, usando el modelo local Phi-3. |
| Generación de hallazgos estructurados | Produce los hallazgos en formato JSON Schema validado por el backend para su validación y construcción del informe. |

> ✅ **Privacidad garantizada:** El texto de los contratos **nunca se envía a servicios externos**. El análisis se ejecuta completamente en local mediante `llama-server` en loopback (`127.0.0.1:9931`), sin acceso a red externa.

---

### 2.4 Base de datos

**Tecnología confirmada:** SQLite  
**Estado:** Implementado y validado

| Responsabilidad | Descripción |
|---|---|
| Almacenamiento de cuentas | Guarda las credenciales y datos de los usuarios autorizados (tabla `usuarios`). |
| Historial de análisis | Asocia cada análisis completado al usuario que lo realizó y almacena el informe para consulta posterior (tabla `analisis`). El archivo original del contrato no se guarda. |

> **Implementado:** motor SQLite, esquema completo (`usuarios`, `sesiones`, `analisis`), campos definidos en `historial.py`. Política de conservación y eliminación de datos pendiente de definición formal.

---

## 3. Flujo general del sistema

```
Usuario
  │
  │ 1. Abre la aplicación en su navegador
  ▼
Frontend — Pantalla de inicio de sesión
  │
  │ 2. Introduce nombre de usuario y contraseña
  │    POST /auth/login
  ▼
Backend — Verificación de credenciales
  │
  │    Si las credenciales son incorrectas → error genérico. Fin del flujo.
  │
  │ 3. Sesión establecida. El usuario accede a la herramienta.
  ▼
Frontend — Pantalla de inicio / Analizar contrato
  │
  │ 4. El usuario carga un archivo PDF o DOCX
  │    POST /analizar
  ▼
Backend — Módulo de extracción
  │
  │ 5. Extrae el texto del documento
  │    Si falla o es incompleto → notifica al frontend y detiene el flujo.
  │    No se generan hallazgos.
  ▼
Backend — Módulo de clasificación local
  │
  │ 6. El módulo propone el tipo de contrato con justificación breve basada en reglas locales
  │ 7. Devuelve la propuesta al frontend
  ▼
Frontend — Confirmación del tipo
  │
  │ 8. El usuario confirma o corrige la clasificación
  │    POST /confirmar-tipo
  ▼
Backend — Módulo de orquestación  ←→  Servicio de IA
  │
  │ 9.  Selecciona la lista de verificación y criterios según el tipo
  │ 10. Llama al servicio de IA con el texto y los criterios
  │ 11. La IA devuelve hallazgos estructurados
  ▼
Backend — Validación y construcción del informe
  │
  │ 12. Verifica que cada cita exista en el texto original
  │ 13. Construye el informe estructurado
  │ 14. Registra el análisis en el historial del usuario (sin el archivo original)
  │ 15. Devuelve el informe al frontend
  ▼
Frontend — Sección Resultados
  │
  │ 16. Renderiza el informe al usuario
  ▼
Usuario
  │    Lee el informe y aplica su propio criterio
  │
  │ 17. Puede consultar el análisis posterior desde la sección Historial
  ▼
Frontend — Sección Historial
  │
  │    GET /historial  →  lista de análisis del usuario autenticado
  │    GET /historial/{id}  →  informe de un análisis anterior
  ▼
Usuario
     Consulta el informe previo
```

---

## 4. Tecnologías confirmadas e implementadas

| Componente | Tecnología | Estado |
|---|---|---|
| Frontend | React + TypeScript | **Confirmado e implementado** |
| Estilos | Tailwind CSS | **Confirmado e implementado** |
| Almacenamiento de preferencia de tema | localStorage del navegador | **Confirmado e implementado** |
| Backend | Python + FastAPI | **Confirmado e implementado** |
| Extracción PDF | pypdf | **Confirmado e implementado** |
| Extracción DOCX | python-docx | **Confirmado e implementado** |
| IA / LLM | llama-server (llama.cpp) local + Phi-3 GGUF | **Confirmado e implementado** |
| Mecanismo de autenticación | JWT + cookie HttpOnly (token opaco, PBKDF2) | **Confirmado e implementado** |
| Base de datos | SQLite | **Confirmado e implementado** |
| ORM | Sin ORM (SQL directo con sqlite3) | **Confirmado e implementado** |
| Pruebas backend | pytest + httpx + httpx2 | **Confirmado e implementado (109 tests)** |
| Despliegue | Entorno de desarrollo Windows (documentado en README) | **Parcial: demo funcional; producción pendiente** |

---

## 5. Consideraciones de privacidad y manejo de documentos

1. **Transmisión a terceros:** El texto de los contratos no se envía a APIs de IA externas. El análisis se ejecuta completamente en local mediante `llama-server` en loopback (`127.0.0.1:9931`), sin acceso a red externa.

2. **Archivo original del contrato:** El archivo subido por el usuario no se guarda en el historial ni forma parte de los datos persistentes. Se procesa en memoria y se descarta tras la extracción; el momento exacto de eliminación está pendiente de definición formal.

3. **Historial e informes:** El historial guarda el informe de resultados asociado al usuario (tabla `analisis` en SQLite). Los campos exactos están definidos en `historial.py`; la política de conservación está pendiente de definición formal.

4. **Aislamiento de datos por usuario:** El backend garantiza que un usuario autenticado solo pueda consultar sus propios análisis. Nunca devuelve análisis de otro usuario (filtrado por `usuario_id` en SQL).

5. **Logs:** El contenido de los contratos no se registra en logs de texto plano para evitar exposición accidental de información sensible.

6. **Cifrado en tránsito:** La comunicación entre el cliente y el servidor debe realizarse sobre HTTPS en el entorno de producción.

7. **Confidencialidad de las partes:** Los contratos pueden contener datos personales o información confidencial. El diseño del sistema lo considera desde el inicio.

---

## 6. Aspectos de arquitectura pendientes de definir

- [x] Selección y validación del proveedor de IA: **Resuelto — `llama-server` local (llama.cpp) con modelo Phi-3 GGUF**.
- [x] Mecanismo técnico de autenticación: **Resuelto — JWT + cookie HttpOnly (token opaco, PBKDF2)**.
- [x] Creación y administración de cuentas autorizadas: **Resuelto — script `backend/crear_usuario.py`**.
- [x] Motor de base de datos para historial y cuentas de usuario: **Resuelto — SQLite**.
- [ ] Campos exactos que se guardarán por cada análisis en el historial y política de conservación: **Parcial — campos definidos en `historial.py`; política pendiente**.
- [ ] Política de almacenamiento y eliminación del documento cargado tras la extracción: **Pendiente**.
- [ ] Estrategia de despliegue (nube, servidor local, contenedores): **Pendiente — entorno demo documentado; producción pendiente**.
- [x] Estrategia de manejo de errores y reintentos ante fallos del servicio de IA: **Resuelto — retry 503 en frontend + 503 en backend**.
- [ ] Tamaño máximo de archivo aceptado y su validación en frontend y backend: **Pendiente**.

---

*Este documento refleja la arquitectura implementada y validada; sujeto a ajustes menores por el equipo del proyecto.*
