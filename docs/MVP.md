# Alcance del MVP

**Proyecto:** MotorRevisionLegal  
**Versión:** 0.2 — Alineación con PRD v0.2 y requisitos v0.2  
**Estado:** En elaboración  
**Relación con otros documentos:** Este documento define el alcance de la primera versión funcional. El problema, los usuarios y los objetivos generales del producto están en [`PRD.md`](PRD.md). Los requisitos detallados están en [`requisitos.md`](requisitos.md).

---

## 1. Propósito de este documento

Define qué debe hacer el MVP, qué queda fuera, cuál es el flujo principal y cuándo puede considerarse terminado. Es el documento de referencia para decidir si una función entra o no en la primera versión.

---

## 2. Definición del MVP

El MVP es la primera versión funcional de la herramienta. Cubre el flujo completo de extremo a extremo: desde que el usuario inicia sesión hasta que consulta el informe de hallazgos en pantalla y el análisis queda registrado en su historial. No se trata de una versión experimental ni de alcance reducido por razones técnicas: es el producto funcionando dentro de las capacidades descritas en este documento.

---

## 3. Funciones incluidas en el MVP

### 3.1 Acceso privado

- El sistema requiere inicio de sesión con nombre de usuario y contraseña para acceder a cualquier función.
- Solo los usuarios con cuenta autorizada pueden entrar. No existe opción de registro público.
- Si las credenciales son incorrectas, el sistema muestra un mensaje de error genérico sin revelar qué campo específico falló.
- El mecanismo técnico de autenticación (sesiones, tokens u otro) está pendiente de definir. *(pendiente)*
- La creación y administración de cuentas autorizadas está pendiente de definir. *(pendiente)*

### 3.2 Interfaz: navegación y tema

- La navegación principal incluye: **Inicio**, **Analizar contrato**, **Resultados** e **Historial**. Las secciones **Cómo funciona** y **Criterios** pueden incluirse también.
- La interfaz ofrece **tema claro** y **tema oscuro**.
- La preferencia de tema se guarda en el navegador del usuario y se aplica automáticamente en visitas posteriores.
- El cambio de tema no interrumpe la sesión ni el flujo de trabajo en curso.

### 3.3 Carga del documento

- El usuario sube un archivo desde su dispositivo.
- Formatos aceptados: **PDF con texto seleccionable** y **DOCX**.
- El sistema confirma la carga exitosa con un mensaje visible.
- El sistema rechaza formatos no soportados con un mensaje claro.
- El tamaño máximo de archivo está pendiente de definir. *(pendiente)*

### 3.4 Extracción de texto

- El sistema extrae el texto completo del archivo cargado.
- Si la extracción **falla o resulta incompleta**, el sistema:
  - Muestra un mensaje de advertencia claro al usuario.
  - **Detiene el análisis.** No genera ni presenta hallazgos.
  - No ofrece continuar con una revisión parcial.
  - No simula haber leído el documento completo.
  - Indica al usuario que verifique que el PDF tenga texto seleccionable o que intente con otro archivo.

### 3.5 Clasificación del tipo de contrato (determinista y local)

- El sistema sugiere el tipo de contrato identificado: **prestación de servicios** o **proveedor**, mediante una clasificación local y determinista basada en señales textuales explicables del propio documento. **No usa IA ni envía el contrato a terceros.**
- La propuesta incluye una justificación breve basada en el texto del documento: cada evidencia es un fragmento literal verificado contra el texto extraído.
- Ante señales débiles o ambiguas (baja confianza), el sistema lo indica y pide revisión manual.
- El usuario revisa la propuesta y debe **confirmarla o corregirla** antes de que inicie el análisis.
- El usuario puede seleccionar el tipo correcto de una lista predefinida con los dos tipos acordados.
- El análisis no inicia sin esa confirmación.

> **Alcance:** Solo RF-03. El análisis (RF-04) y los criterios jurídicos siguen pendientes de sus decisiones y validación. La clasificación con IA externa queda pendiente de proveedor y autorización explícita.

### 3.6 Análisis del contrato

