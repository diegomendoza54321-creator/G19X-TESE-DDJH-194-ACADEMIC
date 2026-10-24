# Manual de Usuario

**Proyecto:** MotorRevisionLegal  
**Estado:** Completado para el flujo implementado en el prototipo. No incluye capturas de pantalla.

---

## 1. Introducción

MotorRevisionLegal es una herramienta web de revisión de cláusulas contractuales. Extrae el texto de un contrato, propone su tipo, permite confirmar o corregir esa clasificación y genera un informe de hallazgos respaldado por fragmentos del documento original. El acceso es privado y no existe registro público.

Los hallazgos son orientativos y requieren revisión humana. La herramienta no emite dictámenes jurídicos ni garantiza la validez de ningún contrato.

---

## 2. Acceso a la herramienta

1. Abra la dirección de la aplicación que le proporcione quien opere el servidor. En el entorno de desarrollo documentado, la interfaz está en `http://localhost:5173`.
2. En la pantalla de inicio de sesión, introduzca su **Usuario** y **Contraseña**.
3. Pulse **Iniciar sesión**.
4. Si las credenciales son correctas, se muestra la navegación principal. Si son incorrectas, se muestra el mensaje genérico `Usuario o contraseña incorrectos.` sin indicar qué campo falló.

No existe opción de registro público. Las cuentas las crea quien opera el servidor mediante `backend/crear_usuario.py`. Para cerrar la sesión, pulse **Cerrar sesión**.

---

## 3. Paso 1 — Cargar y extraer el contrato

1. En la navegación, pulse **Analizar contrato**.
2. En **Archivo del contrato**, seleccione un archivo PDF con texto seleccionable o DOCX (`.pdf`, `.docx`).
3. La interfaz muestra el nombre y el tamaño del archivo seleccionado.
4. Pulse **Extraer texto**.
5. Espere el mensaje de extracción. Si el proceso termina con éxito, se muestra:
   - **Formato** del documento.
   - **Páginas**, cuando el archivo es PDF.
   - El texto extraído en un cuadro de texto.
6. Si la extracción falla, se muestra un mensaje de error y no se entrega texto parcial. Compruebe que el PDF tenga texto seleccionable y no sea una imagen escaneada.

El backend valida el formato, el tamaño máximo configurado (10 MB en el código actual) y que el documento contenga texto legible.

---

## 4. Paso 2 — Confirmar el tipo de contrato

Tras extraer el texto, la aplicación propone un tipo de contrato de forma local y determinista, sin IA ni envío a terceros:

1. Se muestra la **Confianza** (Alta o Baja) y, cuando existen, **Evidencias en el texto**.
2. Si la confianza es baja, se advierte que las señales textuales son débiles o ambiguas y se solicita revisar manualmente.
3. Seleccione el tipo en **Seleccionar tipo de contrato**:
   - Prestación de servicios.
   - Proveedor.
4. Pulse **Confirmar tipo de contrato**.

La clasificación propuesta puede corregirse eligiendo el otro tipo antes de confirmar. Sin un tipo confirmado, el análisis no se inicia. Si la clasificación automática falla, se puede seleccionar el tipo manualmente.

---

## 5. Paso 3 — Analizar el contrato

1. Con el texto extraído y el tipo confirmado, pulse **Analizar cláusulas con IA local**.
2. El análisis usa el servidor de IA local del equipo y puede tardar varios minutos. No cierre la vista mientras se procesa.
3. Si el servidor local está ocupado o su estado no puede verificarse, se muestra un aviso; reintente cuando esté libre.
4. Pulse **Dejar de esperar** si desea dejar de aguardar la respuesta en pantalla.

Si el análisis falla, se muestra el motivo y no se registra un análisis en el Historial.

---

## 6. Revisar los resultados

Tras un análisis exitoso, los hallazgos se muestran en la sección **Analizar contrato**. Se agrupan por categoría; las categorías sin hallazgos se ocultan. Si no se identifican hallazgos, se indica que no se identificaron hallazgos con los criterios aplicados y que eso no garantiza que el contrato esté libre de problemas.

Por cada hallazgo se presenta:

- Tipo de hallazgo (posible ambigüedad, omisión, contradicción o riesgo).
- Categoría.
- Descripción.
- Cita textual del documento original.
- Explicación.
- Posible consecuencia.
- Recomendación.
- Limitaciones del análisis.

Si se descartaron citas que no existían literalmente en el texto, se informa cuántas. Al final se muestra un aviso de que el informe es automático, no constituye asesoría jurídica y debe revisarse por una persona con formación jurídica. El sistema no afirma que un contrato sea válido, legal ni que cumpla con la ley.

La sección **Resultados** forma parte de la navegación principal.

---

## 7. Consultar el Historial

1. Pulse **Historial** en la navegación.
2. Se cargan automáticamente los análisis del usuario autenticado, del más reciente al más antiguo.
3. Cada entrada muestra la fecha, el tipo de contrato confirmado, el número de hallazgos y la lista de hallazgos.
4. Si no hay análisis registrados, se indica que no hay análisis registrados todavía.
5. Si ocurre un error al cargar, se muestra un mensaje de error.

El Historial es privado: cada usuario ve únicamente sus propios análisis. No se almacena el archivo original del contrato ni su texto completo; solo metadatos y hallazgos.

---

## 8. Tema claro/oscuro y navegación

- La barra superior incluye el control de tema claro/oscuro.
- La preferencia se guarda en el navegador y se restaura al recargar la página. Sin preferencia guardada, se usa el tema del sistema.
- Cambiar el tema no cierra la sesión ni borra el trabajo en curso.
- La navegación principal incluye **Inicio**, **Analizar contrato**, **Resultados** e **Historial**.

---

## 9. Limitaciones de la herramienta

- Los hallazgos son orientativos y requieren revisión humana.
- La herramienta no determina la validez legal ni la ejecutabilidad de ningún contrato.
- Requiere archivos PDF con texto seleccionable. Los PDF escaneados sin capa de texto no están soportados.
- Si la extracción del texto falla o resulta incompleta, el análisis se detiene y no se generan hallazgos.
- El alcance inicial cubre contratos de prestación de servicios y de proveedores en español.
- El análisis puede tardar varios minutos porque se ejecuta en el equipo local.
- No existe descarga ni exportación del informe, ni compartición por correo.

---

## 10. Preguntas frecuentes

**¿Por qué no puedo crear una cuenta?** No existe registro público. Las cuentas las crea quien opera el servidor.

**¿Por qué el análisis tarda?** Porque se ejecuta contra el servidor de IA local del equipo.

**¿Qué hago si mi PDF no tiene texto?** Verifique que sea un PDF con texto seleccionable; los PDF escaneados no están soportados.

---

## 11. Contacto y soporte

El canal de soporte se definirá según la organización receptora; en esta entrega queda pendiente de asignación.

---

*Manual de usuario completado para el flujo implementado en el prototipo.*
