@echo off
D:\OllamaSetup.exe /DIR="D:\Ollama" /S
if exist D:\Ollama\ollama.exe (
    echo INSTALADO OK
) else (
    echo INSTALACION FALLO
)