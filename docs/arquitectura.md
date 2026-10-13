# Arquitectura del Sistema

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.1 — Borrador inicial  
**Estado:** Propuesta sujeta a validación — el código no existe todavía

---

## 1. Visión general

La aplicación sigue una arquitectura cliente-servidor de tres capas:

```
┌────────────────────────────────┐
│         FRONTEND WEB           │
│    React + TypeScript          │
│    Tailwind CSS                │
│                                │
│  - Carga de archivo            │
│  - Confirmación de tipo        │
│  - Visualización del informe   │
└──────────────┬─────────────────┘
               │ HTTP / REST (HTTPS en producción)
               ▼
┌────────────────────────────────┐
│         BACKEND (API)          │
│    Python + FastAPI            │
│                                │
│  - Recepción del archivo       │
│  - Extracción de texto         │
│  - Orquestación del análisis   │
│  - Construcción del informe    │
└──────────┬────────────────┬────┘
           │                │
           ▼                ▼
┌──────────────────┐  ┌───────────────────────┐
│  Almacenamiento  │  │   Servicio de IA       │
│  *(pendiente)*   │  │   (API externa)        │
│  PostgreSQL      │  │   *(pendiente)*        │
│  u otro          │  │   p. ej. OpenAI        │
└──────────────────┘  └───────────────────────┘
```

> **Nota:** Tanto la base de datos como la API de IA son opciones candidatas, no decisiones definitivas.

---

## 2. Componentes y responsabilidades

### 2.1 Frontend

**Tecnología candidata:** React + TypeScript con Tailwind CSS  
**Estado:** Pendiente de confirmar

| Responsabilidad | Descripción |
|---|---|
| Carga de archivo | Proporciona una interfaz para que el usuario seleccione o arrastre un archivo PDF o DOCX. |
| Confirmación de clasificación | Muestra la clasificación propuesta por el backend y permite al usuario confirmarla o corregirla. |
| Visualización del informe | Renderiza los hallazgos con citas, explicaciones, consecuencias, recomendaciones y limitaciones. |
| Avisos de uso | Muestra el aviso de que el informe no constituye asesoría jurídica. |
| Manejo de errores | Informa al usuario en casos de archivo no soportado, extracción incompleta o error de red. |

---

### 2.2 Backend

**Tecnología candidata:** Python + FastAPI  
**Estado:** Pendiente de confirmar

| Responsabilidad | Descripción |
|---|---|
| Recepción del archivo | Endpoint para recibir el archivo cargado por el frontend. |
| Extracción de texto | Procesa el archivo (PDF o DOCX) y extrae el texto. Notifica si la extracción es incompleta. |
| Clasificación del tipo de contrato | Analiza el texto y propone el tipo de contrato. |
| Orquestación del análisis | Selecciona la lista de verificación y los criterios según el tipo confirmado; coordina la llamada a la API de IA. |
| Construcción del informe | Estructura los hallazgos con citas textuales verificadas, explicaciones y recomendaciones. |
| Validación de citas | Verifica que cada cita generada exista en el texto extraído antes de incluirla en el informe. |
| Exposición de endpoints | Define las rutas de la API consumidas por el frontend. |

---

### 2.3 Servicio de IA

**Tecnología candidata:** API de OpenAI u otra  
**Estado:** Pendiente de validar — privacidad, costo, políticas institucionales

| Responsabilidad | Descripción |
|---|---|
| Análisis semántico del texto | Identifica ambigüedades, omisiones, contradicciones y riesgos a partir del texto del contrato y la lista de verificación. |
| Generación de hallazgos estructurados | Produce los hallazgos en el formato esperado por el backend. |

> **Consideración de privacidad:** Si se usa una API de terceros, el texto del contrato se enviará a servidores externos. Esto requiere validación con la organización receptora antes de elegir el proveedor. Se debe evaluar si existe una opción que permita procesamiento local o en una nube privada.

---

### 2.4 Almacenamiento

**Tecnología candidata:** PostgreSQL  
**Estado:** Pendiente de validar — depende de si se requiere persistencia

| Escenario | Implicación |
|---|---|
| Procesamiento por sesión (sin persistencia) | No se necesita base de datos; el archivo se procesa y descarta. Más sencillo y privado. |
| Historial de análisis | Requiere almacenamiento persistente para asociar documentos, usuarios e informes. |

