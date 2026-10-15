# PRD — Documento de Requisitos del Producto

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.2 — Actualización de alcance  
**Estado:** En elaboración

---

## 1. Problema que se busca resolver

La revisión de contratos de prestación de servicios y de proveedores es una tarea que requiere tiempo, experiencia jurídica y atención al detalle. Personas que participan en la contratación (coordinadores de compras, responsables de área, emprendedores, equipos sin acceso inmediato a un abogado) pueden pasar por alto cláusulas ambiguas, omisiones relevantes o riesgos contractuales que solo son evidentes con una lectura sistemática.

**Brecha identificada:** No existe, en el entorno de la organización objetivo, una herramienta accesible que guíe la revisión contractual de forma estructurada, en español, y que genere observaciones respaldadas en el texto del propio documento.

---

## 2. Usuarios previstos

El acceso a la herramienta es privado: solo pueden utilizarla personas con una cuenta autorizada. No existe registro público. La creación y administración de cuentas está pendiente de definir.

| Perfil | Descripción | Necesidad principal |
|---|---|---|
| Coordinador de compras / adquisiciones | Gestiona contratos con proveedores de bienes y servicios | Identificar cláusulas de riesgo antes de firmar |
| Responsable de área | Firma o avala contratos operativos | Comprender el alcance de sus obligaciones |
| Profesional jurídico de apoyo | Realiza revisiones formales | Contar con un primer análisis estructurado que ahorre tiempo |
| Usuario con acceso autorizado sin formación jurídica | Necesita entender un contrato que le afecta directamente | Recibir explicaciones claras y señalamientos concretos |

> **Nota:** Los perfiles exactos y su prioridad deben validarse con el cliente o la institución receptora de la residencia.

---

## 3. Objetivos del producto

### Objetivo principal

Proporcionar un análisis estructurado de contratos de prestación de servicios y de proveedores que ayude al usuario a identificar puntos de atención antes de tomar una decisión, sin reemplazar el juicio de un profesional jurídico.

### Objetivos específicos

1. Extraer el texto del contrato desde formatos PDF (texto seleccionable) y DOCX.
2. Clasificar el tipo de contrato y presentar esa clasificación al usuario para confirmación o corrección.
3. Aplicar una lista de verificación adaptada al tipo de contrato clasificado.
4. Identificar y reportar posibles ambigüedades, omisiones, contradicciones aparentes y riesgos.
5. Respaldar cada hallazgo con una cita textual del documento original.
6. Presentar recomendaciones claras, con sus limitaciones explícitas.
7. Presentar el informe en pantalla para que el usuario pueda consultarlo durante la sesión. La descarga o el envío del informe quedan fuera del MVP.

---

## 4. Alcance del producto

### Incluido en el alcance inicial

- Análisis de contratos de **prestación de servicios** y contratos de **proveedores**.
- Formatos de entrada: **PDF con texto seleccionable** y **DOCX**.
- Idioma de los contratos: **español**.
- Acceso privado mediante nombre de usuario y contraseña. No existe registro público; solo acceden cuentas autorizadas.
- Interfaz web con navegación que incluye: Inicio, Analizar contrato, Resultados e Historial. Pueden incluirse también Cómo funciona y Criterios.
- Tema claro y oscuro con memoria de la preferencia en el navegador del usuario.
- Generación de un informe de hallazgos en pantalla.
- Historial de análisis anteriores. El historial es parte del alcance; permitirá consultar análisis realizados previamente. El motor de base de datos, los campos exactos que se guardarán y la política de conservación de esos datos están pendientes de definir. El archivo original del contrato no se asume guardado.

### Excluido del alcance inicial

- Análisis de contratos en otros idiomas.
- Contratos distintos a los tipos mencionados (arrendamiento, laboral, compraventa, etc.).
- PDF escaneados sin capa de texto (sin OCR integrado en la primera versión).
- Descarga o exportación del informe (PDF, DOCX u otro formato).
- Compartir el informe por correo u otro medio.
- Firma electrónica o gestión de contratos.
- Comparación entre versiones de un contrato.
- Integración con sistemas ERP, gestores documentales u otras plataformas externas.
- Asesoría jurídica o emisión de opiniones legales vinculantes.
- Generación automática de cláusulas o redacción de contratos.

---

## 5. Definición propuesta del MVP

El MVP debe demostrar el flujo completo de extremo a extremo con las funciones esenciales:

