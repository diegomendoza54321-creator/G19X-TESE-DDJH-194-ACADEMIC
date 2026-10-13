# Requisitos del Sistema

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.1 — Borrador inicial  
**Estado:** En elaboración

---

## 1. Requisitos funcionales

### RF-01 — Carga de documentos

| ID | Descripción | Prioridad |
|---|---|---|
| RF-01.1 | El sistema debe aceptar archivos en formato PDF con texto seleccionable. | Alta |
| RF-01.2 | El sistema debe aceptar archivos en formato DOCX. | Alta |
| RF-01.3 | El sistema debe rechazar formatos no soportados y notificar al usuario con un mensaje claro. | Alta |
| RF-01.4 | El sistema debe definir y validar un tamaño máximo de archivo. *(tamaño pendiente de definir)* | Media |
| RF-01.5 | El sistema debe confirmar al usuario cuando la carga del archivo se completó correctamente. | Alta |

---

### RF-02 — Extracción de texto

| ID | Descripción | Prioridad |
|---|---|---|
| RF-02.1 | El sistema debe extraer el texto completo de un PDF con texto seleccionable. | Alta |
| RF-02.2 | El sistema debe extraer el texto completo de un archivo DOCX. | Alta |
| RF-02.3 | Si la extracción falla o resulta incompleta, el sistema debe notificar al usuario con un mensaje claro y detener el análisis. | Alta |
| RF-02.4 | El sistema no debe generar ni presentar hallazgos a partir de un texto que no pudo extraerse correctamente. No debe ofrecer continuar con una revisión parcial ni presentar resultados como si hubiera analizado el documento completo. | Alta |

---

### RF-03 — Clasificación del tipo de contrato

| ID | Descripción | Prioridad |
|---|---|---|
| RF-03.1 | El sistema debe proponer automáticamente el tipo de contrato identificado. | Alta |
| RF-03.2 | La propuesta de clasificación debe incluir una justificación breve basada en el texto del documento. | Alta |
| RF-03.3 | El usuario debe poder confirmar la clasificación propuesta antes de iniciar el análisis. | Alta |
| RF-03.4 | El usuario debe poder corregir la clasificación seleccionando un tipo diferente de una lista predefinida. | Alta |
| RF-03.5 | El análisis no debe iniciarse sin confirmación del usuario. | Alta |

---

### RF-04 — Análisis del contrato

| ID | Descripción | Prioridad |
|---|---|---|
| RF-04.1 | El sistema debe aplicar una lista de verificación base según el tipo de contrato confirmado. Existe una propuesta inicial de criterios base y condicionales que requiere validación con el tutor o con una persona con experiencia jurídica antes de considerarse definitiva. | Alta |
| RF-04.2 | El sistema debe aplicar criterios condicionales adicionales según el tipo de contrato. Estos criterios forman parte de la misma propuesta indicada en RF-04.1 y están sujetos a la misma validación. | Alta |
| RF-04.3 | El sistema debe identificar posibles ambigüedades en las cláusulas del contrato. | Alta |
| RF-04.4 | El sistema debe identificar posibles omisiones de elementos típicos en ese tipo de contrato. | Alta |
| RF-04.5 | El sistema debe identificar posibles contradicciones aparentes entre cláusulas. | Alta |
| RF-04.6 | El sistema debe identificar posibles riesgos contractuales. | Alta |

---

### RF-05 — Generación del informe de hallazgos

| ID | Descripción | Prioridad |
|---|---|---|
| RF-05.1 | Cada hallazgo debe incluir: descripción, cita textual, explicación, posible consecuencia, recomendación y limitaciones. | Alta |
| RF-05.2 | Las citas textuales deben corresponder exactamente a fragmentos del documento analizado. | Alta |
| RF-05.3 | El sistema no debe generar citas que no existan en el documento. | Alta (restricción de integridad) |
| RF-05.4 | En el informe solo se muestran las categorías que tengan al menos un hallazgo. Si una categoría no tiene hallazgos, no se muestra; en su lugar, el informe indica que no se identificaron hallazgos con los criterios aplicados, sin garantizar que el contrato esté libre de problemas de ese tipo. | Media |
| RF-05.5 | El informe debe incluir un aviso visible de que no constituye asesoría jurídica. | Alta |
| RF-05.6 | El informe debe presentarse en pantalla al usuario. | Alta |

---

### RF-06 — Presentación de resultados al usuario

| ID | Descripción | Prioridad |
|---|---|---|
| RF-06.1 | La interfaz debe estar en español. | Alta |
| RF-06.2 | Los hallazgos deben presentarse de forma comprensible para usuarios sin formación jurídica. | Alta |
| RF-06.3 | Cada hallazgo debe mostrar sus limitaciones de forma explícita. | Alta |

