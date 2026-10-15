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
- Aplicar una lista de verificación base y criterios condicionales según el tipo confirmado.
- Identificar posibles ambigüedades, omisiones, contradicciones aparentes y riesgos contractuales.
- Generar hallazgos respaldados por citas textuales del documento original.
- Presentar por cada hallazgo: explicación, posible consecuencia, recomendación y limitaciones del análisis.
- Mostrar el informe en pantalla. Las categorías sin hallazgos se ocultan; si no hay ninguno, se indica que no se identificaron hallazgos con los criterios aplicados.
- Consultar análisis anteriores desde la sección **Historial**. Cada usuario ve únicamente los suyos.
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

> **Fase actual:** Documentación en elaboración — el código de la aplicación no existe todavía.

La documentación de requisitos, arquitectura y alcance del MVP está disponible en la carpeta `docs/`. La implementación no ha comenzado.

---

## Tecnologías

### Candidatas (pendientes de validar)

Ninguna tecnología está instalada ni confirmada. No deben asumirse como definitivas.

| Componente | Tecnología candidata | Estado |
|---|---|---|
| Backend | Python + FastAPI | Pendiente de confirmar |
| Frontend | React + TypeScript | Pendiente de confirmar |
| Estilos | Tailwind CSS | Pendiente de confirmar |
| Base de datos | PostgreSQL u otro | Pendiente de definir |
| IA / LLM | API de OpenAI u otra | Pendiente — requiere validación de privacidad, costo y políticas |
| Autenticación | Por definir (sesiones, JWT u otro) | Pendiente |
| Control de versiones | Git + GitHub | En uso |
| Pruebas backend | pytest | Pendiente de confirmar |

### Decisiones pendientes

- [ ] Proveedor de IA: privacidad, costo, políticas. El texto de los contratos no debe enviarse a servicios externos sin autorización expresa.
- [ ] Mecanismo técnico de autenticación.
- [ ] Creación y administración de cuentas autorizadas.
- [ ] Motor de base de datos para historial y cuentas.
- [ ] Campos exactos del historial y política de conservación de esos datos.
- [ ] Manejo temporal del archivo cargado durante el procesamiento y momento de eliminación.
- [ ] Validación jurídica de la lista de criterios de revisión (prerrequisito para implementar el módulo de análisis).
- [ ] Tamaño máximo de archivo aceptado.
- [ ] Estrategia de despliegue.

---

## Requisitos previos e instalación rápida

> **Pendiente — no usar hasta que esté verificado.**
>
> Las tecnologías, dependencias y comandos reales se documentarán una vez que estén confirmados y verificados en un entorno limpio. No instalar dependencias ni ejecutar comandos basándose en esta sección.
>
> Para el **ingeniero evaluador**: cuando el sistema esté listo, aquí aparecerán los requisitos mínimos (versiones exactas de Python, Node.js y demás dependencias) y los pasos resumidos de instalación y ejecución. La guía detallada y verificada estará en [`docs/guia-instalacion.md`](docs/guia-instalacion.md).

*(pendiente)*

---

## Estructura del proyecto

> Propuesta preliminar sujeta a cambios al iniciar la implementación.

```
MotorRevisionLegal/
├── backend/           # API y lógica de análisis (Python / FastAPI)
├── frontend/          # Interfaz de usuario (React / TypeScript)
├── docs/              # Documentación del proyecto
│   ├── MVP.md
│   ├── PRD.md
│   ├── requisitos.md
│   ├── arquitectura.md
│   ├── plan-de-pruebas.md
│   ├── bitacora.md
│   ├── entregables.md
│   ├── guia-instalacion.md    (pendiente)
│   ├── manual-usuario.md      (pendiente)
│   └── manual-tecnico.md      (pendiente)
├── tests/             # Pruebas automatizadas (pytest)
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
| [docs/guia-instalacion.md](docs/guia-instalacion.md) | Guía de instalación *(pendiente)* |
| [docs/manual-usuario.md](docs/manual-usuario.md) | Manual de usuario *(pendiente)* |
| [docs/manual-tecnico.md](docs/manual-tecnico.md) | Manual técnico *(pendiente)* |

---

## Residencias profesionales

Este proyecto se desarrolla como parte de un programa de residencias profesionales. Los entregables académicos requeridos y su estado actual se describen en [`docs/entregables.md`](docs/entregables.md).

---

*Última actualización: alineación con PRD v0.2, requisitos v0.2, MVP v0.2 y arquitectura v0.2.*
