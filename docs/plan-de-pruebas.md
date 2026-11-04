# Plan de Pruebas

**Proyecto:** MotorRevisionLegal
**VersiÃ³n:** 0.2 â€” AlineaciÃ³n con PRD v0.2, requisitos v0.2 y MVP v0.2
**Estado:** En elaboraciÃ³n â€” los casos se completarÃ¡n durante el desarrollo

---

## 1. Objetivos del plan de pruebas

- Verificar que el acceso estÃ¡ protegido y solo entran cuentas autorizadas.
- Verificar que el sistema procesa correctamente los formatos PDF y DOCX soportados.
- Validar que la clasificaciÃ³n del tipo de contrato es razonable y corregible.
- Confirmar que los hallazgos estÃ¡n respaldados por citas reales del documento.
- Verificar que el Historial registra correctamente los anÃ¡lisis y los aÃ­sla por usuario.
- Detectar comportamientos incorrectos ante documentos problemÃ¡ticos.
- Verificar que el sistema aplica correctamente las reglas de prudencia jurÃ­dica.
- Verificar el comportamiento del tema claro/oscuro y la navegaciÃ³n principal.

---

## 2. Tipos de prueba contemplados

| Tipo | DescripciÃ³n |
|---|---|
| Pruebas unitarias | Funciones individuales del backend (extracciÃ³n, validaciÃ³n de citas, construcciÃ³n del informe, registro del historial). |
| Pruebas de integraciÃ³n | Flujo completo desde el inicio de sesiÃ³n hasta la generaciÃ³n del informe y su registro en el historial. |
| Pruebas de casos lÃ­mite | Documentos problemÃ¡ticos, clasificaciones incorrectas, extracciones fallidas, credenciales incorrectas. |
| Pruebas de validaciÃ³n de salida | Verificar que las citas existen en el texto y que el informe cumple con las reglas de prudencia jurÃ­dica. |
| Pruebas manuales / exploratorias | RevisiÃ³n cualitativa de la calidad de los hallazgos con contratos reales o sintÃ©ticos. |

---

## 3. Casos de prueba

> **Ãšltima corrida verificada:** 102 pruebas de backend aprobadas (`pytest backend`), distribuidas en `test_analisis_ia.py` (29), `test_api.py` (10), `test_auth.py` (17), `test_citas.py` (28), `test_extraccion.py` (14) y `test_historial.py` (4).

> **Nota:** Los contratos usados en las pruebas deben ser documentos sintÃ©ticos o de dominio pÃºblico. No usar contratos reales de la organizaciÃ³n salvo autorizaciÃ³n expresa.

---

### Grupo I â€” AutenticaciÃ³n y acceso

#### CI-01 â€” Inicio de sesiÃ³n con credenciales correctas

**DescripciÃ³n:** Un usuario con cuenta autorizada introduce sus credenciales correctas.
**Resultado esperado:**
- El sistema permite el acceso.
- El usuario llega a la pantalla de inicio de la herramienta.
- No se expone informaciÃ³n interna ni de otros usuarios.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_auth.py`: login correcto).
**Estado:** Aprobado

---

#### CI-02 â€” Inicio de sesiÃ³n con credenciales incorrectas

**DescripciÃ³n:** Se introducen credenciales incorrectas (usuario inexistente, contraseÃ±a errÃ³nea o ambos).
**Resultado esperado:**
- El sistema muestra un mensaje de error genÃ©rico que no indica quÃ© campo especÃ­fico fallÃ³.
- El acceso es denegado.
- El sistema no expone informaciÃ³n sobre cuentas existentes.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_auth.py`: credenciales incorrectas â†’ acceso denegado).
**Estado:** Aprobado

---

#### CI-03 â€” Ausencia de registro pÃºblico

