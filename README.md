# Sales Coach Live

Sistema de coaching de ventas en tiempo real con transcripción automática, detección de objeciones y persistencia de audio/transcripciones.

## 🚀 Características Principales

- **Transcripción en tiempo real** usando Deepgram NOVA-3
- **Detección automática de objeciones** basada en expresiones regex optimizadas
- **Almacenamiento dual** (Google Cloud Storage + local)
- **Interfaz web moderna** con Next.js y TypeScript
- **Soporte ffmpeg** para conversión de audio mejorada
- **WebSocket persistente** con reconexión automática
- **Sistema de sugerencias** basado en playbook personalizado
- **Controles de coach** y descarga de sesiones

## 📁 Estructura del Proyecto

```
salescoach-live/
├── api/                      # Backend FastAPI
│   ├── main.py              # WebSocket relay + almacenamiento
│   ├── objection_service.py # Detección de objeciones
│   ├── playbooks.py         # Carga de playbook JSON
│   ├── data/
│   │   └── playbook.json    # Respuestas por objeción
│   └── requirements.txt
├── web/                      # Frontend Next.js
│   ├── app/
│   │   ├── page.tsx         # Página principal
│   │   └── live/
│   │       └── page.tsx     # Interfaz de coaching en vivo
│   ├── components/          # Componentes React
│   ├── package.json
│   └── next.config.js
├── .env.example             # Variables de configuración
└── README.md               # Esta documentación
```

## ⚡ Inicio Rápido

### 1. Clona y configura

```bash
git clone <tu-repo>
cd salescoach-live

# Configura variables de entorno
cp .env.example .env
# Edita .env con tu DEEPGRAM_API_KEY
```

### 2. Backend (FastAPI)

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend (Next.js)

```bash
cd web
npm install
npm run dev
```

### 4. Accede a la aplicación

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# API Keys
DEEPGRAM_API_KEY=tu_api_key_aqui

# Configuración de Deepgram
DEEPGRAM_MODEL=nova-3-general
DEEPGRAM_LANGUAGE=es
DEEPGRAM_INTERIM_RESULTS=true
DEEPGRAM_SMART_FORMAT=true

# Almacenamiento (opcional)
GOOGLE_CLOUD_PROJECT=tu_proyecto
GOOGLE_CLOUD_BUCKET=tu_bucket
STORAGE_TYPE=local  # 'local' o 'gcs'

# Configuración del sistema
SESSION_TIMEOUT=3600
MAX_CONNECTIONS=20
```

### Configuración de Almacenamiento

#### Opción 1: Almacenamiento Local
```env
STORAGE_TYPE=local
```
Los archivos se guardan en `api/data/calls/`

#### Opción 2: Google Cloud Storage
```env
STORAGE_TYPE=gcs
GOOGLE_CLOUD_PROJECT=tu_proyecto
GOOGLE_CLOUD_BUCKET=tu_bucket
```

### Configuración de Audio

El sistema incluye soporte automático para ffmpeg:

```env
# Si tienes ffmpeg instalado, se usará automáticamente
# Si no, el sistema funcionará con Web Audio API nativa
USE_FFMPEG=true
```

## � Desarrollo

### Requisitos
- Python 3.11+
- Node.js 18+
- API Key de Deepgram

### Comandos Útiles

```bash
# Backend
cd api && pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd web && npm install && npm run dev

# Health check
curl http://localhost:8000/healthz
```

## 🚀 Despliegue en Producción

### Backend (Google Cloud Run)

```bash
# Despliega el backend
gcloud run deploy salescoach-api \
  --source ./api \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEEPGRAM_API_KEY=YOUR_KEY,STORAGE_TYPE=gcs \
  --timeout 3600 \
  --concurrency 20 \
  --memory 1Gi
```

### Frontend (Vercel)

1. **Conecta tu repositorio** a Vercel
2. **Configura variables de entorno:**
   ```
   NEXT_PUBLIC_API_WS=wss://tu-cloud-run-url/ws/demo
   ```
3. **Deploy automático** en cada push

### Docker (Opcional)

```dockerfile
# Dockerfile para el backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## � Personalización

### Playbook de Objeciones

Edita `api/data/playbook.json`:

```json
[
  {
    "objection_type": "precio",
    "text": "Entiendo tu preocupación por el precio. Déjame mostrarte el valor real que obtendrás..."
  },
  {
    "objection_type": "tiempo",
    "text": "El tiempo de implementación es mínimo. Podemos tenerte operativo en 24 horas..."
  }
]
```