1. El usuario inicia sesión con su cuenta autorizada.
2. El usuario carga un contrato (PDF con texto seleccionable o DOCX).
3. El sistema extrae el texto del documento. Si la extracción falla o es incompleta, detiene el proceso y avisa.
4. El sistema propone el tipo de contrato con una justificación breve.
5. El usuario confirma o corrige la clasificación.
6. El sistema aplica la lista de verificación correspondiente al tipo confirmado.
7. El sistema genera un informe con hallazgos, citas textuales, explicación, consecuencia posible, recomendación y limitaciones. Las categorías sin hallazgos se ocultan.
8. El usuario puede leer el informe en pantalla.
9. El análisis queda registrado en el historial del usuario. Los campos exactos que se guardan y la política de conservación están pendientes de definir; el archivo original del contrato no se asume guardado.

**Fuera del MVP:** exportación del informe, múltiples idiomas, soporte para PDF escaneados, comparación de versiones, integración con sistemas externos.

> La definición del MVP está sujeta a validación con el tutor de residencias y la organización receptora.

---

## 6. Historias de usuario

### HU-00 — Acceder a la herramienta

> Como usuario con cuenta autorizada, quiero iniciar sesión con mi nombre de usuario y contraseña para acceder a la herramienta de forma segura.

**Criterios de aceptación:**
- El sistema presenta una pantalla de inicio de sesión con campos de nombre de usuario y contraseña.
- Solo los usuarios con cuenta autorizada pueden acceder. No existe opción de registro público.
- Si las credenciales son incorrectas, el sistema muestra un mensaje de error sin revelar qué campo falló.
- Tras un inicio de sesión exitoso, el usuario accede a la pantalla de inicio de la herramienta.
- El mecanismo técnico de autenticación (sesiones, tokens, etc.) está pendiente de definir.

---

### HU-01 — Cargar contrato

> Como usuario, quiero cargar un archivo PDF o DOCX con el contrato que necesito revisar, para que el sistema pueda analizarlo.

**Criterios de aceptación:**
- El sistema acepta archivos PDF con texto seleccionable y archivos DOCX.
- El sistema rechaza archivos con formato no soportado e informa al usuario.
- El sistema muestra un mensaje de confirmación al completar la carga.
- El tamaño máximo del archivo se define durante el desarrollo. *(pendiente)*

---

### HU-02 — Confirmar la clasificación del contrato

> Como usuario, quiero que el sistema me proponga el tipo de contrato identificado y pueda confirmar o corregir esa clasificación antes de que se apliquen los criterios de revisión.

**Criterios de aceptación:**
- El sistema muestra la clasificación propuesta con una justificación breve basada en el texto del documento.
- El usuario puede aceptar la clasificación con un clic.
- El usuario puede seleccionar un tipo diferente de una lista predefinida.
- El análisis no inicia hasta que el usuario confirme o corrija la clasificación.

---

### HU-03 — Recibir el informe de hallazgos

> Como usuario, quiero recibir un informe que detalle los posibles problemas identificados en el contrato, respaldados por citas del documento, para poder tomar decisiones informadas.

**Criterios de aceptación:**
- Cada hallazgo incluye: descripción, cita textual del documento, explicación, posible consecuencia, recomendación y limitaciones del análisis.
- En el informe solo se muestran las categorías que tengan al menos un hallazgo. Las categorías sin hallazgos se ocultan. Si no se identificaron hallazgos en ninguna categoría, el informe muestra un mensaje general: "No se identificaron hallazgos con los criterios aplicados", sin garantizar que el contrato esté libre de problemas.
- El informe incluye una advertencia explícita de que no constituye asesoría jurídica.
- El sistema no genera citas que no existan en el documento original.

---

### HU-04 — Entender las limitaciones del análisis

> Como usuario, quiero que el sistema me indique claramente cuándo un hallazgo tiene limitaciones, para no interpretar el informe como una opinión jurídica definitiva.

**Criterios de aceptación:**
- Cada hallazgo incluye una sección de limitaciones.
- El informe incluye un aviso general visible sobre el alcance de la herramienta.
- El sistema no afirma que un contrato "es válido" ni que "cumple con la ley".

---

### HU-05 — Manejar un documento con extracción fallida o incompleta

> Como usuario, quiero que el sistema me informe si no pudo extraer el texto del documento y detenga el proceso, para no recibir un análisis basado en información incompleta o inexistente.

