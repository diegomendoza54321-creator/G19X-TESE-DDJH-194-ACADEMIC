@echo off
REM ---------------------------------------------------------------------------
REM Este script solía instalar Ollama en rutas fijas de D:\. El proyecto
REM MotorRevisionLegal usa llama-server (llama.cpp), no Ollama.
REM No se realiza ninguna instalación automática. El usuario debe obtener
REM llama-server y un modelo GGUF por su cuenta.
REM ---------------------------------------------------------------------------
echo Este script está obsoleto: el proyecto usa llama-server (llama.cpp), no Ollama.
echo Obtenga llama-server y un modelo GGUF, luego arranque:
echo   llama-server.exe -m "C:\Modelos\modelo.gguf" --host 127.0.0.1 --port 9931 -c 2048
echo Compruebe que responde: curl.exe http://127.0.0.1:9931/v1/models
pause