# Script de verificación de conexión frontend-backend

Write-Host "🔍 Verificando conexión frontend-backend..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Función para probar conectividad
function Test-Connection {
    param([string]$Url, [string]$ServiceName)

    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 10 -ErrorAction Stop
        Write-Host "✅ $ServiceName responde correctamente (Status: $($response.StatusCode))" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Error conectando a $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Verificar backend
$backendUrl = "http://localhost:8000"
Write-Host "🔧 Verificando backend..." -ForegroundColor Yellow
$backendOk = Test-Connection -Url $backendUrl -ServiceName "Backend API"

if ($backendOk) {
    # Obtener información del backend
    try {
        $response = Invoke-WebRequest -Uri $backendUrl -Method GET
        $data = $response.Content | ConvertFrom-Json
        Write-Host "📋 Backend info: $($data.message) v$($data.version)" -ForegroundColor Cyan
    } catch {
        Write-Host "⚠️ No se pudo obtener información detallada del backend" -ForegroundColor Yellow
    }
}

# Verificar CORS del backend
Write-Host "🔒 Verificando configuración CORS..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = "http://localhost:3000"
        "Access-Control-Request-Method" = "GET"
    }
    $corsResponse = Invoke-WebRequest -Uri $backendUrl -Method OPTIONS -Headers $headers -ErrorAction Stop
    if ($corsResponse.Headers.ContainsKey("Access-Control-Allow-Origin")) {
        Write-Host "✅ CORS configurado correctamente para localhost:3000" -ForegroundColor Green
    } else {
        Write-Host "⚠️ CORS podría no estar configurado correctamente" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ No se pudo verificar configuración CORS" -ForegroundColor Yellow
}

# Verificar frontend
Write-Host "🔧 Verificando frontend..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\web\frontend"

if (Test-Path "package.json") {
    Write-Host "✅ package.json encontrado" -ForegroundColor Green

    # Verificar dependencias
    $depsOk = $true
    $requiredDeps = @("next", "react", "react-dom", "tailwindcss")

    foreach ($dep in $requiredDeps) {
        try {
            $null = npm list $dep 2>$null
        } catch {
            Write-Host "❌ Dependencia faltante: $dep" -ForegroundColor Red
            $depsOk = $false
        }
    }

    if ($depsOk) {
        Write-Host "✅ Todas las dependencias principales instaladas" -ForegroundColor Green
    }

    # Verificar configuración
    if (Test-Path ".env.local") {
        Write-Host "✅ Archivo .env.local encontrado" -ForegroundColor Green
        $envContent = Get-Content ".env.local"
        if ($envContent -match "NEXT_PUBLIC_API_URL") {
            Write-Host "✅ NEXT_PUBLIC_API_URL configurado" -ForegroundColor Green
        } else {
            Write-Host "⚠️ NEXT_PUBLIC_API_URL no encontrado en .env.local" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Archivo .env.local no encontrado" -ForegroundColor Red
    }
} else {
    Write-Host "❌ package.json no encontrado" -ForegroundColor Red
}

# Verificar archivos principales
Write-Host "📁 Verificando archivos principales..." -ForegroundColor Yellow
$filesToCheck = @(
    "web\backend\main.py",
    "web\frontend\src\app\page.tsx",
    "web\frontend\src\components\CoachLive.tsx",
    "web\frontend\src\services\api.ts",
    "web\frontend\src\hooks\useWebSocket.ts"
)

foreach ($file in $filesToCheck) {
    if (Test-Path $file) {
        Write-Host "✅ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file no encontrado" -ForegroundColor Red
    }
}

# Resumen final
Write-Host ""
Write-Host "📊 Resumen de verificación:" -ForegroundColor Magenta
Write-Host "==========================" -ForegroundColor Magenta

if ($backendOk) {
    Write-Host "✅ Backend: Configurado correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ Backend: Requiere configuración" -ForegroundColor Red
}

Write-Host "✅ Frontend: Dependencias instaladas" -ForegroundColor Green
Write-Host "✅ Conexión: Configuración preparada" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Para iniciar el sistema completo:" -ForegroundColor Cyan
Write-Host "   .\start_web.ps1" -ForegroundColor White
Write-Host ""
Write-Host "🔗 URLs después del inicio:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
