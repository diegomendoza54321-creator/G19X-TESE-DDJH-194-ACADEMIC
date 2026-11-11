Validación de instalación siguiendo README

Fecha: 2026-11-10



Commit validado

5dc27205e28b729ce272bb22cda8814ab4e58ed9



Entorno de validación

Carpeta nueva:



D:\\validacion-corte8



Repositorio clonado:



G19X-TESE-DDJH-194-ACADEMIC



Procedimiento realizado

Creación de carpeta nueva sin .venv, node\_modules ni base SQLite previa.

Git clone del repositorio.

Creación del entorno virtual con Python 3.14.

Instalación de dependencias backend.

Copia de .env.example a .env.

Creación de usuario mediante crear\_usuario.py.

Arranque de backend con uvicorn.

Arranque de frontend con Vite.

Arranque de llama-server con Phi-3.

Inicio de sesión desde la interfaz.

Carga de contrato DOCX.

Extracción de texto.

Clasificación del contrato.

Análisis con IA local.

Verificación de Resultados.

Verificación de Historial.

Resultado

✅ Inicio de sesión correcto.



✅ Extracción de texto correcta.



✅ Clasificación correcta.



✅ Análisis con IA local ejecutado correctamente.



✅ Hallazgos visibles en Resultados.



✅ Registro visible en Historial.



✅ Flujo realizado desde la interfaz web.



✅ README suficiente para reproducir la instalación.



Evidencia capturada

Backend operativo.

llama-server operativo.

Inicio de sesión.

Análisis realizado.

Resultados visibles.

Historial visible.

Conclusión

La instalación fue reproducida en una carpeta nueva siguiendo el README. El sistema permitió iniciar sesión, analizar un contrato desde la interfaz, visualizar hallazgos en Resultados y verificar el análisis en Historial.