---

## 2. Requisitos no funcionales

### RNF-01 — Usabilidad

| ID | Descripción |
|---|---|
| RNF-01.1 | La interfaz debe ser comprensible para usuarios sin conocimientos técnicos ni jurídicos. |
| RNF-01.2 | El flujo de uso debe completarse sin necesidad de instrucciones adicionales para un usuario nuevo. *(validar en pruebas de usabilidad)* |

---

### RNF-02 — Rendimiento

| ID | Descripción |
|---|---|
| RNF-02.1 | El tiempo de respuesta para el análisis de un contrato de extensión típica debe ser razonable para el usuario. *(umbral pendiente de definir tras pruebas)* |
| RNF-02.2 | El sistema debe mostrar indicadores de progreso durante el análisis para no dar la impresión de error. |

---

### RNF-03 — Privacidad y seguridad

| ID | Descripción |
|---|---|
| RNF-03.1 | Los documentos cargados no deben ser almacenados de forma persistente sin consentimiento explícito del usuario. *(política pendiente de definir)* |
| RNF-03.2 | La comunicación entre el cliente y el servidor debe realizarse mediante HTTPS en el entorno de producción. |
| RNF-03.3 | El sistema no debe registrar el contenido de los contratos en logs de texto plano. |
| RNF-03.4 | El uso de APIs de IA de terceros debe ajustarse a las políticas de privacidad de la organización receptora. *(pendiente de validar)* |

---

### RNF-04 — Mantenibilidad

| ID | Descripción |
|---|---|
| RNF-04.1 | El código debe seguir convenciones de estilo definidas para el proyecto. *(pendiente de definir)* |
| RNF-04.2 | Las funciones críticas del backend deben contar con pruebas automatizadas. |
| RNF-04.3 | La lista de verificación base debe ser modificable sin cambiar el código de la aplicación. *(deseable; pendiente de diseño)* |

---

### RNF-05 — Disponibilidad

| ID | Descripción |
|---|---|
| RNF-05.1 | El entorno de demostración (MVP) debe estar disponible durante las presentaciones de la residencia. |
| RNF-05.2 | Los requisitos de disponibilidad en producción están pendientes de definir con la organización receptora. |

---

## 3. Reglas de prudencia jurídica

Estas reglas son restricciones no negociables que aplican a toda la aplicación:

| ID | Regla |
|---|---|
| RPJ-01 | El sistema nunca debe afirmar que un contrato "es válido", "es legal" o "cumple con la ley". |
| RPJ-02 | El sistema nunca debe generar, inferir ni inventar citas, cláusulas u obligaciones que no estén en el documento analizado. |
| RPJ-03 | Cada hallazgo debe incluir sus limitaciones; ningún hallazgo debe presentarse como una conclusión definitiva. |
| RPJ-04 | El sistema no debe emitir consejos jurídicos vinculantes ni actuar como sustituto de un abogado. |
| RPJ-05 | El informe generado debe incluir en todo momento un aviso visible de que no constituye asesoría jurídica y de que los resultados deben ser revisados por un profesional. |
| RPJ-06 | El sistema debe informar al usuario cuando la extracción de texto falla o resulta incompleta, y detener el análisis. No debe presentar hallazgos como si hubiera revisado el documento completo. |

---

## 4. Criterios de aceptación generales

- El sistema puede cargar, procesar y generar un informe para un contrato de prestación de servicios y para un contrato de proveedor, en PDF y en DOCX, sin errores no controlados.
- El sistema muestra correctamente la clasificación propuesta y permite al usuario confirmarla o corregirla.
- Todos los hallazgos incluyen cita textual, explicación, consecuencia posible, recomendación y limitaciones.
- No se genera ninguna cita que no exista en el documento analizado.
- El informe incluye el aviso de que no constituye asesoría jurídica.
- El sistema notifica al usuario cuando la extracción de texto falla o resulta incompleta, y detiene el análisis sin presentar hallazgos.
- La interfaz y todos los mensajes están en español.

---

## 5. Exclusiones del alcance inicial

- Contratos en idiomas distintos al español.
- Tipos de contrato distintos a prestación de servicios y proveedores.
- PDF escaneados sin capa de texto (OCR).
- Exportación del informe a PDF o DOCX.
- Autenticación y gestión de usuarios.
- Historial de análisis previos.
- Integración con sistemas externos (ERP, gestores documentales).
- Generación automática de contratos o cláusulas.
- Firma electrónica.

---

*Este documento es un borrador inicial sujeto a revisión y validación.*
