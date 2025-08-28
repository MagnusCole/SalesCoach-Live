#!/bin/bash

# Sales Coach Live - Script de Inicio
# Inicia tanto el backend como el frontend

echo "🚀 Iniciando Sales Coach Live..."
echo "================================"

# Función para verificar si un puerto está disponible
check_port() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Puerto $port ($name) ya está en uso"
        return 1
    else
        echo "✅ Puerto $port ($name) disponible"
        return 0
    fi
}

# Verificar puertos disponibles
echo "🔍 Verificando puertos disponibles..."
check_port 8000 "Backend API" || exit 1
check_port 3000 "Frontend Web" || exit 1
echo ""

# Verificar variables de entorno
echo "🔧 Verificando configuración..."
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado. Copiando .env.example..."
    cp .env.example .env
    echo "✏️  Edita el archivo .env con tus claves API antes de continuar"
    echo ""
fi

# Función para iniciar backend
start_backend() {
    echo "🔧 Iniciando backend..."
    cd web/backend

    # Verificar si existe entorno virtual
    if [ ! -d "venv" ]; then
        echo "📦 Creando entorno virtual para backend..."
        python -m venv venv
    fi

    # Activar entorno virtual
    source venv/bin/activate

    # Instalar dependencias si es necesario
    if [ ! -f "venv/installed" ]; then
        echo "📦 Instalando dependencias del backend..."
        pip install -r requirements.txt
        touch venv/installed
    fi

    # Iniciar backend
    echo "🌐 Iniciando servidor backend en http://localhost:8000"
    python main.py &
    BACKEND_PID=$!
    cd ../..
    echo "✅ Backend iniciado (PID: $BACKEND_PID)"
}

# Función para iniciar frontend
start_frontend() {
    echo "🔧 Iniciando frontend..."
    cd web/frontend

    # Instalar dependencias si es necesario
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependencias del frontend..."
        npm install
    fi

    # Iniciar frontend
    echo "🌐 Iniciando servidor frontend en http://localhost:3000"
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
    echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
}

# Función para manejar señales de interrupción
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend detenido"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend detenido"
    fi
    echo "👋 ¡Hasta luego!"
    exit 0
}

# Configurar handler de señales
trap cleanup SIGINT SIGTERM

# Iniciar servicios
start_backend
echo ""
start_frontend
echo ""

# Esperar un poco para que los servicios inicien
sleep 3

# Verificar que los servicios están corriendo
echo "🔍 Verificando servicios..."
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Backend API: http://localhost:8000"
    echo "   📖 Documentación: http://localhost:8000/docs"
else
    echo "❌ Backend API no responde"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend Web: http://localhost:3000"
else
    echo "❌ Frontend Web no responde"
fi

echo ""
echo "🎉 ¡Sales Coach Live está listo!"
echo "================================"
echo "📱 Abre tu navegador en: http://localhost:3000"
echo "📡 Backend API: http://localhost:8000"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"

# Mantener el script corriendo
wait
