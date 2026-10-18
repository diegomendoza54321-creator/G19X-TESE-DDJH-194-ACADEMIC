@echo off
if exist D:\Ollama\ollama.exe (
    echo OLLAMA_EXE_EXISTE
) else (
    echo OLLAMA_EXE_NO_EXISTE
)