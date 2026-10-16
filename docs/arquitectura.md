# Arquitectura del Sistema

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.2 — Alineación con PRD v0.2 y requisitos v0.2  
**Estado:** Propuesta sujeta a validación — el código no existe todavía

---

## 1. Visión general

La aplicación sigue una arquitectura cliente-servidor. El frontend web se comunica con el backend a través de una API REST. El backend coordina la extracción de texto, la clasificación, el análisis con IA y la persistencia del historial. El acceso está protegido por autenticación; solo los usuarios con cuenta autorizada pueden usar la herramienta.

```
┌──────────────────────────────────────────────┐
│               FRONTEND WEB                   │
│         React + TypeScript (candidato)        │
│         Tailwind CSS (candidato)              │
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
│         Python + FastAPI (candidato)          │
│                                               │
│  - Verificación de credenciales               │
│  - Recepción del archivo                      │
│  - Extracción de texto                        │
│    (fallo o incompleto → detención,           │
│     sin hallazgos parciales)                  │
│  - Clasificación del tipo de contrato          │
│    (determinista y local, sin IA)             │
│  - Orquestación del análisis con IA           │
│  - Validación de citas                        │
│  - Construcción del informe                   │
│  - Registro y consulta del historial          │
│  - Gestión de sesión activa                   │
└───────────┬───────────────────┬──────────────┘
            │                   │
            ▼                   ▼
┌───────────────────┐  ┌─────────────────────────┐
│   BASE DE DATOS   │  │     SERVICIO DE IA       │
│   *(pendiente)*   │  │     *(pendiente)*        │
│                   │  │                          │
│  - Cuentas de     │  │  Propone clasificación   │
│  │    análisis       │  │                          │
│    usuario        │  │  y analiza el texto.     │
│  - Historial de   │  │  No se envía texto a     │
│    análisis       │  │  servicios externos sin  │
│  - Informes       │  │  autorización expresa.   │
│    anteriores     │  │                          │
│                   │  │  Candidato: API de       │
│  Candidato:       │  │  OpenAI u otra.          │
│  PostgreSQL       │  │  Pendiente de validar:   │
│  u otro motor     │  │  privacidad, costo,      │
│                   │  │  políticas.              │
└───────────────────┘  └─────────────────────────┘
```

> **Nota:** Las tecnologías mostradas son candidatas, no decisiones confirmadas. Ninguna está instalada ni verificada todavía.
>
> **Decisión de alcance (RF-03):** la clasificación del tipo de contrato es determinista y local, basada en señales textuales explicables del propio documento. No usa IA ni envía el contrato a terceros. La IA externa queda pendiente de proveedor y autorización explícita; su bloque en el diagrama cubre solo el análisis (RF-04).

---

## 2. Componentes y responsabilidades

### 2.1 Frontend

**Tecnología candidata:** React + TypeScript con Tailwind CSS  
**Estado:** Pendiente de confirmar

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

**Tecnología candidata:** Python + FastAPI  
**Estado:** Pendiente de confirmar

| Responsabilidad | Descripción |
|---|---|
| Verificación de credenciales | Valida usuario y contraseña contra las cuentas almacenadas. Rechaza el acceso si no coinciden; devuelve error genérico. |
| Gestión de sesión activa | Mantiene y valida la sesión del usuario autenticado. El mecanismo técnico (sesiones, tokens u otro) está pendiente de definir. |
| Recepción del archivo | Endpoint para recibir el archivo cargado desde el frontend. |
| Extracción de texto | Procesa el archivo (PDF o DOCX) y extrae el texto. Si la extracción falla o resulta incompleta, notifica al frontend y detiene el flujo sin generar hallazgos. |
| Clasificación del tipo de contrato | Determina localmente y de forma determinista el tipo de contrato (prestación de servicios o proveedor) con una justificación breve basada en reglas del texto, sin usar IA ni enviar texto a terceros. |
| Orquestación del análisis | Con el tipo confirmado por el usuario, selecciona la lista de verificación y criterios correspondientes, y coordina la llamada al servicio de IA. |
| Validación de citas | Verifica que cada cita generada por la IA exista literalmente en el texto extraído antes de incluirla en el informe. |
| Construcción del informe | Estructura los hallazgos verificados con citas, explicaciones, consecuencias, recomendaciones y limitaciones. |
| Registro del historial | Guarda un registro del análisis completado asociado al usuario autenticado. No guarda el archivo original del contrato. Los campos exactos están pendientes de definir. |
| Consulta del historial | Devuelve al frontend la lista de análisis del usuario autenticado y el contenido de un análisis anterior solicitado. Nunca devuelve análisis de otro usuario. |
| Exposición de endpoints | Define las rutas de la API consumidas por el frontend. |

---

### 2.3 Servicio de IA

**Tecnología candidata:** API de OpenAI u otra  
**Estado:** Pendiente de validar — privacidad, costo, políticas institucionales

