# ---------------------------------------------------------------------------
# Este script solía instalar Ollama en rutas fijas de D:\. El proyecto
# MotorRevisionLegal usa llama-server (llama.cpp), no Ollama.
# No se realiza ninguna instalación automática. El usuario debe obtener
# llama-server y un modelo GGUF por su cuenta.
# ---------------------------------------------------------------------------
Write-Host "Este script está obsoleto: el proyecto usa llama-server (llama.cpp), no Ollama."
Write-Host "Obtenga llama-server y un modelo GGUF, luego arranque:"
Write-Host "  llama-server.exe -m 'C:\Modelos\modelo.gguf' --host 127.0.0.1 --port 9931 -c 2048"
Write-Host "Compruebe que responde: Invoke-RestMethod -Uri http://127.0.0.1:9931/v1/models"