- Con el tipo confirmado, el sistema aplica una **lista de verificación base** y **criterios condicionales** según el tipo.
- El sistema identifica y reporta:
  - Posibles ambigüedades en la redacción.
  - Posibles omisiones de elementos típicos del tipo de contrato.
  - Posibles contradicciones aparentes entre cláusulas.
  - Posibles riesgos contractuales.

> **Nota:** Existe una propuesta inicial de criterios base y condicionales. Requiere validación con el tutor o con una persona con experiencia jurídica antes de considerarse definitiva. Esta validación debe completarse **antes de implementar el módulo de análisis**. *(pendiente)*

### 3.7 Informe de hallazgos

- El informe se presenta **en pantalla**.
- Por cada hallazgo, el informe muestra:
  - Cita textual del documento original (verificada contra el texto extraído).
  - Explicación del problema identificado.
  - Posible consecuencia.
  - Recomendación.
  - Limitaciones del análisis para ese hallazgo.
- **Solo se muestran las categorías que tengan al menos un hallazgo. Las categorías sin hallazgos se ocultan.** Si no se identificaron hallazgos en ninguna categoría, el informe muestra un mensaje general: "No se identificaron hallazgos con los criterios aplicados", sin garantizar que el contrato esté libre de problemas.
- El informe incluye un aviso visible y permanente de que no constituye asesoría jurídica.
- El sistema no genera citas que no existan en el documento analizado.
- Los resultados son orientativos y requieren revisión humana; no constituyen un dictamen jurídico.

### 3.8 Historial de análisis

- Cada análisis completado queda registrado y asociado al usuario autenticado que lo realizó.
- El usuario puede acceder a la sección Historial desde la navegación principal.
- El historial muestra los análisis realizados por ese usuario.
- El usuario puede abrir un análisis anterior y consultar su informe.
- El historial **no muestra ni permite descargar el archivo original del contrato**. No se asume que el archivo se guarda.
- El motor de base de datos, los campos exactos que se guardarán por cada análisis y la política de conservación de esos datos están pendientes de definir. *(pendiente)*

---

## 4. Funciones excluidas del MVP

Las siguientes funciones están fuera de alcance para la primera versión y se registran aquí para evitar que entren por expansión del alcance durante el desarrollo:

| Función excluida | Nota |
|---|---|
| Registro público de nuevos usuarios | El acceso es solo para cuentas autorizadas; el registro libre está fuera por diseño |
| Descarga o exportación del informe (PDF, DOCX u otro) | Fuera del MVP; puede incluirse en una versión posterior |
| Compartir el informe por correo u otro medio | Fuera del MVP |
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
2. El sistema muestra la pantalla de inicio de sesión.
        │
3. El usuario introduce sus credenciales. Si son incorrectas → mensaje de error. Fin del flujo.
        │
4. El usuario accede a la pantalla de inicio de la herramienta.
        │
5. El usuario navega a "Analizar contrato" y carga un archivo PDF o DOCX.
        │
6. El sistema extrae el texto.
        │
        ├─ Si falla o está incompleto → aviso + detención. Fin del flujo.
        │
7. La IA propone el tipo de contrato con justificación breve.
        │
8. El usuario confirma o corrige la clasificación.
        │
9. El sistema aplica la lista de verificación al tipo confirmado.
        │
10. La IA analiza el texto y genera hallazgos estructurados.
        │
11. El sistema verifica que cada cita exista en el texto original.
        │
12. El sistema construye el informe y lo presenta en pantalla.
        │
13. El análisis queda registrado en el historial del usuario.
        │       Los campos exactos y la política de conservación están pendientes de definir.
        │       El archivo original no se asume guardado.
        │
14. El usuario lee el informe y aplica su propio criterio.
        │
