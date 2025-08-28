# Sales Coach Live

Sistema de coaching de ventas en tiempo real que captura audio de llamadas y proporciona sugerencias automáticas basadas en objeciones detectadas.

## 🚀 Inicio Rápido

### Desarrollo Local

**Backend:**
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd web
npm install
npm run dev
```

### Despliegue en Producción

**Backend (Cloud Run):**
```bash
gcloud run deploy salescoach-api \
  --source ./api \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEEPGRAM_API_KEY=YOUR_KEY,DEEPGRAM_MODEL=nova-3-general,DEEPGRAM_LANGUAGE=multi \
  --timeout 3600 --concurrency 20 --memory 1Gi
```

**Frontend (Vercel/Netlify):**
1. Despliega la carpeta `web/`
2. Configura `NEXT_PUBLIC_API_WS` con la URL de Cloud Run (ej: `wss://tu-app.run.app/ws/demo`)

## 📁 Estructura del Proyecto

```
salescoach-live/
├─ api/                      # Backend FastAPI (Cloud Run)
│  ├─ main.py                # WS relay + Deepgram + eventos
│  ├─ objection_service.py   # Reglas + fallback LLM (opcional)
│  ├─ playbooks.py           # Lectura de KB / playbook
│  ├─ data/
│  │  └─ playbook.json       # Respuestas por objeción (tu KB)
│  ├─ requirements.txt
│  └─ Dockerfile
├─ web/                      # Frontend (Next.js sencillo)
│  ├─ app/
│  │  ├─ page.tsx            # / (Start)
│  │  └─ live/page.tsx       # /live (vista en vivo)
│  ├─ public/
│  ├─ package.json
│  └─ next.config.mjs
├─ .env.example              # Variables necesarias (sin secretos)
└─ README.md                 # Cómo correr local / desplegar
```

## ⚙️ Configuración

1. Copia `.env.example` a `.env`
2. Configura tu `DEEPGRAM_API_KEY`
3. Ajusta `DEEPGRAM_LANGUAGE` según necesites (`es` para español puro, `multi` para multilingüe)

## 🎯 Características

- **Transcripción en tiempo real** usando Deepgram NOVA 3
- **Detección automática de objeciones** basada en reglas regex
- **Sugerencias contextuales** desde playbook personalizado
- **Interfaz web moderna** con captura de pantalla
- **Arquitectura serverless** lista para producción

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

## 🚀 Despliegue

### Cloud Run (Backend)
```bash
gcloud run deploy salescoach-api \
  --source ./api \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEEPGRAM_API_KEY=XXXX,DEEPGRAM_MODEL=nova-3-general,DEEPGRAM_LANGUAGE=multi \
  --timeout 3600
```

### Vercel (Frontend)
1. Conecta tu repo a Vercel
2. Configura variable: `NEXT_PUBLIC_API_WS=wss://tu-cloud-run-url/ws/demo`
3. Deploy automático

## � Personalización

### Playbook de Objeciones
Edita `api/data/playbook.json` para personalizar las respuestas:

```json
[
  { "objection_type": "precio", "text": "Tu respuesta personalizada aquí" },
  { "objection_type": "tiempo", "text": "Otra respuesta..." }
]
```

### Reglas de Detección
Modifica `api/objection_service.py` para ajustar las expresiones regex que detectan objeciones.

## 🔒 Seguridad

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
- Documentación oficial de Deepgram: https://developers.deepgram.com/
- SDK v3 Documentation: https://github.com/deepgram/deepgram-python-sdk
- Comunidad Deepgram: https://github.com/deepgram

---

**¡Tu sistema de transcripción NOVA 3 con SDK v3 está listo para usar!** 🎉