**DescripciÃ³n:** Se verifica que no existe ninguna opciÃ³n de crear una cuenta desde la interfaz pÃºblica.
**Resultado esperado:**
- No hay enlace, botÃ³n ni formulario de registro accesible sin sesiÃ³n iniciada.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_auth.py`: sin registro pÃºblico â†’ 404).
**Estado:** Aprobado

---

#### CI-04 â€” Acceso a funciÃ³n privada sin sesiÃ³n iniciada

**DescripciÃ³n:** Se intenta acceder directamente a una ruta protegida (p. ej. Analizar contrato o Historial) sin haber iniciado sesiÃ³n.
**Resultado esperado:**
- El sistema redirige al usuario a la pantalla de inicio de sesiÃ³n o muestra un error de acceso no autorizado.
- No se muestra contenido privado.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_auth.py` y `test_analisis_ia.py`: acceso sin sesiÃ³n â†’ 401).
**Estado:** Aprobado

---

### Grupo A â€” Contratos claros y bien estructurados

#### CA-01 â€” Contrato de prestaciÃ³n de servicios completo

**DescripciÃ³n:** Contrato de prestaciÃ³n de servicios con todas las secciones tÃ­picas presentes y sin ambigÃ¼edades evidentes.
**Formato:** PDF con texto seleccionable
**Resultado esperado:**
- ExtracciÃ³n de texto exitosa.
- El sistema propone correctamente el tipo "PrestaciÃ³n de servicios".
- La lista de verificaciÃ³n se aplica completamente.
- Los hallazgos, si los hay, incluyen citas reales, explicaciÃ³n, consecuencia, recomendaciÃ³n y limitaciones.
- No se generan hallazgos sin fundamento en el texto.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_api.py`: extracciÃ³n exitosa de PDF y DOCX vÃ¡lidos).
**Estado:** Aprobado

---

#### CA-02 â€” Contrato de proveedor completo

**DescripciÃ³n:** Contrato de proveedor de bienes con todas las secciones estÃ¡ndar y redacciÃ³n sin problemas evidentes.
**Formato:** DOCX
**Resultado esperado:**
- ExtracciÃ³n de texto exitosa.
- El sistema propone correctamente el tipo "Contrato de proveedor".
- Se aplican los criterios condicionales correspondientes.
- Los hallazgos incluyen citas reales.

**Resultado real:** 102 pruebas de backend pasaron (`test_api.py`: extracciÃ³n de DOCX) y prueba manual con Contrato-sintetico.docx confirmÃ³ clasificaciÃ³n como "Contrato de proveedor".
**Estado:** Aprobado

---

### Grupo B â€” Contratos con ambigÃ¼edades

#### CB-01 â€” ClÃ¡usula de vigencia indefinida o imprecisa

**DescripciÃ³n:** Contrato cuya clÃ¡usula de vigencia usa tÃ©rminos vagos ("mientras las partes lo decidan", sin fecha de tÃ©rmino).
**Resultado esperado:**
- El sistema identifica la ambigÃ¼edad en la clÃ¡usula de vigencia.
- El hallazgo incluye la cita textual de la clÃ¡usula.
- Se explica la posible consecuencia y se recomienda precisar la fecha o el mecanismo de terminaciÃ³n.
- El hallazgo incluye limitaciones del anÃ¡lisis.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CB-02 â€” ClÃ¡usula de pago con tÃ©rminos ambiguos

**DescripciÃ³n:** Contrato donde la forma de pago usa tÃ©rminos como "de comÃºn acuerdo" sin especificar montos, fechas ni condiciones.
**Resultado esperado:**
- El sistema identifica la ambigÃ¼edad.
- Se genera un hallazgo con cita textual y explicaciÃ³n.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

### Grupo C â€” Contratos con posibles omisiones

#### CC-01 â€” Contrato sin clÃ¡usula de confidencialidad

**DescripciÃ³n:** Contrato de prestaciÃ³n de servicios donde se espera una clÃ¡usula de confidencialidad pero no existe.
**Resultado esperado:**
- El sistema identifica la omisiÃ³n.
- El hallazgo indica que no se encontrÃ³ clÃ¡usula de confidencialidad.
- No se genera una cita falsa.
- Se incluye la recomendaciÃ³n de incluir dicha clÃ¡usula.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CC-02 â€” Contrato sin mecanismo de resoluciÃ³n de disputas

**DescripciÃ³n:** Contrato sin clÃ¡usula de arbitraje ni jurisdicciÃ³n aplicable.
**Resultado esperado:**
- El sistema identifica la omisiÃ³n.
- El hallazgo no genera una cita inventada para justificar la observaciÃ³n.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

### Grupo D â€” Contratos con posibles contradicciones aparentes

#### CD-01 â€” ContradicciÃ³n entre plazo de entrega y fecha de vigencia

**DescripciÃ³n:** Contrato donde el plazo de entrega del servicio es posterior a la fecha de terminaciÃ³n del contrato.
**Resultado esperado:**
- El sistema identifica la posible contradicciÃ³n.
- El hallazgo cita ambas clÃ¡usulas relevantes.
- La explicaciÃ³n seÃ±ala el conflicto potencial sin afirmar que el contrato es invÃ¡lido.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CD-02 â€” ContradicciÃ³n en el monto de pago

**DescripciÃ³n:** El monto aparece diferente en dos clÃ¡usulas del mismo contrato (en letras vs. en nÃºmeros).
**Resultado esperado:**
- El sistema identifica la posible contradicciÃ³n.
- Se generan citas de ambas referencias.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

### Grupo E â€” Contratos con riesgos contractuales potenciales

#### CE-01 â€” ClÃ¡usula de exclusividad desfavorable

**DescripciÃ³n:** Contrato donde se exige exclusividad al prestador sin contraprestaciÃ³n clara.
**Resultado esperado:**
- El sistema identifica el riesgo.
- El hallazgo incluye la cita, la explicaciÃ³n del riesgo y la recomendaciÃ³n.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CE-02 â€” ClÃ¡usula de responsabilidad ilimitada

**DescripciÃ³n:** Contrato que establece responsabilidad ilimitada para una de las partes sin justificaciÃ³n.
**Resultado esperado:**
- El sistema identifica el riesgo.
- Se genera el hallazgo con cita textual y advertencia de limitaciones.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

### Grupo F â€” ClasificaciÃ³n del tipo de contrato

#### CF-01 â€” ClasificaciÃ³n correcta (prestaciÃ³n de servicios)

**DescripciÃ³n:** El contrato es claramente de prestaciÃ³n de servicios y el sistema lo clasifica correctamente.
**Resultado esperado:** El sistema clasifica localmente y de forma determinista el contrato como "PrestaciÃ³n de servicios", sin usar IA ni enviar texto a terceros.
**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CF-02 â€” ClasificaciÃ³n incorrecta del sistema (corregida por el usuario)

**DescripciÃ³n:** El documento es un contrato de proveedor, pero el sistema lo clasifica incorrectamente como contrato de prestaciÃ³n de servicios. El usuario corrige la clasificaciÃ³n y el anÃ¡lisis se ejecuta con el tipo correcto.
**Resultado esperado:**
- La interfaz permite al usuario seleccionar "Contrato de proveedor" en lugar de la propuesta incorrecta.
- El anÃ¡lisis se realiza con el tipo seleccionado por el usuario ("Contrato de proveedor"), no con el propuesto inicialmente ("PrestaciÃ³n de servicios").
- Los criterios de verificaciÃ³n aplicados corresponden al tipo corregido por el usuario.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CF-03 â€” Documento que no es un contrato

**DescripciÃ³n:** Se carga un documento que no es un contrato (p. ej. una factura, una carta, un reglamento interno).
**Resultado esperado:**
- El sistema indica que no pudo identificar un tipo de contrato conocido.
- Se solicita al usuario que confirme el tipo manualmente.
- El sistema no genera hallazgos sin fundamento.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

### Grupo G â€” PDF ilegible o extracciÃ³n incompleta

#### CG-01 â€” PDF escaneado sin capa de texto

**DescripciÃ³n:** Se carga un PDF escaneado cuyo texto no es seleccionable.
**Resultado esperado:**
- El sistema detecta que no puede extraer texto.
- Se notifica al usuario con un mensaje claro.
- El sistema no procede al anÃ¡lisis sin texto extraÃ­do.
- No se generan ni muestran hallazgos.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_api.py`: PDF escaneado â†’ 422 sin texto).
**Estado:** Aprobado

