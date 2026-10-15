# Plan de Pruebas

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.2 — Alineación con PRD v0.2, requisitos v0.2 y MVP v0.2  
**Estado:** En elaboración — los casos se completarán durante el desarrollo

---

## 1. Objetivos del plan de pruebas

- Verificar que el acceso está protegido y solo entran cuentas autorizadas.
- Verificar que el sistema procesa correctamente los formatos PDF y DOCX soportados.
- Validar que la clasificación del tipo de contrato es razonable y corregible.
- Confirmar que los hallazgos están respaldados por citas reales del documento.
- Verificar que el Historial registra correctamente los análisis y los aísla por usuario.
- Detectar comportamientos incorrectos ante documentos problemáticos.
- Verificar que el sistema aplica correctamente las reglas de prudencia jurídica.
- Verificar el comportamiento del tema claro/oscuro y la navegación principal.

---

## 2. Tipos de prueba contemplados

| Tipo | Descripción |
|---|---|
| Pruebas unitarias | Funciones individuales del backend (extracción, validación de citas, construcción del informe, registro del historial). |
| Pruebas de integración | Flujo completo desde el inicio de sesión hasta la generación del informe y su registro en el historial. |
| Pruebas de casos límite | Documentos problemáticos, clasificaciones incorrectas, extracciones fallidas, credenciales incorrectas. |
| Pruebas de validación de salida | Verificar que las citas existen en el texto y que el informe cumple con las reglas de prudencia jurídica. |
| Pruebas manuales / exploratorias | Revisión cualitativa de la calidad de los hallazgos con contratos reales o sintéticos. |

---

## 3. Casos de prueba

> **Nota:** Los contratos usados en las pruebas deben ser documentos sintéticos o de dominio público. No usar contratos reales de la organización salvo autorización expresa.

---

### Grupo I — Autenticación y acceso

#### CI-01 — Inicio de sesión con credenciales correctas

**Descripción:** Un usuario con cuenta autorizada introduce sus credenciales correctas.  
**Resultado esperado:**
- El sistema permite el acceso.
- El usuario llega a la pantalla de inicio de la herramienta.
- No se expone información interna ni de otros usuarios.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CI-02 — Inicio de sesión con credenciales incorrectas

**Descripción:** Se introducen credenciales incorrectas (usuario inexistente, contraseña errónea o ambos).  
**Resultado esperado:**
- El sistema muestra un mensaje de error genérico que no indica qué campo específico falló.
- El acceso es denegado.
- El sistema no expone información sobre cuentas existentes.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CI-03 — Ausencia de registro público

**Descripción:** Se verifica que no existe ninguna opción de crear una cuenta desde la interfaz pública.  
**Resultado esperado:**
- No hay enlace, botón ni formulario de registro accesible sin sesión iniciada.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CI-04 — Acceso a función privada sin sesión iniciada

**Descripción:** Se intenta acceder directamente a una ruta protegida (p. ej. Analizar contrato o Historial) sin haber iniciado sesión.  
**Resultado esperado:**
- El sistema redirige al usuario a la pantalla de inicio de sesión o muestra un error de acceso no autorizado.
- No se muestra contenido privado.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

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
- No se generan ni muestran hallazgos.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CG-02 — PDF con extracción parcial

**Descripción:** PDF con texto seleccionable en algunas páginas pero no en todas, de modo que la extracción resulta incompleta.  
**Resultado esperado:**
- El sistema detecta que la extracción es incompleta.
- Muestra un mensaje de advertencia claro al usuario.
- **Detiene el análisis.** No genera ni presenta hallazgos.
- No ofrece continuar con una revisión parcial ni simula haber leído el documento completo.
- Indica al usuario que verifique el archivo o intente con otro.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CG-03 — Archivo corrupto o no legible

**Descripción:** Se carga un archivo que no puede abrirse (corrupto o truncado).  
**Resultado esperado:**
- El sistema detecta el error.
- Se notifica al usuario con un mensaje de error claro.
- El sistema no genera un informe vacío ni expone errores internos.

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

### Grupo J — Historial de análisis

#### CJ-01 — Un análisis completado aparece en el Historial

**Descripción:** Tras completar un análisis exitosamente, el usuario navega a la sección Historial.  
**Resultado esperado:**
- El análisis recién completado aparece en la lista del historial del usuario.
- La entrada incluye información identificable del análisis (p. ej. fecha, tipo de contrato). Los campos exactos están pendientes de definir.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CJ-02 — El usuario puede abrir un análisis anterior desde el Historial

**Descripción:** El usuario selecciona una entrada del Historial para consultar su informe.  
**Resultado esperado:**
- El informe del análisis anterior se muestra correctamente.
- No se ofrece ni aparece el archivo original del contrato.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CJ-03 — El Historial de un usuario no muestra análisis de otro usuario

**Descripción:** Dos usuarios distintos con cuentas autorizadas realizan análisis. Cada uno consulta su Historial.  
**Resultado esperado:**
- El usuario A solo ve sus propios análisis.
- El usuario B solo ve los suyos.
- Ninguno puede acceder a los análisis del otro.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

### Grupo K — Interfaz: tema y navegación

#### CK-01 — Cambio de tema claro a oscuro y persistencia

**Descripción:** El usuario cambia el tema de claro a oscuro, luego recarga la página o abre la herramienta en una nueva visita.  
**Resultado esperado:**
- El tema oscuro se aplica visualmente tras el cambio.
- Al recargar o volver a abrir, la herramienta aplica automáticamente el tema oscuro sin que el usuario lo ajuste de nuevo.
- El cambio no interrumpe la sesión ni el flujo de trabajo en curso.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

#### CK-02 — Navegación principal completa y accesible

**Descripción:** El usuario con sesión iniciada verifica la navegación principal.  
**Resultado esperado:**
- Las secciones Inicio, Analizar contrato, Resultados e Historial están disponibles en la navegación.
- Cada sección es accesible desde la navegación sin errores.

**Resultado real:** *(registrar durante las pruebas)*  
**Estado:** Pendiente

---

## 4. Registro de resultados

Para cada caso ejecutado, registrar:

| Campo | Descripción |
|---|---|
| ID del caso | Identificador del caso de prueba (p. ej. CI-01) |
| Fecha de ejecución | Fecha en que se ejecutó la prueba |
| Versión del sistema | Commit o versión del sistema bajo prueba |
| Resultado real | Lo que el sistema produjo realmente |
| ¿Pasa? | Sí / No / Parcial |
| Observaciones | Notas relevantes, defectos encontrados, comportamientos inesperados |
| Defecto registrado en | Referencia al issue o tarea creada si se encontró un defecto |

---

*Este documento es un borrador. Los contratos de prueba y los resultados reales se completarán durante el desarrollo.*