15. El usuario puede consultar el análisis posterior desde la sección Historial.
```

---

## 6. Decisiones pendientes que afectan el MVP

Estas decisiones no están resueltas. No deben asumirse como tomadas ni implementarse sin confirmación:

| Decisión | Impacto en el MVP |
|---|---|
| Mecanismo técnico de autenticación (sesiones, JWT u otro) | Define cómo se implementa el inicio de sesión y la gestión de la sesión activa |
| Creación y administración de cuentas autorizadas | Define quién crea cuentas, cómo y con qué herramienta |
| Selección del proveedor de IA (privacidad, costo, políticas) | Define la arquitectura del módulo de análisis (RF-04); la clasificación de tipo de contrato (RF-03) es local y determinista, sin IA ni envío de texto a terceros. No asumir envío de contratos a servicios externos sin autorización. |
| Validación jurídica de la lista de criterios de revisión | Define qué busca el sistema en cada tipo de contrato; prerrequisito del módulo de análisis |
| Motor de base de datos para historial y cuentas | Define la tecnología de persistencia |
| Campos exactos que guardará el historial y política de conservación | Define qué datos se almacenan y por cuánto tiempo |
| Política de almacenamiento y eliminación del documento cargado | Define si el archivo se descarta al finalizar el análisis o se retiene |
| Tamaño máximo de archivo aceptado | Afecta al mensaje de rechazo y a la infraestructura |
| Estrategia de despliegue (entorno, infraestructura, dominio) | Define dónde y cómo se ejecuta el sistema |

---

## 7. Criterios de aceptación del MVP

El MVP se considera funcionando cuando cumple **todos** los criterios siguientes:

### Acceso
- [ ] La pantalla de inicio de sesión se muestra antes de acceder a cualquier función.
- [ ] Un usuario con credenciales correctas puede iniciar sesión y acceder a la herramienta.
- [ ] Un usuario con credenciales incorrectas recibe un mensaje de error genérico y no accede.
- [ ] No existe opción de registro público.

### Interfaz
- [ ] La navegación incluye Inicio, Analizar contrato, Resultados e Historial.
- [ ] El usuario puede cambiar entre tema claro y oscuro.
- [ ] La preferencia de tema se mantiene al recargar la página o en visitas posteriores.

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
- [ ] Solo se muestran las categorías con hallazgos; las categorías vacías se ocultan. Si no hay hallazgos en ninguna categoría, el informe muestra el mensaje: "No se identificaron hallazgos con los criterios aplicados", sin garantizar que el contrato esté libre de problemas.
- [ ] El informe incluye un aviso visible de que no constituye asesoría jurídica.
- [ ] El informe no afirma que el contrato "es válido", "es legal" ni "cumple con la ley".

### Historial
- [ ] Tras completar un análisis, este aparece en la sección Historial del usuario.
- [ ] El usuario puede abrir un análisis anterior desde el Historial y consultar su informe.
- [ ] El Historial no muestra ni permite descargar el archivo original del contrato.
- [ ] El Historial de un usuario no muestra análisis de otros usuarios.

### General
- [ ] La interfaz y todos los mensajes están en español.
- [ ] El flujo completo (inicio de sesión → carga → extracción → clasificación → confirmación → análisis → informe → registro en historial) funciona sin errores no controlados para un contrato de prestación de servicios y para uno de proveedor.

---

## 8. Condiciones para considerar terminado el MVP

El MVP se considera **terminado** cuando:

1. Todos los criterios de aceptación de la sección 7 están verificados con contratos de prueba reales o sintéticos.
2. El plan de pruebas ([`plan-de-pruebas.md`](plan-de-pruebas.md)) ha sido ejecutado y los resultados están registrados.
3. La lista de criterios de revisión base y condicional ha sido validada con el tutor o con una persona con experiencia jurídica. **Esta validación es un prerrequisito para implementar el módulo de análisis; debe completarse antes de ese módulo, no solo antes de declarar el MVP terminado.** Existe una propuesta inicial pendiente de esa revisión.
4. Las decisiones de persistencia del historial (motor de base de datos, campos, política de conservación) han sido definidas e implementadas.
5. El sistema está desplegado en un entorno al que el evaluador pueda acceder con una cuenta autorizada.
6. Los entregables de acceso de prueba y evidencias (capturas o video) están disponibles.

> Ninguna de estas condiciones está cumplida todavía. El estado actual es: documentación en elaboración, implementación no iniciada.

---

*Este documento es un borrador sujeto a revisión y validación con el tutor de residencias y la organización receptora.*
