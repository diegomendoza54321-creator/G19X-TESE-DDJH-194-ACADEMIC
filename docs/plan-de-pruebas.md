# Plan de Pruebas

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.1 — Borrador inicial  
**Estado:** En elaboración — los casos se completarán durante el desarrollo

---

## 1. Objetivos del plan de pruebas

- Verificar que el sistema procesa correctamente los formatos PDF y DOCX soportados.
- Validar que la clasificación del tipo de contrato es razonable y corregible.
- Confirmar que los hallazgos están respaldados por citas reales del documento.
- Detectar comportamientos incorrectos ante documentos problemáticos (ilegibles, incompletos, mal formateados).
- Verificar que el sistema aplica correctamente las reglas de prudencia jurídica.

---

## 2. Tipos de prueba contemplados

| Tipo | Descripción |
|---|---|
| Pruebas unitarias | Funciones individuales del backend (extracción, validación de citas, construcción del informe). |
| Pruebas de integración | Flujo completo desde la carga hasta la generación del informe. |
| Pruebas de casos límite | Documentos problemáticos, clasificaciones incorrectas, extracciones fallidas. |
| Pruebas de validación de salida | Verificar que las citas existen en el texto y que el informe cumple con las reglas de prudencia jurídica. |
| Pruebas manuales / exploratorias | Revisión cualitativa de la calidad de los hallazgos con contratos reales o sintéticos. |

---

## 3. Casos de prueba

> **Nota:** Los contratos usados en las pruebas deben ser documentos sintéticos o de dominio público. No usar contratos reales de la organización salvo autorización expresa.

---

### Grupo A — Contratos claros y bien estructurados

#### CA-01 — Contrato de prestación de servicios completo

**Descripción:** Contrato de prestación de servicios con todas las secciones típicas presentes y sin ambigüedades evidentes.  
**Formato:** PDF con texto seleccionable  
**Resultado esperado:**
- Extracción de texto exitosa.
- El sistema propone correctamente el tipo "Prestación de servicios".
- La lista de verificación se aplica completamente.
- Los hallazgos, si los hay, incluyen citas reales, explicación, consecuencia, recomendación y limitaciones.
- No se generan hallazgos sin fundamento en el texto.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CA-02 — Contrato de proveedor completo

**Descripción:** Contrato de proveedor de bienes con todas las secciones estándar y redacción sin problemas evidentes.  
**Formato:** DOCX  
**Resultado esperado:**
- Extracción de texto exitosa.
- El sistema propone correctamente el tipo "Contrato de proveedor".
- Se aplican los criterios condicionales correspondientes.
- Los hallazgos incluyen citas reales.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo B — Contratos con ambigüedades

#### CB-01 — Cláusula de vigencia indefinida o imprecisa

**Descripción:** Contrato cuya cláusula de vigencia usa términos vagos ("mientras las partes lo decidan", sin fecha de término).  
**Resultado esperado:**
- El sistema identifica la ambigüedad en la cláusula de vigencia.
- El hallazgo incluye la cita textual de la cláusula.
- Se explica la posible consecuencia y se recomienda precisar la fecha o el mecanismo de terminación.
- El hallazgo incluye limitaciones del análisis.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CB-02 — Cláusula de pago con términos ambiguos

**Descripción:** Contrato donde la forma de pago usa términos como "de común acuerdo" sin especificar montos, fechas ni condiciones.  
**Resultado esperado:**
- El sistema identifica la ambigüedad.
- Se genera un hallazgo con cita textual y explicación.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo C — Contratos con posibles omisiones

#### CC-01 — Contrato sin cláusula de confidencialidad

**Descripción:** Contrato de prestación de servicios donde se espera una cláusula de confidencialidad pero no existe.  
**Resultado esperado:**
- El sistema identifica la omisión.
- El hallazgo indica que no se encontró cláusula de confidencialidad.
- No se genera una cita falsa.
- Se incluye la recomendación de incluir dicha cláusula.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CC-02 — Contrato sin mecanismo de resolución de disputas

**Descripción:** Contrato sin cláusula de arbitraje ni jurisdicción aplicable.  
**Resultado esperado:**
- El sistema identifica la omisión.
- El hallazgo no genera una cita inventada para justificar la observación.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo D — Contratos con posibles contradicciones aparentes

#### CD-01 — Contradicción entre plazo de entrega y fecha de vigencia

**Descripción:** Contrato donde el plazo de entrega del servicio es posterior a la fecha de terminación del contrato.  
**Resultado esperado:**
- El sistema identifica la posible contradicción.
- El hallazgo cita ambas cláusulas relevantes.
- La explicación señala el conflicto potencial sin afirmar que el contrato es inválido.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CD-02 — Contradicción en el monto de pago

