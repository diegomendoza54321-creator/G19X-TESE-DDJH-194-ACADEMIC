# Evidencia de instalación limpia y validación funcional

**Fecha:** 4 de noviembre de 2026

## Entorno de prueba

- Carpeta de trabajo: MotorRevisionLegal (clon del repositorio).
- Sistema operativo: Windows.
- Python: 3.14.4
- Node.js: v24.22.0
- Commit validado: `7fa1c6b`

## Comandos ejecutados y resultados observados

1. `git clone <repositorio> MotorRevisionLegal-clean-install`
   - Resultado: repositorio clonado correctamente.

2. `git rev-parse --short HEAD`
   - Resultado: `7fa1c6b`

3. `py -3.14 -m venv .venv`
   - Resultado: entorno virtual creado.

4. `.venv\Scripts\python.exe -m pip install -r backend\requirements.txt`
   - Resultado: dependencias instaladas sin errores.

5. `.venv\Scripts\python.exe -m pytest backend -q`
   - Resultado: 102 pruebas aprobadas (`[100%]`).

## Ejecución de llama-server

- Ruta: `D:\llama.cpp\llama-server.exe`
- Modelo: `D:\Modelos\Phi-3-mini-4k-instruct-q4.gguf`
- Comando: `D:\llama.cpp\llama-server.exe -m D:\Modelos\Phi-3-mini-4k-instruct-q4.gguf --host 127.0.0.1 --port 9931 -c 2048`
- Evidencia: `GET http://127.0.0.1:9931/v1/models` respondió correctamente y el modelo quedó cargado.

## Validación funcional

### Login

- `POST /login` con usuario `testuser`
- Resultado: `{"ok": true, "usuario": "testuser", "codigo": null, "motivo": null}` (HTTP 200).

### Análisis

- `POST /analizar-con-ia` con contrato sintético:
  - Texto: "CONTRATO SINTETICO DE PRUEBA. El proveedor entregara los bienes en 30 dias. El cliente pagara al recibir. No se establece penalidad por retraso."
  - Tipo confirmado: `proveedor`
- Resultado: HTTP 200, 1 hallazgo válido:
  - Tipo: `riesgo`
  - Categoría: `Plazos de entrega`
  - Cita: `El proveedor entregara los bienes en 30 dias.`
  - `num_descartados`: 0

### Historial

- `GET /historial`
- Resultado: HTTP 200, 1 registro con el hallazgo anterior.

## Notas

- No se modificó código ni otros documentos durante esta evidencia.
- No se realizó stage, commit ni push.
- La evidencia cubre instalación limpia, commit identificado, llama-server, análisis real con hallazgos y Historial visible vía API.