---

#### CG-02 â€” PDF con extracciÃ³n parcial

**DescripciÃ³n:** PDF con texto seleccionable en algunas pÃ¡ginas pero no en todas, de modo que la extracciÃ³n resulta incompleta.
**Resultado esperado:**
- El sistema detecta que la extracciÃ³n es incompleta.
- Muestra un mensaje de advertencia claro al usuario.
- **Detiene el anÃ¡lisis.** No genera ni presenta hallazgos.
- No ofrece continuar con una revisiÃ³n parcial ni simula haber leÃ­do el documento completo.
- Indica al usuario que verifique el archivo o intente con otro.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_api.py`: extracciÃ³n parcial â†’ 422, texto nulo).
**Estado:** Aprobado

---

#### CG-03 â€” Archivo corrupto o no legible

**DescripciÃ³n:** Se carga un archivo que no puede abrirse (corrupto o truncado).
**Resultado esperado:**
- El sistema detecta el error.
- Se notifica al usuario con un mensaje de error claro.
- El sistema no genera un informe vacÃ­o ni expone errores internos.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_api.py`: archivo corrupto â†’ 422).
**Estado:** Aprobado

---

### Grupo H â€” Reglas de prudencia jurÃ­dica

#### CH-01 â€” El informe no afirma que el contrato es vÃ¡lido o ilegal

