# 🚀 Guía de Inicio Rápido - Sales Coach Live

¡Felicidades! Has implementado completamente la interfaz web para el sistema de coaching de ventas. Esta guía te ayudará a probar que todo funciona correctamente.

## ✅ Checklist de Verificación

### 1. **Configuración del Entorno**
```bash
# Verificar que tienes las dependencias necesarias
python --version  # Debe ser 3.8+
node --version    # Debe ser 18+
npm --version     # Debe estar instalado
```

### 2. **Configurar Variables de Entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus claves API
# DEEPGRAM_API_KEY=tu_clave_aqui
# OPENAI_API_KEY=tu_clave_aqui (opcional)
```

### 3. **Probar Sistema Base**
```bash
# Probar que el sistema Python funciona
python test_system.py

# Si todo está bien, deberías ver:
# ✅ Configuración importada
# ✅ Servicio de transcripción importado
# ✅ Servicio de almacenamiento importado
# ✅ Exportador de transcripciones importado
# ✅ Analizador de llamadas importado
# ✅ Servicio de objeciones importado
# ✅ Entidades del dominio importadas
# 🎉 Todas las importaciones funcionan correctamente!
```

### 4. **Iniciar la Interfaz Web**
```bash
# Opción A: Script automático (recomendado)
chmod +x start_web.sh
./start_web.sh

# Opción B: Manual
# Terminal 1 - Backend
cd web/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Terminal 2 - Frontend
cd web/frontend
npm install
npm run dev
```

### 5. **Verificar Servicios**
```bash
# Backend API (debe responder)
curl http://localhost:8000

# Frontend Web (debe cargar)
curl http://localhost:3000

# Documentación API
open http://localhost:8000/docs
```

## 🎯 Prueba de Funcionalidades

### **Paso 1: Abrir la Interfaz**
1. Abre tu navegador: http://localhost:3000
2. Deberías ver la interfaz "Sales Coach Live"
3. Verifica que aparezca "Desconectado" inicialmente

### **Paso 2: Probar Conexión**
1. Presiona "Iniciar Grabación"
2. Deberías ver:
   - Estado cambiar a "Conectado"
   - Call ID generado
   - Backend iniciar transcripción

### **Paso 3: Probar Transcripción**
1. Habla por tu micrófono
2. Deberías ver texto aparecer en < 1 segundo
3. Prueba decir frases de prueba

### **Paso 4: Probar Detección de Objeciones**
Di frases como:
- "Es muy caro para mi presupuesto"
- "Ahora no tengo tiempo"
- "Tengo que consultarlo con mi jefe"
- "Ya trabajo con otra empresa"

Deberías ver:
- Objeción resaltada en rojo en < 1.5s
- Chip de objeción aparecer en panel izquierdo
- Sugerencia de respuesta aparecer

### **Paso 5: Probar Controles**
1. **Toggle Coach**: Activar/desactivar modo coach
2. **Selector de Modelo**: Cambiar modelo de IA
3. **Detener Grabación**: Finalizar sesión

## 📊 Verificar Rendimiento

### **Latencias Objetivo**
- ✅ Primera palabra: < 1 segundo
- ✅ Objeción resaltada: < 1.5 segundos
- ✅ Sugerencia mostrada: < 2 segundos

### **Cómo Medir**
```bash
# En otra terminal, monitorea logs
tail -f web/backend/logs/app.log

# O usa las herramientas de desarrollo del navegador
# Network tab: WebSocket connection
# Console: Mensajes de eventos
```

## 🔧 Solución de Problemas

### **"No se puede conectar al backend"**
```bash
# Verificar que el backend está corriendo
ps aux | grep python
curl http://localhost:8000

# Reiniciar backend
cd web/backend
python main.py
```

### **"WebSocket desconectado"**
```bash
# Verificar configuración CORS
# En web/backend/main.py, verificar:
allow_origins=["http://localhost:3000"]

# Reiniciar ambos servicios
```

### **"No se detectan objeciones"**
```bash
# Verificar configuración
cat .env | grep LLM

# Probar con frases conocidas
# Verificar logs del backend
```

### **"La transcripción es lenta"**
```bash
# Verificar conexión a internet
ping api.deepgram.com

# Verificar configuración de audio
cat .env | grep AUDIO_

# Reiniciar servicios
```

## 🎉 ¡Éxito!

Si todas las pruebas pasan, ¡felicidades! Has implementado completamente:

✅ **Interfaz web en tiempo real**
✅ **Transcripción < 1s**
✅ **Detección de objeciones < 1.5s**
✅ **Sistema de coaching completo**
✅ **Persistencia de datos**
✅ **Exportación de llamadas**

## 📚 Recursos Adicionales

- **Documentación Backend**: http://localhost:8000/docs
- **README Backend**: web/backend/README.md
- **README Frontend**: web/frontend/README.md
- **README Principal**: web/README.md

## 🚀 Próximos Pasos

1. **Personalizar colores y estilos** en `web/frontend/src/components/CoachLive.tsx`
2. **Agregar más tipos de objeciones** en `services/objection_service.py`
3. **Implementar vista post-call** con resumen detallado
4. **Agregar autenticación** para múltiples usuarios
5. **Desplegar en producción** con HTTPS

¡Tu sistema de coaching de ventas está listo para transformar la experiencia de ventas! 🎯
