# Script para iniciar solo el backend de Sales Coach Live

Write-Host "🔧 Iniciando backend de Sales Coach Live..." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Verificar si estamos en el directorio correcto
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Error: requirements.txt no encontrado. Ejecuta este script desde web\backend\" -ForegroundColor Red
    exit 1
}

# Verificar si el puerto 8000 está disponible
$connection = New-Object System.Net.Sockets.TcpClient
try {
    $connection.Connect("localhost", 8000)
    $connection.Close()
    Write-Host "❌ Puerto 8000 ya está en uso" -ForegroundColor Red
    exit 1
} catch {
    Write-Host "✅ Puerto 8000 disponible" -ForegroundColor Green
}

# Crear entorno virtual si no existe
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activar entorno virtual
Write-Host "🔄 Activando entorno virtual..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Instalar dependencias
Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

# Iniciar backend
Write-Host "🚀 Iniciando backend en http://localhost:8000" -ForegroundColor Green
Write-Host "📚 API Docs disponible en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
