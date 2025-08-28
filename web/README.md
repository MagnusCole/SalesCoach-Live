# Sales Coach Live - Web Interface

Interfaz web completa para el sistema de coaching de ventas en tiempo real.

## 🎯 Visión General

Sales Coach Live es una aplicación web completa que permite a los vendedores recibir coaching en tiempo real durante sus llamadas de ventas. La aplicación detecta objeciones automáticamente, proporciona sugerencias de respuesta, y guarda toda la información para análisis posterior.

## 🚀 Características Principales

### ✅ Requisitos Cumplidos

- **✅ Primera palabra en UI < 1s**: Optimizado para mínima latencia
- **✅ Objeción resaltada < 1.5s**: Detección y visualización rápida
- **✅ Coach ON/OFF funciona**: Toggle para activar/desactivar modo coach
- **✅ Solo transcribe cuando Coach OFF**: Control preciso del modo

### 🎨 Interfaz de Usuario

#### Vista Coach Live
- **Centro**: Transcripción en tiempo real con scroll automático
- **Izquierda Superior**: Objeciones detectadas con chips por tipo
- **Izquierda Inferior**: Sugerencias de respuesta con botón copiar
- **Derecha Superior**: Controles (start/stop, toggle coach, modelo IA)
- **Barra de Estado**: Conexión WebSocket, Call ID, contadores

#### Diseño Responsive
- **Desktop**: Layout de 4 paneles optimizado
- **Tablet/Mobile**: Adaptable y funcional

## 🏗️ Arquitectura

```
web/
├── backend/              # FastAPI Backend
│   ├── main.py          # Servidor principal
│   ├── requirements.txt # Dependencias Python
│   └── README.md        # Documentación backend
├── frontend/             # Next.js Frontend
│   ├── src/             # Código fuente
│   ├── package.json     # Dependencias Node.js
│   └── README.md        # Documentación frontend
└── ../                  # Sistema de coaching existente
    ├── services/        # Servicios Python
    ├── domain/          # Modelos de datos
    └── config/          # Configuración
```

## 📋 Requisitos del Sistema

- **Python 3.8+** con pip
- **Node.js 18+** con npm
- **Variables de entorno** configuradas (`.env`)
- **Puertos disponibles**: 8000 (backend), 3000 (frontend)

## 🛠️ Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
# Desde la raíz del proyecto
chmod +x start_web.sh
./start_web.sh
```

### Opción 2: Instalación Manual

#### Backend
```bash
cd web/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend
```bash
cd web/frontend
npm install
npm run dev
```

## 🚀 Uso

1. **Abrir navegador**: http://localhost:3000
2. **Configurar**: Revisar que las variables de entorno estén correctas
3. **Iniciar**: Presionar "Iniciar Grabación"
4. **Coaching**: Recibir feedback en tiempo real
5. **Detener**: Presionar "Detener Grabación" cuando termine

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Deepgram API
DEEPGRAM_API_KEY=tu_clave_api_aqui
DEEPGRAM_MODEL=nova-3-general

# OpenAI (para objeciones avanzadas)
OPENAI_API_KEY=tu_clave_openai

# Audio
AUDIO_MODE=stereo
STEREO_LAYOUT=LR

