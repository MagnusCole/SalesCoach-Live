# Sales Coach Live - Backend

Backend FastAPI para el sistema de coaching de ventas en tiempo real.

## 🚀 Características

- **API REST**: Endpoints para iniciar sesiones y obtener datos
- **WebSocket**: Comunicación en tiempo real con el frontend
- **Transcripción**: Integración con Deepgram NOVA 3
- **Detección de Objeciones**: Análisis en tiempo real
- **Almacenamiento**: Persistencia de llamadas y exportación
- **CORS**: Configurado para desarrollo local

## 📋 Requisitos

- Python 3.8+
- Variables de entorno configuradas (`.env`)

## 🛠️ Instalación

1. **Crear entorno virtual:**
```bash
cd web/backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Editar .env con tus claves API
```

## 🚀 Uso

### Desarrollo
```bash
python main.py
```

### Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### REST API

- `POST /session/start` - Iniciar nueva sesión
- `GET /calls/{id}/transcript.txt` - Descargar transcripción TXT
- `GET /calls/{id}/transcript.json` - Obtener datos JSON
- `GET /calls/{id}/audio/{type}.wav` - Descargar audio
- `GET /calls` - Listar llamadas

### WebSocket

- `WS /ws/{call_id}` - Conexión WebSocket para eventos en tiempo real

#### Eventos WebSocket

- `session_started` - Sesión iniciada
- `transcript_update` - Nueva transcripción
- `objection_detected` - Objeción detectada
- `suggestion_ready` - Sugerencia disponible
- `call_completed` - Llamada finalizada
- `ping/pong` - Keep-alive

## 🔧 Configuración

Las configuraciones principales están en `config/settings.py`:

- **Deepgram**: `DEEPGRAM_API_KEY`, `DEEPGRAM_MODEL`
- **Audio**: `AUDIO_MODE`, `STEREO_LAYOUT`, `VAD_ENABLED`
- **Objeciones**: `USE_LLM_FALLBACK`, `LLM_MODEL`
- **Web**: CORS origins, WebSocket timeout

## 🏗️ Arquitectura

```
web/backend/
├── main.py              # Aplicación FastAPI principal
├── requirements.txt     # Dependencias Python
└── README.md           # Esta documentación
```

## 🔌 Integración con Sistema Existente

El backend se integra con los servicios existentes:

- `TranscriptionService` - Manejo de transcripción
- `StorageService` - Persistencia de datos
- `TranscriptExporter` - Exportación de transcripciones
- Sistema de objeciones y sugerencias

## 📊 Monitoreo

- Logs en tiempo real
- Estadísticas de rendimiento
- Manejo de errores con detalles

## 🚨 Solución de Problemas

### Error de conexión WebSocket
- Verificar que el puerto 8000 esté disponible
- Revisar configuración CORS

### Error de API de Deepgram
- Verificar `DEEPGRAM_API_KEY` en `.env`
- Revisar región configurada

### Problemas de audio
- Verificar dispositivos de audio disponibles
- Revisar configuración de `AUDIO_MODE`

## 📝 Notas de Desarrollo

- El backend está optimizado para baja latencia (< 1s)
- WebSocket maneja desconexiones automáticamente
- Sistema de eventos desacoplado para extensibilidad