| Responsabilidad | Descripción |
|---|---|
| Propuesta de clasificación | (No aplicable en RF-03) La clasificación del tipo de contrato se realiza localmente y de forma determinista en el backend, sin usar el servicio de IA. |
| Análisis semántico | Identifica posibles ambigüedades, omisiones, contradicciones aparentes y riesgos a partir del texto y la lista de verificación. |
| Generación de hallazgos estructurados | Produce los hallazgos en el formato esperado por el backend para su validación y construcción del informe. |

> ⚠️ **Restricción de privacidad:** El texto de los contratos **no debe enviarse a servicios externos de IA** sin que la organización receptora haya autorizado expresamente ese proveedor y validado su política de privacidad. No se puede asumir que los contratos pueden transmitirse a terceros. Esta decisión debe resolverse antes de implementar el módulo de análisis.

---

### 2.4 Base de datos

**Tecnología candidata:** PostgreSQL u otro motor  
**Estado:** Pendiente de definir — motor, esquema y política de conservación

| Responsabilidad | Descripción |
|---|---|
| Almacenamiento de cuentas | Guarda las credenciales y datos de los usuarios autorizados. |
| Historial de análisis | Asocia cada análisis completado al usuario que lo realizó y almacena el informe para consulta posterior. El archivo original del contrato no se guarda. |

> **Decisiones pendientes:** motor de base de datos, campos exactos que se guardarán por análisis, política de conservación y eliminación de datos, y esquema completo. El historial está en el alcance del MVP; estos detalles deben resolverse antes de implementar ese módulo.

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

## 4. Tecnologías propuestas y decisiones pendientes

| Componente | Tecnología candidata | Estado |
|---|---|---|
| Frontend | React + TypeScript | Pendiente de confirmar |
| Estilos | Tailwind CSS | Pendiente de confirmar |
| Almacenamiento de preferencia de tema | localStorage del navegador | Pendiente de confirmar |
| Backend | Python + FastAPI | Pendiente de confirmar |
| Extracción PDF | pdfplumber, PyMuPDF u otra librería Python | Pendiente de evaluar y comparar |
| Extracción DOCX | python-docx u otra | Pendiente de confirmar |
| IA / LLM | API de OpenAI u otra — requiere validación de privacidad y políticas | Pendiente |
| Mecanismo de autenticación | Sesiones, JWT u otro | Pendiente de definir |
| Base de datos | PostgreSQL u otro motor | Pendiente de definir |
| ORM (si aplica) | SQLAlchemy u otro | Pendiente |
| Pruebas backend | pytest | Pendiente de confirmar |
| Despliegue | Por definir | Pendiente |

---

## 5. Consideraciones de privacidad y manejo de documentos

1. **Transmisión a terceros:** El texto de los contratos no debe enviarse a APIs de IA externas sin autorización expresa de la organización receptora y validación de la política de privacidad del proveedor. No se puede asumir que los contratos pueden transmitirse a servicios externos.

2. **Archivo original del contrato:** El archivo subido por el usuario no se guarda en el historial ni forma parte de los datos persistentes. La forma en que se maneja temporalmente durante el procesamiento y el momento en que se elimina están pendientes de definir.

3. **Historial e informes:** El historial guarda el informe de resultados asociado al usuario. Los campos exactos, la política de conservación y el motor de base de datos están pendientes de definir.

4. **Aislamiento de datos por usuario:** El backend debe garantizar que un usuario autenticado solo pueda consultar sus propios análisis. Nunca debe devolver análisis de otro usuario.

5. **Logs:** El contenido de los contratos no debe registrarse en logs de texto plano para evitar exposición accidental de información sensible.

6. **Cifrado en tránsito:** La comunicación entre el cliente y el servidor debe realizarse sobre HTTPS en el entorno de producción.

7. **Confidencialidad de las partes:** Los contratos pueden contener datos personales o información confidencial. El diseño del sistema debe considerarlo desde el inicio.

---

## 6. Aspectos de arquitectura pendientes de definir

- [ ] Selección y validación del proveedor de IA: privacidad, costo, políticas institucionales. **Prerrequisito para implementar el módulo de análisis.**
- [ ] Mecanismo técnico de autenticación (sesiones, JWT u otro).
- [ ] Creación y administración de cuentas autorizadas: quién las crea, cómo y con qué herramienta.
- [ ] Motor de base de datos para historial y cuentas de usuario.
- [ ] Campos exactos que se guardarán por cada análisis en el historial y política de conservación.
- [ ] Política de almacenamiento y eliminación del documento cargado tras la extracción.
- [ ] Estrategia de despliegue (nube, servidor local, contenedores).
- [ ] Estrategia de manejo de errores y reintentos ante fallos del servicio de IA.
- [ ] Tamaño máximo de archivo aceptado y su validación en frontend y backend.

---

*Este documento es una propuesta inicial sujeta a revisión y validación.*