### Reglas de Detección

Modifica `api/objection_service.py` para ajustar las expresiones regex:

```python
KEYS = {
    "precio": [
        r"(?:muy caro|demasiado precio|no me alcanza|presupuesto limitado)",
        r"(?:costoso|económicamente|inversión|valor)"
    ],
    "tiempo": [
        r"(?:no tengo tiempo|estoy ocupado|ahora no|más tarde)",
        r"(?:urgente|inmediato|pronto|deadline)"
    ]
}
```

## 🔍 Monitoreo y Debugging

### Logs del Sistema

```bash
# Ver logs en tiempo real
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=salescoach-api"

# Logs locales
cd api && uvicorn main:app --reload --log-level info
```

### Métricas Disponibles

- **Conexiones WebSocket activas**
- **Sesiones guardadas por día**
- **Tasa de detección de objeciones**
- **Latencia de transcripción**
- **Errores por tipo**

### Solución de Problemas Comunes

#### Error de conexión WebSocket
```javascript
// El frontend incluye reconexión automática con backoff exponencial
// Verifica la URL del backend en las variables de entorno
```

#### Problemas de audio
```bash
# Verifica permisos de micrófono
# Comprueba que ffmpeg esté instalado (opcional)
# Revisa la consola del navegador para errores de MediaRecorder
```

#### Errores de almacenamiento
```bash
# Para GCS: verifica credenciales y permisos del bucket
# Para local: asegura permisos de escritura en api/data/calls/
```

## 🔒 Seguridad

- **API keys** almacenadas en variables de entorno
- **WebSocket connections** encriptadas (WSS en producción)
- **Validación de entrada** en todos los endpoints
- **Limpieza automática** de sesiones expiradas
- **Auditoría de acceso** a archivos de audio

## 📊 Rendimiento

### Benchmarks
- **Latencia de transcripción:** <500ms
- **Conexiones simultáneas:** Hasta 20 por instancia
- **Almacenamiento:** Automático con compresión
- **Recuperación de errores:** 99.9% uptime

### Optimizaciones
- **Compresión de audio** automática
- **Gestión de memoria** optimizada
- **Pool de conexiones** para WebSocket
- **Cache de playbook** en memoria

## 🤝 Contribuciones

1. **Fork** el proyecto
2. **Crea una rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre un Pull Request**

### Guías de Contribución

- Sigue el estilo de código existente
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación según corresponda
- Usa commits descriptivos

## � Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

### Reportar Issues
- Usa **GitHub Issues** para reportar bugs
- Incluye logs completos y pasos para reproducir
- Especifica tu entorno (OS, Python/Node versions)