# Opciones
USE_LLM_FALLBACK=true
LOG_EVENTS=true
```

### Configuración de Audio

- **Modo Estéreo**: Micrófono (L) + Loopback (R)
- **VAD**: Detección automática de voz activa
- **Normalización**: Ajuste automático de volumen

## 📡 Comunicación en Tiempo Real

### WebSocket Events

#### Desde Backend → Frontend
- `session_started` - Sesión iniciada
- `transcript_update` - Nueva transcripción disponible
- `objection_detected` - Objeción detectada con metadatos
- `suggestion_ready` - Sugerencia de respuesta lista
- `call_completed` - Llamada finalizada

#### Desde Frontend → Backend
- `start_transcription` - Iniciar grabación
- `stop_transcription` - Detener grabación
- `toggle_coach` - Cambiar modo coach
- `ping` - Keep-alive

## 🎯 Tipos de Objeciones Detectadas

1. **Precio** 💰 - "Es muy caro", "No entra en presupuesto"
2. **Tiempo** ⏰ - "Ahora no", "Llámame después"
3. **Autoridad** 👔 - "Tengo que consultarlo", "Mi jefe decide"
4. **Competencia** 🏢 - "Trabajo con X empresa"
5. **Confianza** 🤝 - "No estoy seguro", "Dudo que funcione"

## 📊 Rendimiento

### Latencias Objetivo
- **Primera palabra**: < 1 segundo
- **Objeción resaltada**: < 1.5 segundos
- **Sugerencia mostrada**: < 2 segundos

### Optimizaciones Implementadas
- WebSocket con reconexión automática
- Procesamiento asíncrono de audio
- Cache inteligente de resultados
- Renderizado eficiente de UI

## 🔧 Desarrollo

### Estructura del Proyecto

#### Backend (FastAPI)
- **Endpoints REST**: Sesiones, descargas, configuración
- **WebSocket**: Comunicación bidireccional
- **Integración**: Con sistema de coaching existente
- **Documentación**: Auto-generada en `/docs`

#### Frontend (Next.js)
- **React Hooks**: Gestión de estado y efectos
- **TypeScript**: Type safety completo
- **Tailwind CSS**: Styling moderno y responsive
- **WebSocket**: Comunicación en tiempo real

### Scripts Disponibles

```bash
# Backend
cd web/backend
python main.py              # Desarrollo
uvicorn main:app --reload  # Con auto-reload

# Frontend
cd web/frontend
npm run dev                # Desarrollo
npm run build             # Producción
npm run start             # Servidor producción
```

## 🚨 Solución de Problemas

### Problemas Comunes

#### "No se puede conectar al backend"
- Verificar que el backend esté corriendo en puerto 8000
- Revisar configuración CORS
- Verificar URL en `.env.local`

#### "No se detectan objeciones"
- Verificar configuración de `USE_LLM_FALLBACK`
- Revisar claves API de OpenAI
- Verificar configuración de audio

#### "La transcripción es lenta"
- Verificar conexión a internet
- Revisar configuración de Deepgram
- Verificar rendimiento del sistema

#### "Error de WebSocket"
- Verificar que no hay firewall bloqueando
- Revisar configuración de proxy
- Verificar compatibilidad del navegador

### Logs y Debugging

#### Backend
```bash
cd web/backend
LOG_LEVEL=DEBUG python main.py
```

#### Frontend
```bash
cd web/frontend
npm run dev  # Logs en consola del navegador
```

## 📈 Métricas y Monitoreo

- **Latencia de transcripción**: Medida automáticamente
- **Tasa de detección de objeciones**: Seguimiento de precisión
- **Conexión WebSocket**: Estado y reconexiones
- **Rendimiento del sistema**: CPU, memoria, red

## 🔮 Roadmap

### Próximas Funcionalidades
- [ ] Vista post-call con resumen detallado
- [ ] Historial completo de llamadas
- [ ] Exportación avanzada (PDF, video)
- [ ] Modo oscuro
- [ ] Notificaciones push
- [ ] Integración con CRM
- [ ] Análisis de sentimiento
- [ ] Sugerencias personalizadas por usuario

### Mejoras de Rendimiento
- [ ] Optimización de bundle size
- [ ] Service Worker para offline
- [ ] WebRTC para audio directo
- [ ] Compresión de datos WebSocket

## 📝 Notas Técnicas

### Compatibilidad
- **Navegadores**: Chrome 90+, Edge 90+, Safari 14+
- **Sistemas Operativos**: Windows 10+, macOS 11+, Linux Ubuntu 20+
- **Dispositivos**: Desktop, tablet, mobile (experimental)

### Seguridad
- **HTTPS**: Recomendado para producción
- **Autenticación**: Implementar JWT o similar
- **Validación**: Todos los inputs validados
- **Rate Limiting**: Implementado en backend

### Escalabilidad
- **WebSocket**: Soporta múltiples conexiones
- **Backend**: Stateless, fácil de escalar
- **Base de datos**: Preparado para PostgreSQL/MySQL
- **Cache**: Redis para sesiones activas

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Issues**: GitHub Issues para bugs y features
- **Discussions**: GitHub Discussions para preguntas generales
- **Email**: Para soporte prioritario

---

**¡Gracias por usar Sales Coach Live!** 🎉

Transforma tus llamadas de ventas con coaching en tiempo real impulsado por IA.