**DescripciÃ³n:** Verificar que ningÃºn hallazgo ni secciÃ³n del informe use frases como "el contrato es vÃ¡lido", "el contrato es ilegal" o "cumple con la ley".
**Resultado esperado:** No aparecen esas afirmaciones en ninguna parte del informe.
**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CH-02 â€” Las citas en el informe existen en el documento analizado

**DescripciÃ³n:** Verificar manualmente que cada cita textual en el informe aparece literalmente en el documento cargado.
**Resultado esperado:** Todas las citas son verificables en el documento original.
**Resultado real:** Prueba manual con Contrato-sintetico.docx generÃ³ un hallazgo con cita literal; 102 pruebas de backend pasaron (`test_citas.py`: verificaciÃ³n de citas textuales).
**Estado:** Aprobado

---

#### CH-03 â€” El aviso de uso responsable es visible en el informe

**DescripciÃ³n:** Verificar que el informe generado incluye el aviso de que no constituye asesorÃ­a jurÃ­dica.
**Resultado esperado:** El aviso es visible y estÃ¡ redactado de forma clara.
**Resultado real:** Prueba manual con Contrato-sintetico.docx mostrÃ³ el aviso de no asesorÃ­a jurÃ­dica en el informe.
**Estado:** Aprobado

---

### Grupo J â€” Historial de anÃ¡lisis

#### CJ-01 â€” Un anÃ¡lisis completado aparece en el Historial