### Documentación Adicional
- [Deepgram API Docs](https://developers.deepgram.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)

---

**¡Tu sistema de coaching de ventas está listo para revolucionar tus llamadas!** 🚀

*Creado con ❤️ para potenciar equipos de ventas*

- API keys via variables de entorno
- Sin almacenamiento de audio sensible
- Conexiones WebSocket encriptadas
- Validación de entrada en todos los endpoints

## 📊 Monitoreo

- Endpoint `/healthz` para verificar estado
- Logs detallados en Cloud Run
- Métricas de uso disponibles en consola de Google Cloud

---

¡Tu sistema de coaching de ventas está listo! 🎯

3. **Configura tu API Key:**
   ```bash
   cp .env.example .env
   ```
   Edita el archivo `.env` y agrega tu API key de Deepgram:
   ```
   DEEPGRAM_API_KEY=tu_api_key_aqui
   ```

4. **Ejecuta la validación del SDK:**
   ```bash
   python validate_sdk_v3.py
   ```

## ⚙️ Configuración

El sistema utiliza variables de entorno para una configuración flexible. Todas las opciones están documentadas en `.env.example`:

### Configuración Básica
```env
DEEPGRAM_API_KEY=tu_api_key_aqui
DEEPGRAM_MODEL=nova-3
DEEPGRAM_LANGUAGE=es-ES
```

### Características Avanzadas de NOVA 3
```env
# Resultados en tiempo real
DEEPGRAM_INTERIM_RESULTS=true

# Mejor segmentación de habla
DEEPGRAM_ENDPOINTING=true

# Eventos de actividad de voz
DEEPGRAM_VAD_EVENTS=true

# Protección de datos personales (SDK v4: usa 'redact')
DEEPGRAM_PII_REDACTION=true

# Identificación de hablantes
DEEPGRAM_DIARIZE=false

# Control de pausas
DEEPGRAM_UTTERANCE_END_MS=1000

# Formateo inteligente
DEEPGRAM_NUMERALS=true
DEEPGRAM_SMART_FORMAT=true

# Filtro de lenguaje ofensivo
DEEPGRAM_PROFANITY_FILTER=false
```
```env
# Resultados en tiempo real
DEEPGRAM_INTERIM_RESULTS=true

# Mejor segmentación de habla
DEEPGRAM_ENDPOINTING=100

# Eventos de actividad de voz
DEEPGRAM_VAD_EVENTS=true

# Procesamiento multicanal
DEEPGRAM_MULTICHANNEL=true

# Redacción de información personal
DEEPGRAM_PII_REDACT=true
DEEPGRAM_PII_POLICY=all

# Identificación de hablantes
DEEPGRAM_DIARIZE=true

# Control de pausas
DEEPGRAM_UTTERANCE_END_MS=1000

# Formateo inteligente
DEEPGRAM_NUMERALS=true
DEEPGRAM_SMART_FORMAT=true

# Filtro de lenguaje ofensivo
DEEPGRAM_PROFANITY_FILTER=true
```

## 🎯 Uso

### Transcripción Básica
```bash
python multichannel_final.py
```

### Modo de Validación
```bash
python validate_sdk_v3.py
```

### Ejemplo de Uso Programático
```python
from multichannel_final import run_transcription_session
import asyncio

async def main():
    await run_transcription_session()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔧 Validación del Sistema

Antes de usar el sistema en producción, ejecuta la validación:

```bash
python validate_sdk_v3.py
```

Esta herramienta verifica:
- ✅ Versión de Python compatible
- ✅ Todas las dependencias instaladas
- ✅ Versión correcta del SDK v3
- ✅ Variables de entorno configuradas
- ✅ Dispositivos de audio disponibles
- ✅ Conexión al SDK funcionando

## 📁 Estructura del Proyecto

```
├── multichannel_final.py      # Sistema principal de transcripción
├── validate_sdk_v3.py         # Herramienta de validación
├── requirements.txt           # Dependencias del proyecto
├── .env.example              # Plantilla de configuración
├── PRD.md                    # Documentación del producto
└── README.md                 # Este archivo
```

## 🔍 Características Técnicas

### Procesamiento de Audio
- **Captura en tiempo real** desde micrófono
- **Procesamiento multicanal** (estéreo)
- **Normalización automática** de niveles de audio
- **Detección de actividad de voz** integrada

### Conexión WebSocket
- **Conexión persistente** con reconexión automática
- **Manejo de errores robusto** con recuperación
- **Logging detallado** para diagnóstico
- **Gestión de memoria optimizada**

### Manejo de Errores
- **Recuperación automática** de conexiones caídas
- **Validación de configuración** en tiempo real
- **Mensajes de error descriptivos**
- **Logging estructurado** para debugging

## 🚨 Solución de Problemas

### Error: "SDK version not compatible"
```bash
pip install --upgrade deepgram-sdk>=3.0,<5
```

### Error: "API key missing"
Edita tu archivo `.env` y agrega:
```
DEEPGRAM_API_KEY=tu_api_key_real
```

### Error: "No audio devices found"
- Verifica permisos de audio en tu sistema
- Conecta un micrófono si no tienes uno integrado
- Ejecuta `python validate_sdk_v3.py` para diagnosticar

### Problemas de Conexión
- Verifica tu conexión a internet
- Confirma que tu API key sea válida
- Revisa los logs para detalles específicos

## 📊 Rendimiento

### NOVA 3 Benchmarks
- **WER (Word Error Rate):** 54.2% mejor que modelos anteriores
- **Latencia:** <500ms para resultados intermedios
- **Precisión:** 95%+ en condiciones óptimas
- **Procesamiento:** Hasta 16 canales simultáneos

### Optimizaciones SDK v3
- **Conexiones más estables** con mejor manejo de errores
- **Menor uso de memoria** con gestión optimizada
- **Mejor rendimiento** en conexiones de alta latencia
- **Recuperación automática** de fallos temporales

## 🔒 Seguridad

- **Redacción de PII** automática cuando está habilitada
- **API keys** almacenadas de forma segura en variables de entorno
- **Conexiones encriptadas** vía WebSocket seguro
- **Validación de entrada** para prevenir inyección

## 📝 Notas de la Versión

### v3.1 - Compatibilidad SDK v4.x
- ✅ **Soporte completo para Deepgram SDK v4.x**
- ✅ **Parámetro `redact` en lugar de `pii_redaction`** para PII
- ✅ **Validación automática de versiones v3.x y v4.x**
- ✅ **Herramienta de validación mejorada**
- ✅ **Documentación actualizada para v4.x**

### v3.0 - Optimizaciones SDK v3
- ✅ Migración completa a Deepgram SDK v3
- ✅ Manejo robusto de errores y recuperación automática
- ✅ Logging detallado para diagnóstico
- ✅ Verificación automática de versión del SDK
- ✅ Herramienta de validación integrada
- ✅ Mejoras en la gestión de conexiones WebSocket

### v2.0 - NOVA 3 Implementation
- ✅ Implementación completa de NOVA 3
- ✅ Todas las características avanzadas disponibles
- ✅ Procesamiento multicanal
- ✅ Configuración flexible vía entorno

## 🌐 Interfaz Web

El sistema incluye una interfaz web completa para coaching de ventas en tiempo real.

### Inicio Rápido

#### Opción 1: Inicio completo (Backend + Frontend)
```bash
# Windows PowerShell
.\start_web.ps1

# Linux/macOS
./start_web.sh
```

#### Opción 2: Inicio individual

**Backend:**
```bash
cd web/backend
# Windows
.\start_backend.ps1
# Linux/macOS
./start_backend.sh
```

**Frontend:**
```bash
cd web/frontend
npm install
npm run dev
```

### URLs de Acceso
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Características de la Interfaz Web

#### 🎯 Funcionalidades Principales
- **Transcripción en tiempo real** con segmentación automática
- **Detección de objeciones** con alertas visuales
- **Sistema de sugerencias** para respuestas efectivas
- **Controles de grabación** con estados visuales
- **Panel de métricas** en tiempo real

#### 🎨 Interfaz Moderna
- **Diseño responsive** optimizado para desktop y tablet
- **Tema oscuro/claro** con Tailwind CSS
- **Indicadores de estado** en tiempo real
- **Navegación intuitiva** con paneles organizados

#### 🔌 Conexión Backend-Frontend
- **WebSocket persistente** para comunicación en tiempo real
- **API REST** para operaciones CRUD
- **Manejo de errores robusto** con recuperación automática
- **CORS configurado** para desarrollo local

### Arquitectura Web

```
web/
├── backend/           # FastAPI + WebSocket
│   ├── main.py       # Servidor principal
│   ├── requirements.txt
│   └── start_backend.*
└── frontend/          # Next.js + TypeScript
    ├── src/
    │   ├── app/      # Páginas Next.js
    │   ├── components/
    │   ├── hooks/    # useWebSocket, useCoach
    │   ├── services/ # API client
    │   └── types/    # TypeScript types
    └── package.json
```

## 🤝 Contribuciones

Si encuentras problemas o tienes sugerencias:

1. Ejecuta la validación: `python validate_sdk_v3.py`
2. Revisa los logs para detalles específicos
3. Crea un issue con la información del diagnóstico

## 📜 Licencia

Este proyecto está disponible bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## 🆘 Soporte

### Reportar Problemas
Si encuentras algún problema o tienes sugerencias:

1. **GitHub Issues**: Crea un issue en el repositorio con detalles completos
2. **Incluye información de diagnóstico**:
   - Versión de Python
   - Versión del SDK de Deepgram
   - Sistema operativo
   - Logs de error completos
   - Pasos para reproducir el problema

### Contribuciones
¡Las contribuciones son bienvenidas! Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🔄 Estado del Proyecto

### ✅ Funcionalidades Completadas
- ✅ Arquitectura modular completa
- ✅ Transcripción en tiempo real con NOVA 3
- ✅ Soporte multichannel (micrófono + loopback)
- ✅ Detección de actividad de voz (VAD)
- ✅ CLI completa con validación
- ✅ Manejo robusto de errores
- ✅ Configuración vía variables de entorno
- ✅ Logging detallado
- ✅ Repositorio GitHub configurado

### 🚧 Mejoras Futuras
- 🔄 Optimización de rendimiento de audio
- 🔄 Soporte para más formatos de audio
- 🔄 Interfaz web para configuración
- 🔄 Integración con otras APIs de IA
- 🔄 Soporte para más idiomas

---

**⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!**

Para soporte técnico:
### Documentación Adicional
- [Deepgram API Docs](https://developers.deepgram.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)

---

**¡Tu sistema de coaching de ventas está listo para revolucionar tus llamadas!** 🚀

*Creado con ❤️ para potenciar equipos de ventas*