**Descripción:** El monto aparece diferente en dos cláusulas del mismo contrato (en letras vs. en números).  
**Resultado esperado:**
- El sistema identifica la posible contradicción.
- Se generan citas de ambas referencias.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo E — Contratos con riesgos contractuales potenciales

#### CE-01 — Cláusula de exclusividad desfavorable

**Descripción:** Contrato donde se exige exclusividad al prestador sin contraprestación clara.  
**Resultado esperado:**
- El sistema identifica el riesgo.
- El hallazgo incluye la cita, la explicación del riesgo y la recomendación.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CE-02 — Cláusula de responsabilidad ilimitada

**Descripción:** Contrato que establece responsabilidad ilimitada para una de las partes sin justificación.  
**Resultado esperado:**
- El sistema identifica el riesgo.
- Se genera el hallazgo con cita textual y advertencia de limitaciones.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo F — Clasificación del tipo de contrato

#### CF-01 — Clasificación correcta (prestación de servicios)

**Descripción:** El contrato es claramente de prestación de servicios y el sistema lo clasifica correctamente.  
**Resultado esperado:** Clasificación correcta en la primera propuesta.  
**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CF-02 — Clasificación incorrecta del sistema (corregida por el usuario)

**Descripción:** El documento es un contrato de proveedor, pero el sistema lo clasifica incorrectamente como contrato de prestación de servicios. El usuario corrige la clasificación y el análisis se ejecuta con el tipo correcto.  
**Resultado esperado:**
- La interfaz permite al usuario seleccionar "Contrato de proveedor" en lugar de la propuesta incorrecta.
- El análisis se realiza con el tipo seleccionado por el usuario ("Contrato de proveedor"), no con el propuesto inicialmente ("Prestación de servicios").
- Los criterios de verificación aplicados corresponden al tipo corregido por el usuario.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CF-03 — Documento que no es un contrato

**Descripción:** Se carga un documento que no es un contrato (p. ej. una factura, una carta, un reglamento interno).  
**Resultado esperado:**
- El sistema indica que no pudo identificar un tipo de contrato conocido.
- Se solicita al usuario que confirme el tipo manualmente.
- El sistema no genera hallazgos sin fundamento.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo G — PDF ilegible o extracción incompleta

#### CG-01 — PDF escaneado sin capa de texto

**Descripción:** Se carga un PDF escaneado cuyo texto no es seleccionable.  
**Resultado esperado:**
- El sistema detecta que no puede extraer texto.
- Se notifica al usuario con un mensaje claro.
- El sistema no procede al análisis sin texto extraído.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CG-02 — PDF con extracción parcial

**Descripción:** PDF con texto seleccionable en algunas páginas pero no en todas.  
**Resultado esperado:**
- El sistema informa que la extracción fue parcial.
- El usuario decide si continúa con el texto disponible.
- El informe indica que el análisis es parcial.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CG-03 — Archivo corrupto o no legible

**Descripción:** Se carga un archivo que no puede abrirse (corrupto o truncado).  
**Resultado esperado:**
- El sistema detecta el error.
- Se notifica al usuario con un mensaje de error claro.
- El sistema no genera un informe vacío ni con errores internos expuestos.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo H — Reglas de prudencia jurídica

#### CH-01 — El informe no afirma que el contrato es válido o ilegal

**Descripción:** Verificar que ningún hallazgo ni sección del informe use frases como "el contrato es válido", "el contrato es ilegal" o "cumple con la ley".  
**Resultado esperado:** No aparecen esas afirmaciones en ninguna parte del informe.  
**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CH-02 — Las citas en el informe existen en el documento analizado

**Descripción:** Verificar manualmente que cada cita textual en el informe aparece literalmente en el documento cargado.  
**Resultado esperado:** Todas las citas son verificables en el documento original.  
**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CH-03 — El aviso de uso responsable es visible en el informe

**Descripción:** Verificar que el informe generado incluye el aviso de que no constituye asesoría jurídica.  
**Resultado esperado:** El aviso es visible y está redactado de forma clara.  
**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

## 4. Registro de resultados

Para cada caso ejecutado, registrar:

| Campo | Descripción |
|---|---|
| ID del caso | Identificador del caso de prueba (p. ej. CA-01) |
| Fecha de ejecución | Fecha en que se ejecutó la prueba |
| Versión del sistema | Commit o versión del sistema bajo prueba |
| Resultado real | Lo que el sistema produjo realmente |
| ¿Pasa? | Sí / No / Parcial |
| Observaciones | Notas relevantes, defectos encontrados, comportamientos inesperados |
| Defecto registrado en | Referencia al issue o tarea creada si se encontró un defecto |

---

*Este documento es un borrador inicial. Los contratos de prueba y los resultados reales se completarán durante el desarrollo.*
