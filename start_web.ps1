# Sales Coach Live - Script de Inicio
# Inicia tanto el backend como el frontend simultáneamente

param(
    [switch]$SkipBuild,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

Write-Host "🚀 Iniciando Sales Coach Live..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Función para verificar si un puerto está disponible
function Test-PortAvailable {
    param([int]$Port)
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $false
    } catch {
        return $true
    }
}

# Función para esperar a que un servicio esté disponible
function Wait-ForService {
    param([string]$Url, [string]$ServiceName, [int]$TimeoutSeconds = 30)
    Write-Host "⏳ Esperando a que $ServiceName esté disponible en $Url..." -ForegroundColor Yellow
    $startTime = Get-Date
    while (((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $ServiceName está disponible" -ForegroundColor Green
                return $true
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    }
    Write-Host "❌ Timeout esperando $ServiceName" -ForegroundColor Red
    return $false
}

# Verificar puertos disponibles
$backendPort = 8000
$frontendPort = 3000

if (-not $FrontendOnly) {
    if (-not (Test-PortAvailable -Port $backendPort)) {
        Write-Host "❌ Puerto $backendPort (Backend) ya está en uso" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ Puerto $backendPort (Backend) disponible" -ForegroundColor Green
    }
}

if (-not $BackendOnly) {
    if (-not (Test-PortAvailable -Port $frontendPort)) {
        Write-Host "❌ Puerto $frontendPort (Frontend) ya está en uso" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ Puerto $frontendPort (Frontend) disponible" -ForegroundColor Green
    }
}

# Función para ejecutar backend
function Start-Backend {
    Write-Host "🔧 Iniciando backend..." -ForegroundColor Cyan
    Set-Location "$PSScriptRoot\web\backend"

    # Verificar si existe el entorno virtual
    if (-not (Test-Path ".venv")) {
        Write-Host "📦 Creando entorno virtual para backend..." -ForegroundColor Yellow
        python -m venv .venv
    }

    # Activar entorno virtual
    & ".\.venv\Scripts\Activate.ps1"

    # Instalar dependencias
    Write-Host "📦 Instalando dependencias del backend..." -ForegroundColor Yellow
    pip install -r requirements.txt

    # Iniciar backend
    Write-Host "🚀 Ejecutando backend en http://localhost:$backendPort" -ForegroundColor Green
    uvicorn main:app --host 0.0.0.0 --port $backendPort --reload
}

# Función para ejecutar frontend
function Start-Frontend {
    Write-Host "🔧 Iniciando frontend..." -ForegroundColor Cyan
    Set-Location "$PSScriptRoot\web\frontend"

    # Instalar dependencias
    Write-Host "📦 Instalando dependencias del frontend..." -ForegroundColor Yellow
    npm install

    # Build si no se especifica SkipBuild
    if (-not $SkipBuild) {
        Write-Host "🔨 Construyendo frontend..." -ForegroundColor Yellow
        npm run build
    }

    # Iniciar frontend
    Write-Host "🚀 Ejecutando frontend en http://localhost:$frontendPort" -ForegroundColor Green
    npm run dev
}

# Ejecutar servicios según los parámetros
if ($BackendOnly) {
    Start-Backend
} elseif ($FrontendOnly) {
    Start-Frontend
} else {
    # Ejecutar ambos servicios en paralelo
    Write-Host "🔄 Iniciando backend y frontend en paralelo..." -ForegroundColor Magenta

    # Iniciar backend en background
    $backendJob = Start-Job -ScriptBlock ${function:Start-Backend}

    # Esperar un poco para que el backend inicie
    Start-Sleep -Seconds 5

    # Verificar que el backend esté disponible
    if (Wait-ForService -Url "http://localhost:$backendPort" -ServiceName "Backend API") {
        # Iniciar frontend
        Start-Frontend
    } else {
        Write-Host "❌ No se pudo iniciar el backend correctamente" -ForegroundColor Red
        Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
        exit 1
    }

    # Limpiar job cuando termine
    Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
}

Write-Host "🎉 ¡Sales Coach Live está ejecutándose!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host "🔗 Backend API: http://localhost:$backendPort" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:$backendPort/docs" -ForegroundColor Cyan
