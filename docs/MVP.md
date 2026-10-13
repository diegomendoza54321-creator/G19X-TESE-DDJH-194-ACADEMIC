# Alcance del MVP

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.1 — Borrador inicial  
**Estado:** En elaboración  
**Relación con otros documentos:** Este documento define el alcance de la primera versión funcional. El problema, los usuarios y los objetivos generales del producto están en [`PRD.md`](PRD.md). Los requisitos detallados están en [`requisitos.md`](requisitos.md).

---

## 1. Propósito de este documento

Define qué debe hacer el MVP, qué queda fuera, cuál es el flujo principal y cuándo puede considerarse terminado. Es el documento de referencia para decidir si una función entra o no en la primera versión.

---

## 2. Definición del MVP

El MVP debe demostrar el flujo completo de extremo a extremo: desde que el usuario carga un contrato hasta que lee el informe de hallazgos en pantalla. No es un prototipo de interfaz ni una prueba técnica aislada; es una aplicación funcionando que cubre todas las funciones esenciales acordadas.

---

## 3. Funciones incluidas en el MVP

### 3.1 Carga del documento

- El usuario sube un archivo desde su dispositivo.
- Formatos aceptados: **PDF con texto seleccionable** y **DOCX**.
- El sistema confirma la carga exitosa con un mensaje visible.
- El sistema rechaza formatos no soportados con un mensaje claro.

### 3.2 Extracción de texto

- El sistema extrae el texto completo del archivo cargado.
- Si la extracción **falla o resulta incompleta**, el sistema:
  - Muestra un mensaje de advertencia claro al usuario.
  - **Detiene el análisis.** No genera ni presenta hallazgos.
  - No ofrece continuar con una revisión parcial.
  - No simula haber leído el documento completo.
  - Indica al usuario que verifique que el PDF tenga texto seleccionable o que intente con otro archivo.

### 3.3 Clasificación del tipo de contrato

- La IA propone el tipo de contrato identificado: **prestación de servicios** o **proveedor**.
- La propuesta incluye una justificación breve basada en el texto del documento.
- El usuario revisa la propuesta y debe **confirmarla o corregirla** antes de que inicie el análisis.
- El usuario puede seleccionar el tipo correcto de una lista predefinida con los dos tipos acordados.
- El análisis no inicia sin esa confirmación.

### 3.4 Análisis del contrato

- Con el tipo confirmado, el sistema aplica una **lista de verificación base** y **criterios condicionales** según el tipo.
- El sistema identifica y reporta:
  - Posibles ambigüedades en la redacción.
  - Posibles omisiones de elementos típicos del tipo de contrato.
  - Posibles contradicciones aparentes entre cláusulas.
  - Posibles riesgos contractuales.

> **Nota:** Existe una propuesta inicial de criterios base y condicionales. Requiere validación con el tutor o con una persona con experiencia jurídica antes de considerarse definitiva. *(pendiente)*

### 3.5 Informe de hallazgos

- El informe se presenta **en pantalla**.
- Por cada hallazgo, el informe muestra:
  - Cita textual del documento original (verificada contra el texto extraído).
  - Explicación del problema identificado.
  - Posible consecuencia.
  - Recomendación.
  - Limitaciones del análisis para ese hallazgo.
- **Solo se muestran las categorías que tengan al menos un hallazgo.** Si no se identificaron hallazgos en una categoría, el informe lo indica sin garantizar que el contrato esté libre de problemas de ese tipo.
- El informe incluye un aviso visible y permanente de que no constituye asesoría jurídica.
- El sistema no genera citas que no existan en el documento analizado.

---

## 4. Funciones excluidas del MVP

Las siguientes funciones están fuera de alcance para la primera versión y se registran aquí para evitar que entren por expansión del alcance durante el desarrollo:

| Función excluida | Razón o condición para incluirla en versiones futuras |
|---|---|
| Descarga o exportación del informe (PDF, DOCX) | Fuera del MVP; puede incluirse en la siguiente versión |
| Compartir el informe por correo u otro medio | Fuera del MVP |
| Autenticación y gestión de usuarios (login) | Pendiente de decidir si aplica al MVP — ver sección 6 |
| Historial de análisis previos | Requiere persistencia; fuera del MVP |
| Soporte para PDF escaneados (OCR) | Fuera del alcance inicial; posible versión futura |
| Análisis de contratos en otros idiomas | Fuera del alcance inicial |
| Tipos de contrato distintos a los dos acordados | Fuera del alcance inicial |
| Comparación entre versiones de un contrato | Fuera del alcance inicial |
| Integración con ERP u otros sistemas externos | Fuera del alcance inicial |
| Generación automática de contratos o cláusulas | Fuera del alcance por diseño |
| Firma electrónica | Fuera del alcance por diseño |

