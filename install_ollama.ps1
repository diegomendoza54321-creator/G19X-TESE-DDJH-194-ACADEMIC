Start-Process -FilePath 'D:\OllamaSetup.exe' -ArgumentList '/DIR="D:\Ollama" /S' -Wait
if (Test-Path 'D:\Ollama\ollama.exe') {
    Write-Host 'INSTALADO OK'
} else {
    Write-Host 'INSTALACIÓN FALLÓ'
}