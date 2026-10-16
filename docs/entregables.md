# Lista de Control de Entregables

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.2 — Lista de 10 entregables oficiales  
**Estado:** Lista de control creada — ningún entregable está completo todavía

---

> Esta lista de control registra el estado de cada entregable requerido por el programa de residencias profesionales. Se actualizará conforme avance el proyecto. No se afirma que un entregable está terminado si todavía no existe o no ha sido verificado.

---

## 1. Accesos de prueba

| Campo | Detalle |
|---|---|
| **Propósito** | Permitir que el evaluador acceda al sistema en funcionamiento para verificar las funciones del MVP. |
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
| **Propósito** | Describir la arquitectura, las decisiones técnicas tomadas y el funcionamiento interno del sistema implementado, para la evaluación académica. Es un entregable distinto al manual técnico (ver entregable 8). |
| **Contenido esperado** | Arquitectura real implementada, tecnologías utilizadas con justificación, flujo del sistema, decisiones técnicas y sus razones. |
| **Estado** | ⬜ No disponible como entregable final — existe un borrador de arquitectura propuesta en [`docs/arquitectura.md`](arquitectura.md) que servirá de base. |
| **Qué falta** | Completar durante el desarrollo; consolidar en el formato requerido por la institución. **El formato exacto del documento técnico está pendiente de confirmar con la institución receptora.** |

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
| **Qué falta** | Completar durante el desarrollo; verificar cada paso en un entorno limpio antes de considerar el documento como terminado. |

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
| **Propósito** | Documentar el sistema para desarrolladores o responsables de mantenimiento. Es un entregable distinto al documento técnico (ver entregable 4). |
| **Contenido esperado** | Estructura del código, descripción de módulos, API del backend, variables de entorno, instrucciones de prueba y despliegue. |
| **Estado** | ⬜ Esqueleto creado como marcador — **pendiente de completar y validar**. Ver [`docs/manual-tecnico.md`](manual-tecnico.md). |
| **Qué falta** | Completar conforme avance la implementación; documentar decisiones técnicas reales, no supuestas. |

---

## 9. MVP (Producto Mínimo Viable)

Este entregable tiene dos componentes con estados distintos:

### 9a. Documento de alcance del MVP

| Campo | Detalle |
|---|---|
| **Propósito** | Definir qué incluye y excluye la primera versión funcional, el flujo principal, los criterios de aceptación y las condiciones de término. |
| **Contenido esperado** | Funciones incluidas, funciones excluidas, flujo principal, decisiones pendientes, criterios de aceptación verificables y condiciones de término. |
| **Estado** | 🔶 Borrador inicial disponible — sujeto a revisión y ajuste por el equipo del proyecto. Ver [`docs/MVP.md`](MVP.md). |
| **Qué falta** | Definir internamente y resolver decisiones pendientes (IA, almacenamiento, tamaño de archivo, criterios jurídicos). El acceso privado ya está decidido; lo pendiente es el mecanismo técnico de autenticación y la creación y administración de cuentas. |

### 9b. MVP funcionando (producto de software)

| Campo | Detalle |
|---|---|
| **Propósito** | Demostrar el flujo completo de la herramienta con las funciones esenciales funcionando de extremo a extremo, para evaluación y presentación de la residencia. |
| **Contenido esperado** | Sistema funcionando: carga de contrato, extracción de texto, clasificación con confirmación del usuario, análisis y generación del informe con citas reales. |
| **Estado** | ⬜ No disponible — el desarrollo no ha comenzado. El documento de alcance (`docs/MVP.md`) no es el producto funcionando. |
| **Qué falta** | Implementar y verificar cada función del MVP contra los criterios de aceptación de [`docs/MVP.md`](MVP.md); ejecutar el plan de pruebas; desplegar el sistema. |

---

## 10. PRD (Documento de Requisitos del Producto)

| Campo | Detalle |
|---|---|
| **Propósito** | Definir el problema, los usuarios, los objetivos, el alcance, las historias de usuario y los criterios de aceptación del producto. |
| **Contenido esperado** | Problema, usuarios previstos, objetivos, alcance, historias de usuario con criterios de aceptación, restricciones, riesgos y decisiones pendientes. |
| **Estado** | 🔶 Borrador inicial disponible — sujeto a revisión y ajuste por el equipo del proyecto. Ver [`docs/PRD.md`](PRD.md). |
| **Qué falta** | Definir internamente perfiles de usuario, alcance del MVP, decisiones pendientes (API de IA, persistencia, autenticación). |

---

## Resumen de estados

| Estado | Significado |
|---|---|
| ⬜ No disponible | El entregable no existe todavía o no ha comenzado. |
| 🔶 Borrador | Existe un borrador inicial sujeto a revisión y ajuste por el equipo del proyecto. |
| 🔷 En progreso | Se está trabajando activamente en el entregable. |
| ✅ Completado | El entregable existe, ha sido verificado y está listo para entregar. |

---

*Este documento se actualizará conforme avance el proyecto. Ningún entregable se marcará como completado sin haberlo verificado.*