> **Decisión pendiente:** Definir si el MVP requiere persistencia o si opera completamente por sesión.

---

## 3. Flujo general del sistema

```
Usuario
  │
  │ 1. Carga el archivo (PDF / DOCX)
  ▼
Frontend
  │
  │ 2. Envía el archivo al backend (POST /analizar)
  ▼
Backend — Módulo de extracción
  │
  │ 3. Extrae el texto del documento
  │    Si falla o es incompleto → notifica al usuario y detiene (o advierte)
  ▼
Backend — Módulo de clasificación
  │
  │ 4. Propone el tipo de contrato
  │
  │ 5. Devuelve la propuesta al frontend
  ▼
Frontend
  │
  │ 6. Muestra la clasificación al usuario
  │    El usuario confirma o corrige
  │
  │ 7. Envía la clasificación confirmada al backend (POST /confirmar-tipo)
  ▼
Backend — Módulo de orquestación
  │
  │ 8. Selecciona la lista de verificación y criterios según el tipo
  │
  │ 9. Llama a la API de IA con el texto y los criterios
  ▼
Servicio de IA
  │
  │ 10. Devuelve hallazgos en formato estructurado
  ▼
Backend — Módulo de validación y construcción del informe
  │
  │ 11. Verifica que las citas existan en el texto original
  │ 12. Construye el informe estructurado
  │ 13. Devuelve el informe al frontend
  ▼
Frontend
  │
  │ 14. Renderiza el informe al usuario
  ▼
Usuario
     Revisa hallazgos con criterio propio
```

---

## 4. Tecnologías propuestas y decisiones pendientes

| Componente | Tecnología candidata | Decisión |
|---|---|---|
| Frontend | React + TypeScript | Pendiente de confirmar |
| Estilos | Tailwind CSS | Pendiente de confirmar |
| Backend | Python + FastAPI | Pendiente de confirmar |
| Extracción PDF | pdfplumber, PyMuPDF u otra librería Python | Pendiente de evaluar y comparar |
| Extracción DOCX | python-docx u otra | Pendiente de confirmar |
| IA / LLM | API de OpenAI, API local, otra | Pendiente — requiere validación de privacidad y costos |
| Base de datos | PostgreSQL | Pendiente — depende de si se requiere persistencia |
| ORM (si aplica) | SQLAlchemy u otro | Pendiente |
| Pruebas backend | pytest | Pendiente de confirmar |
| Despliegue | Por definir | Pendiente |

---

## 5. Consideraciones de privacidad y manejo de documentos

1. **Transmisión a terceros:** Si se usa una API de IA externa (p. ej. OpenAI), el texto del contrato se envía a servidores fuera del control de la organización. Esto debe ser evaluado y autorizado antes de seleccionar el proveedor.

2. **Almacenamiento temporal:** Los archivos cargados deben eliminarse del servidor después del análisis, a menos que el usuario haya consentido explícitamente en su almacenamiento.

3. **Retención de datos:** La política de retención de documentos analizados debe definirse junto con la organización receptora.

4. **Logs:** El contenido de los contratos no debe registrarse en logs de texto plano para evitar exposición accidental de información sensible.

5. **Cifrado en tránsito:** La comunicación entre el cliente y el servidor debe realizarse sobre HTTPS en entornos de producción.

6. **Confidencialidad de las partes:** Los contratos pueden contener datos personales o información confidencial. El diseño del sistema debe tomar esto en cuenta desde el inicio.

---

## 6. Aspectos de arquitectura pendientes de definir

- [ ] Estrategia de despliegue (nube, servidor local, contenedores).
- [ ] Mecanismo de autenticación de usuarios (si aplica en el MVP).
- [ ] Decisión sobre persistencia y base de datos.
- [ ] Selección y validación del proveedor de IA.
- [ ] Definición de la política de almacenamiento y eliminación de documentos.
- [ ] Estrategia de manejo de errores y reintentos con la API de IA.
- [ ] Límites de tamaño de archivo y de texto procesado.

---

*Este documento es una propuesta inicial sujeta a revisión y validación.*
