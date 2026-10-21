@echo off
REM ---------------------------------------------------------------------------
REM Este script solía verificar la presencia de Ollama en D:\Ollama\ollama.exe.
REM El proyecto MotorRevisionLegal usa llama-server (llama.cpp), no Ollama.
REM ---------------------------------------------------------------------------
echo Este script está obsoleto: el proyecto usa llama-server (llama.cpp), no Ollama.
echo Compruebe que llama-server responde en http://127.0.0.1:9931/v1/models
echo Ejemplo: curl http://127.0.0.1:9931/v1/models
pause