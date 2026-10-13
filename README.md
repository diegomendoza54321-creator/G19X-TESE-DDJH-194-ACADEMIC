# MotorRevisionLegal

Motor de revisión inteligente de cláusulas legales — Proyecto de Residencias Profesionales.

---

## Descripción

MotorRevisionLegal es una herramienta en español que apoya la revisión de contratos de prestación de servicios y contratos de proveedores. Analiza el documento cargado, propone su clasificación, aplica una lista de verificación y genera hallazgos textuales que el usuario puede revisar con criterio profesional propio.

**La herramienta no garantiza la legalidad de un contrato ni sustituye el criterio de un profesional jurídico.**

---

## Funciones previstas

- Cargar contratos en formato PDF (con texto seleccionable) y DOCX.
- Proponer el tipo de contrato y sus características.
- Permitir que el usuario confirme o corrija la clasificación antes de aplicar criterios.
- Aplicar una lista de verificación base y criterios condicionales según el tipo de contrato.
- Identificar posibles ambigüedades, omisiones, contradicciones aparentes y riesgos contractuales potenciales.
- Generar hallazgos respaldados por citas textuales del documento original.
- Presentar para cada hallazgo: explicación, posible consecuencia, recomendación y limitaciones del análisis.
- Facilitar la revisión humana sin reemplazar al profesional jurídico.

### Limitaciones conocidas

- No inventa citas, cláusulas, obligaciones ni datos que no estén en el documento.
- No determina la validez legal ni la ejecutabilidad de ningún contrato.
- El alcance inicial se limita a contratos de prestación de servicios y de proveedores en español.
- El análisis depende de la calidad del texto del documento. Esta versión requiere archivos PDF con texto seleccionable; los PDF escaneados (sin capa de texto) no están soportados y no deben procesarse como si hubieran sido leídos correctamente.

---

## Estado del proyecto

> **Fase actual:** Documentación inicial — el código de la aplicación no existe todavía.

---

## Tecnologías

### Candidatas (pendientes de validar)

| Componente | Tecnología candidata | Estado |
|---|---|---|
| Backend | Python + FastAPI | Pendiente de confirmar |
| Frontend | React + TypeScript | Pendiente de confirmar |
| Estilos | Tailwind CSS | Pendiente de confirmar |
| Base de datos | PostgreSQL | Pendiente de validar necesidad y alcance |
| IA / LLM | API de OpenAI u otra | Pendiente — requiere validación de privacidad, costo y políticas |
| Control de versiones | Git + GitHub | En uso |
| Pruebas backend | pytest | Pendiente de confirmar |

> Ninguna de estas tecnologías está instalada ni verificada todavía. No se deben asumir como definitivas.

### Decisiones pendientes

- [ ] Selección y validación de la API de IA (privacidad, costo, políticas institucionales/empresariales).
- [ ] Definir si se requiere base de datos persistente o si el procesamiento será por sesión.
- [ ] Confirmar si el frontend será una SPA o si existirá una integración dentro de otra plataforma.
- [ ] Establecer política de retención de documentos cargados por usuarios.

---

## Requisitos previos

> Esta sección se completará una vez que se definan y verifiquen las tecnologías definitivas.
> **No instalar dependencias basándose en esta lista hasta que esté confirmada.**

*(pendiente)*

---

## Estructura del proyecto

> La estructura se definirá al iniciar la fase de implementación.
> A continuación se muestra una propuesta preliminar sujeta a cambios.

```
MotorRevisionLegal/
├── backend/          # API y lógica de análisis (Python / FastAPI)
├── frontend/         # Interfaz de usuario (React / TypeScript)
├── docs/             # Documentación del proyecto
│   ├── PRD.md
│   ├── requisitos.md
│   ├── arquitectura.md
│   ├── plan-de-pruebas.md
│   ├── bitacora.md
│   ├── entregables.md
│   ├── guia-instalacion.md     (pendiente)
│   ├── manual-usuario.md       (pendiente)
│   └── manual-tecnico.md       (pendiente)
├── tests/            # Pruebas automatizadas (pytest)
├── .gitignore
└── README.md
```

---

## Instalación y ejecución

> **Pendiente.** Las instrucciones de instalación y ejecución se documentarán en [`docs/guia-instalacion.md`](docs/guia-instalacion.md) únicamente cuando hayan sido verificadas durante el desarrollo.
>
> No ejecutar comandos de instalación hasta contar con esa guía validada.

---

## Documentación complementaria

| Documento | Descripción |
|---|---|
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

## Notas de residencia profesional

Este proyecto se desarrolla como parte de un programa de residencias profesionales. Los entregables académicos requeridos se describen en [`docs/entregables.md`](docs/entregables.md).

---

*Última actualización de este documento: fase de documentación inicial.*
