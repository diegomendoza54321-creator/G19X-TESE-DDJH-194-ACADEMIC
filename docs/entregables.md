# Lista de Control de Entregables

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.1 — Estado inicial  
**Estado:** Lista de control creada — ningún entregable está completo todavía

---

> Esta lista de control registra el estado de cada entregable requerido por el programa de residencias profesionales. Se actualizará conforme avance el proyecto. No se afirma que un entregable está terminado si todavía no existe o no ha sido verificado.

---

## 1. Accesos de prueba

| Campo | Detalle |
|---|---|
| **Propósito** | Permitir que el evaluador o tutor acceda al sistema en funcionamiento para verificar las funciones del MVP. |
| **Contenido esperado** | URL o instrucciones de acceso al entorno de demostración; credenciales de prueba si aplica. |
| **Estado** | ⬜ No disponible — el sistema no existe todavía. |
| **Qué falta** | Implementar y desplegar el MVP; definir el entorno de demostración; generar credenciales de prueba si el sistema requiere autenticación. |

---

## 2. Bitácora

| Campo | Detalle |
|---|---|
| **Propósito** | Documentar el avance real del proyecto sesión por sesión, incluyendo problemas y soluciones encontradas. |
| **Contenido esperado** | Registro cronológico con fecha, objetivo, actividades, resultado, problemas, solución, evidencia y siguiente paso por cada sesión. |
| **Estado** | ⬜ Plantilla creada — sin entradas reales todavía. Ver [`docs/bitacora.md`](bitacora.md). |
| **Qué falta** | Registrar cada sesión de trabajo a partir de la fase de implementación. |

---

## 3. Código fuente en ZIP

| Campo | Detalle |
|---|---|
| **Propósito** | Entregar el código fuente completo del proyecto en un archivo comprimido para archivo y evaluación. |
| **Contenido esperado** | Código fuente del backend y del frontend, archivos de configuración, scripts de instalación, sin claves ni secretos. |
| **Estado** | ⬜ No disponible — el código no existe todavía. |
| **Qué falta** | Completar la implementación; preparar el archivo ZIP excluyendo secretos, entornos virtuales y dependencias descargables. |

---

## 4. Documento técnico

| Campo | Detalle |
|---|---|
| **Propósito** | Describir la arquitectura, las decisiones técnicas y el funcionamiento interno del sistema para la evaluación académica. |
| **Contenido esperado** | Descripción de la arquitectura, tecnologías utilizadas, flujo del sistema, decisiones tomadas y justificaciones. |
| **Estado** | ⬜ En elaboración — existe un borrador de arquitectura en [`docs/arquitectura.md`](arquitectura.md). |
| **Qué falta** | Completar y validar la arquitectura durante el desarrollo; consolidar en el formato requerido por la institución. |

---

## 5. Evidencias (capturas, video o demo)

| Campo | Detalle |
|---|---|
| **Propósito** | Demostrar que el sistema funciona según lo especificado, con evidencia visual verificable. |
| **Contenido esperado** | Capturas de pantalla o video del sistema en funcionamiento: carga de contrato, clasificación, confirmación, informe de hallazgos. |
| **Estado** | ⬜ No disponible — el sistema no existe todavía. |
| **Qué falta** | Implementar el MVP; capturar pantallas o grabar video durante las pruebas de aceptación. |

---

## 6. Guía de instalación

| Campo | Detalle |
|---|---|
| **Propósito** | Permitir que otra persona instale y ejecute el sistema siguiendo instrucciones verificadas paso a paso. |
| **Contenido esperado** | Requisitos previos verificados, comandos de instalación probados, configuración del entorno, solución de problemas comunes. |
| **Estado** | ⬜ Esqueleto creado como marcador — **pendiente de completar y validar**. Ver [`docs/guia-instalacion.md`](guia-instalacion.md). |
| **Qué falta** | Completar durante el desarrollo, verificar cada paso en un entorno limpio antes de considerar el documento como terminado. |

---

## 7. Manual de usuario

| Campo | Detalle |
|---|---|
| **Propósito** | Explicar al usuario final cómo usar la herramienta paso a paso, sin conocimientos técnicos. |
| **Contenido esperado** | Descripción de la interfaz, flujo de uso, interpretación del informe, limitaciones de la herramienta, preguntas frecuentes. |
| **Estado** | ⬜ Esqueleto creado como marcador — **pendiente de completar y validar**. Ver [`docs/manual-usuario.md`](manual-usuario.md). |
| **Qué falta** | Completar una vez que la interfaz esté implementada y verificada. |

---

## 8. Manual técnico

| Campo | Detalle |
|---|---|
| **Propósito** | Documentar el sistema para desarrolladores o responsables de mantenimiento. |
| **Contenido esperado** | Estructura del código, descripción de módulos, API del backend, variables de entorno, instrucciones de prueba y despliegue. |
| **Estado** | ⬜ Esqueleto creado como marcador — **pendiente de completar y validar**. Ver [`docs/manual-tecnico.md`](manual-tecnico.md). |
| **Qué falta** | Completar conforme avance la implementación; documentar decisiones técnicas reales, no supuestas. |

---

## 9. MVP (Producto Mínimo Viable)

| Campo | Detalle |
|---|---|
| **Propósito** | Demostrar el flujo completo de la herramienta con las funciones esenciales funcionando de extremo a extremo. |
| **Contenido esperado** | Sistema funcionando con: carga de contrato, extracción de texto, clasificación con confirmación del usuario, análisis y generación del informe con citas reales. |
| **Estado** | ⬜ No disponible — el desarrollo no ha comenzado. Ver definición en [`docs/PRD.md`](PRD.md). |
| **Qué falta** | Completar la documentación; comenzar la implementación; verificar cada función del MVP contra los criterios de aceptación definidos. |

---

## 10. PRD (Documento de Requisitos del Producto)

| Campo | Detalle |
|---|---|
| **Propósito** | Definir el problema, los usuarios, los objetivos, el alcance, las historias de usuario y los criterios de aceptación del producto. |
| **Contenido esperado** | Problema, usuarios previstos, objetivos, alcance, historias de usuario con criterios de aceptación, restricciones, riesgos y decisiones pendientes. |
| **Estado** | 🔶 Borrador inicial disponible — requiere revisión y validación con tutor y organización receptora. Ver [`docs/PRD.md`](PRD.md). |
| **Qué falta** | Validar perfiles de usuario, alcance del MVP, decisiones pendientes (API de IA, persistencia, autenticación). |

---

## Resumen de estados

| Estado | Significado |
|---|---|
| ⬜ No disponible | El entregable no existe todavía o no ha comenzado. |
| 🔶 Borrador | Existe un borrador inicial que requiere revisión y validación. |
| 🔷 En progreso | Se está trabajando activamente en el entregable. |
| ✅ Completado | El entregable existe, ha sido verificado y está listo para entregar. |

---

*Este documento se actualizará conforme avance el proyecto. Ningún entregable se marcará como completado sin haberlo verificado.*