**Criterios de aceptación:**
- Si la extracción de texto falla o resulta incompleta, el sistema muestra un mensaje de advertencia claro.
- El sistema detiene el análisis; no genera ni presenta hallazgos a partir de un texto que no pudo extraerse correctamente.
- El sistema no ofrece continuar con una revisión parcial ni presenta resultados como si hubiera analizado el documento completo.
- El mensaje indica al usuario que puede intentar con un archivo diferente o verificar que el PDF tenga texto seleccionable.

---

### HU-06 — Consultar el historial de análisis

> Como usuario, quiero consultar mis análisis anteriores desde la sección Historial, para poder revisar resultados previos sin tener que cargar el contrato de nuevo.

**Criterios de aceptación:**
- El usuario puede acceder a la sección Historial desde la navegación principal.
- El historial muestra los análisis realizados por ese usuario.
- El usuario puede abrir un análisis anterior y consultar su informe.
- El historial no muestra ni permite descargar el archivo original del contrato.

> **Diseño pendiente:** los campos exactos que se guardan por cada análisis, el motor de base de datos y la política de conservación de esos datos están pendientes de definir antes de implementar este módulo.

---

### HU-07 — Elegir entre tema claro y oscuro

> Como usuario, quiero poder cambiar entre tema claro y oscuro, y que la herramienta recuerde mi elección, para trabajar con la apariencia que prefiero.

**Criterios de aceptación:**
- La interfaz ofrece la opción de cambiar entre tema claro y oscuro.
- La preferencia se guarda en el navegador del usuario y se aplica automáticamente en visitas posteriores.
- El cambio de tema no interrumpe la sesión ni el flujo de trabajo en curso.

---

## 7. Restricciones

- El sistema no puede almacenar los documentos de los usuarios sin su consentimiento explícito. *(política pendiente de definir)*
- El sistema no puede afirmar la legalidad de un contrato ni emitir opiniones jurídicas vinculantes.
- El uso de APIs de terceros para IA está sujeto a la política de privacidad de la organización receptora. *(pendiente de validar)*
- El presupuesto para APIs de IA es desconocido. *(pendiente)*

---

## 8. Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación propuesta |
|---|---|---|---|
| La API de IA elegida no cumple con las políticas de privacidad de la organización | Media | Alto | Evaluar alternativas locales o con mayor control de datos antes de iniciar la implementación |
| Se envían contratos reales con información confidencial a un servicio externo sin autorización | Media | Alto | No asumir que el texto puede enviarse a servicios externos; validar con la organización antes de elegir proveedor de IA |
| Los PDF entregados en producción son escaneados sin OCR | Alta | Medio | Informar al usuario y planificar OCR para una versión posterior |
| Los hallazgos del sistema son malinterpretados como asesoría jurídica | Media | Alto | Avisos explícitos en la interfaz y en cada hallazgo |
| El alcance crece durante el desarrollo (scope creep) | Media | Medio | Definir el MVP con precisión y mantener un backlog separado |
| Calidad variable de los contratos reales de prueba | Alta | Medio | Diseñar casos de prueba propios con contratos sintéticos |
| El historial se implementa sin definir qué datos guarda ni su política de conservación | Media | Medio | Resolver las decisiones de persistencia antes de implementar el módulo de historial |

---

## 9. Decisiones pendientes

- [ ] Validar la API de IA: privacidad, costo por token, política de retención de datos, disponibilidad. No asumir que los contratos pueden enviarse a servicios externos sin autorización.
- [ ] Mecanismo técnico de autenticación (sesiones, JWT u otro). La autenticación con usuario y contraseña está confirmada; el mecanismo de implementación no.
- [ ] Creación y administración de cuentas autorizadas: quién las crea, cómo y con qué herramienta.
- [ ] Motor de base de datos para persistencia del historial y las cuentas.
- [ ] Datos exactos que guardará el historial por cada análisis y política de conservación.
- [ ] Política de almacenamiento y eliminación de los documentos cargados.
- [ ] Validar con el tutor o con una persona con experiencia jurídica la lista de criterios de revisión base y condicional propuesta para cada tipo de contrato (prestación de servicios y proveedores). **Esta validación debe completarse antes de implementar el módulo de análisis.**
- [ ] Tamaño máximo de archivo aceptado.
- [ ] Estrategia de despliegue (entorno, infraestructura, dominio).

---

*Este documento es un borrador inicial sujeto a revisión y validación.*