---

## 5. Flujo principal del MVP

Este es el camino que debe funcionar de extremo a extremo para que el MVP sea válido:

```
1. El usuario abre la aplicación en su navegador.
        │
2. El usuario carga un archivo PDF o DOCX.
        │
3. El sistema extrae el texto.
        │
        ├─ Si falla o está incompleto → aviso + detención. Fin del flujo.
        │
4. La IA propone el tipo de contrato con justificación breve.
        │
5. El usuario confirma o corrige la clasificación.
        │
6. El sistema aplica la lista de verificación al tipo confirmado.
        │
7. La IA analiza el texto y genera hallazgos estructurados.
        │
8. El sistema verifica que cada cita exista en el texto original.
        │
9. El sistema construye el informe y lo presenta en pantalla.
        │
10. El usuario lee el informe y aplica su propio criterio.
```

---

## 6. Decisiones pendientes que afectan el MVP

Estas decisiones no están resueltas. No deben asumirse como tomadas ni implementarse sin confirmación:

| Decisión | Impacto en el MVP |
|---|---|
| Selección de la API de IA (privacidad, costo, políticas) | Define la arquitectura del módulo de análisis y clasificación |
| Validación jurídica de la lista de criterios de revisión | Define qué busca el sistema en cada tipo de contrato |
| Autenticación de usuarios en el MVP | Si se requiere login, debe incluirse en el alcance del MVP |
| Política de almacenamiento del documento cargado | Define si el archivo se borra al cerrar la sesión o se guarda |
| Tamaño máximo de archivo aceptado | Afecta al mensaje de rechazo y a la infraestructura |

---

## 7. Criterios de aceptación del MVP

El MVP se considera funcionando cuando cumple **todos** los criterios siguientes:

### Carga y extracción
- [ ] El sistema acepta un PDF con texto seleccionable y extrae su texto sin errores.
- [ ] El sistema acepta un archivo DOCX y extrae su texto sin errores.
- [ ] El sistema rechaza un formato no soportado con un mensaje claro.
- [ ] El sistema detecta una extracción fallida o incompleta, muestra advertencia y detiene el análisis sin presentar hallazgos.

### Clasificación
- [ ] El sistema propone el tipo de contrato (prestación de servicios o proveedor) con una justificación breve basada en el texto.
- [ ] El usuario puede confirmar la clasificación propuesta.
- [ ] El usuario puede corregir la clasificación seleccionando el otro tipo.
- [ ] El análisis no inicia sin confirmación del usuario.

### Análisis
- [ ] El sistema aplica criterios de revisión distintos según el tipo de contrato confirmado.
- [ ] El sistema identifica al menos uno de los cuatro tipos de hallazgo (ambigüedad, omisión, contradicción, riesgo) en un contrato con problemas conocidos.

### Informe
- [ ] Cada hallazgo incluye: cita textual, explicación, posible consecuencia, recomendación y limitaciones.
- [ ] Todas las citas del informe existen literalmente en el texto del documento analizado.
- [ ] El informe no incluye citas inventadas.
- [ ] Solo se muestran categorías con hallazgos; las categorías sin hallazgos incluyen un mensaje que indica que no se identificaron hallazgos con los criterios aplicados, sin garantizar ausencia de problemas.
- [ ] El informe incluye un aviso visible de que no constituye asesoría jurídica.
- [ ] El informe no afirma que el contrato "es válido", "es legal" ni "cumple con la ley".

### General
- [ ] La interfaz y todos los mensajes están en español.
- [ ] El flujo completo (carga → extracción → clasificación → confirmación → análisis → informe) funciona sin errores no controlados para un contrato de prestación de servicios y para uno de proveedor.

---

## 8. Condiciones para considerar terminado el MVP

El MVP se considera **terminado** cuando:

1. Todos los criterios de aceptación de la sección 7 están verificados con contratos de prueba reales o sintéticos.
2. El plan de pruebas ([`plan-de-pruebas.md`](plan-de-pruebas.md)) ha sido ejecutado y los resultados están registrados.
3. La lista de criterios de revisión ha sido validada con el tutor o con una persona con experiencia jurídica.
4. El sistema está desplegado en un entorno al que el evaluador pueda acceder.
5. Los entregables de acceso de prueba y evidencias (capturas o video) están disponibles.

> Ninguna de estas condiciones está cumplida todavía. El estado actual es: documentación completa, implementación no iniciada.

---

*Este documento es un borrador inicial sujeto a revisión y validación con el tutor de residencias y la organización receptora.*
