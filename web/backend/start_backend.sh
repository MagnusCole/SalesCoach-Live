#!/bin/bash

# Script para iniciar solo el backend de Sales Coach Live

echo "🔧 Iniciando backend de Sales Coach Live..."
echo "==========================================="

# Verificar si estamos en el directorio correcto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt no encontrado. Ejecuta este script desde web/backend/"
    exit 1
fi

# Verificar si el puerto 8000 está disponible
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Puerto 8000 ya está en uso"
    exit 1
else
    echo "✅ Puerto 8000 disponible"
fi

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source .venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Iniciar backend
echo "🚀 Iniciando backend en http://localhost:8000"
echo "📚 API Docs disponible en: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