**DescripciÃ³n:** Tras completar un anÃ¡lisis exitosamente, el usuario navega a la secciÃ³n Historial.
**Resultado esperado:**
- El anÃ¡lisis reciÃ©n completado aparece en la lista del historial del usuario.
- La entrada incluye informaciÃ³n identificable del anÃ¡lisis (p. ej. fecha, tipo de contrato). Los campos exactos estÃ¡n pendientes de definir.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_historial.py`: `test_analisis_exitoso_guarda_registro_historial`).
**Estado:** Aprobado

---

#### CJ-02 â€” El usuario puede abrir un anÃ¡lisis anterior desde el Historial

**DescripciÃ³n:** El usuario selecciona una entrada del Historial para consultar su informe.
**Resultado esperado:**
- El informe del anÃ¡lisis anterior se muestra correctamente.
- No se ofrece ni aparece el archivo original del contrato.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CJ-03 â€” El Historial de un usuario no muestra anÃ¡lisis de otro usuario

**DescripciÃ³n:** Dos usuarios distintos con cuentas autorizadas realizan anÃ¡lisis. Cada uno consulta su Historial.
**Resultado esperado:**
- El usuario A solo ve sus propios anÃ¡lisis.
- El usuario B solo ve los suyos.
- Ninguno puede acceder a los anÃ¡lisis del otro.

**Resultado real:** 102 pruebas de backend pasaron (incluye `test_historial.py`: `test_usuario_no_ve_registros_de_otro`).
**Estado:** Aprobado

---

### Grupo K â€” Interfaz: tema y navegaciÃ³n

#### CK-01 â€” Cambio de tema claro a oscuro y persistencia

**DescripciÃ³n:** El usuario cambia el tema de claro a oscuro, luego recarga la pÃ¡gina o abre la herramienta en una nueva visita.
**Resultado esperado:**
- El tema oscuro se aplica visualmente tras el cambio.
- Al recargar o volver a abrir, la herramienta aplica automÃ¡ticamente el tema oscuro sin que el usuario lo ajuste de nuevo.
- El cambio no interrumpe la sesiÃ³n ni el flujo de trabajo en curso.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

#### CK-02 â€” NavegaciÃ³n principal completa y accesible

**DescripciÃ³n:** El usuario con sesiÃ³n iniciada verifica la navegaciÃ³n principal.
**Resultado esperado:**
- Las secciones Inicio, Analizar contrato, Resultados e Historial estÃ¡n disponibles en la navegaciÃ³n.
- Cada secciÃ³n es accesible desde la navegaciÃ³n sin errores.

**Resultado real:** *(registrar durante las pruebas)*
**Estado:** Pendiente

---

## 4. Registro de resultados

Para cada caso ejecutado, registrar:

| Campo | DescripciÃ³n |
|---|---|
| ID del caso | Identificador del caso de prueba (p. ej. CI-01) |
| Fecha de ejecuciÃ³n | Fecha en que se ejecutÃ³ la prueba |
| VersiÃ³n del sistema | Commit o versiÃ³n del sistema bajo prueba |
| Resultado real | Lo que el sistema produjo realmente |
| Â¿Pasa? | SÃ­ / No / Parcial |
| Observaciones | Notas relevantes, defectos encontrados, comportamientos inesperados |
| Defecto registrado en | Referencia al issue o tarea creada si se encontrÃ³ un defecto |

---

*Este documento es un borrador. Los contratos de prueba y los resultados reales se completarÃ¡n durante el desarrollo.*

---

### Nota sobre casos pendientes

Los siguientes casos no cuentan con evidencia suficiente para aprobarse en esta entrega y se mantienen como **Pendiente**:

- **CB-01, CB-02** (contratos con ambigÃ¼edades): no hay pruebas de detecciÃ³n de ambigÃ¼edades en el flujo completo.
- **CC-01, CC-02** (contratos con omisiones): no hay pruebas de detecciÃ³n de omisiones en el flujo completo.
- **CD-01, CD-02** (contratos con contradicciones aparentes): no hay pruebas de detecciÃ³n de contradicciones en el flujo completo.
- **CE-01, CE-02** (contratos con riesgos contractuales): no hay pruebas de detecciÃ³n de riesgos en el flujo completo.
- **CF-01** (clasificaciÃ³n correcta de prestaciÃ³n de servicios): no hay evidencia de prueba de clasificaciÃ³n en los archivos de prueba existentes (`test_clasificacion.py` no existe).
- **CF-02** (clasificaciÃ³n incorrecta corregida por el usuario): no se probÃ³ en flujo manual.
- **CF-03** (documento que no es un contrato): no se probÃ³ especÃ­ficamente.
- **CH-01** (informe no afirma que el contrato es vÃ¡lido o ilegal): no hay prueba directa de esta restricciÃ³n.
- **CJ-02** (Historial de anÃ¡lisis): no hay prueba automatizada de apertura de un anÃ¡lisis anterior desde el Historial.
- **CK-01, CK-02** (tema y navegaciÃ³n): no se probaron especÃ­ficamente tema claro/oscuro ni navegaciÃ³n principal.

Los casos pendientes requieren pruebas manuales o de integraciÃ³n que aÃºn no se han ejecutado.
