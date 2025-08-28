# Sales Coach Live - Frontend

Interfaz web en tiempo real para el sistema de coaching de ventas.

## 🚀 Características

- **Interfaz en Tiempo Real**: Transcripción, objeciones y sugerencias en vivo
- **WebSocket**: Comunicación bidireccional con el backend
- **UI Moderna**: Diseño responsive con Tailwind CSS
- **Controles Interactivos**: Iniciar/detener grabación, toggle coach
- **Visualización Clara**: Diferenciación visual de objeciones y sugerencias

## 📋 Requisitos

- Node.js 18+
- npm o yarn
- Backend corriendo en `http://localhost:8000`

## 🛠️ Instalación

1. **Instalar dependencias:**
```bash
cd web/frontend
npm install
# o
yarn install
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env.local
# Editar .env.local si es necesario
```

## 🚀 Uso

### Desarrollo
```bash
npm run dev
# o
yarn dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

### Producción
```bash
npm run build
npm start
# o
yarn build
yarn start
```

## 🎯 Funcionalidades

### Vista Coach Live

- **Panel de Transcripción** (Centro):
  - Transcripción en tiempo real
  - Scroll automático
  - Indicador de grabación
  - Diferenciación visual por hablante
  - Resaltado de objeciones

- **Panel de Objeciones** (Izquierda superior):
  - Lista de objeciones detectadas
  - Chips con tipos de objeción
  - Timestamps y confianza
  - Colores diferenciados por tipo

- **Panel de Sugerencias** (Derecha inferior):
  - Sugerencias de respuesta
  - Botón de copiar al portapapeles
  - Historial de últimas sugerencias

- **Panel de Controles** (Derecha superior):
  - Botón iniciar/detener grabación
  - Toggle modo coach ON/OFF
  - Selector de modelo de IA

### Barra de Estado

- Estado de conexión WebSocket
- Call ID actual
- Contadores de segmentos y objeciones

## 🔧 Configuración

### Variables de Entorno

```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # URL del backend
```

### Personalización

Los colores y estilos se pueden personalizar en:
- `tailwind.config.js` - Configuración de Tailwind
- `src/components/CoachLive.tsx` - Estilos de componentes

## 📡 Comunicación con Backend

### WebSocket Events

- `session_started` - Sesión iniciada
- `transcript_update` - Nueva transcripción
- `objection_detected` - Objeción detectada
- `suggestion_ready` - Sugerencia disponible
- `call_completed` - Llamada finalizada

### API REST

- `POST /session/start` - Iniciar sesión
- `GET /calls/{id}/transcript.txt` - Descargar TXT
- `GET /calls/{id}/transcript.json` - Datos JSON
- `GET /calls/{id}/audio/{type}.wav` - Descargar audio

## 🎨 Diseño

### Layout Responsive

- **Desktop**: 4 columnas (objeciones, transcripción, controles, sugerencias)
- **Tablet**: Adaptable a 2-3 columnas
- **Mobile**: Vista simplificada

### Tema Visual

- **Colores principales**: Azul para usuario, verde para cliente
- **Objeciones**: Rojo con borde izquierdo
- **Sugerencias**: Azul claro con botón copiar
- **Estados**: Verde para conectado, rojo para desconectado

## 🔧 Desarrollo

### Estructura de Archivos

```
web/frontend/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── layout.tsx      # Layout principal
│   │   └── page.tsx        # Página principal
│   ├── components/         # Componentes React
│   │   └── CoachLive.tsx   # Componente principal
│   ├── contexts/           # Contextos React
│   │   └── CoachContext.tsx
│   ├── hooks/              # Hooks personalizados
│   │   └── useWebSocket.ts
│   ├── services/           # Servicios API
│   │   └── api.ts
│   └── types/              # Tipos TypeScript
│       └── coach.ts
├── public/                 # Archivos estáticos
├── .env.local             # Variables de entorno
└── tailwind.config.js     # Configuración Tailwind
```

### Scripts Disponibles

```bash
npm run dev          # Desarrollo con hot reload
npm run build        # Build de producción
npm run start        # Servidor de producción
npm run lint         # Linting con ESLint
```

## 🚨 Solución de Problemas

### Error de conexión WebSocket
- Verificar que el backend esté corriendo en el puerto 8000
- Revisar configuración CORS en el backend
- Verificar URL en `.env.local`

### Problemas de rendimiento
- La transcripción aparece con > 1s de latencia
- Objeciones se resaltan en < 1.5s
- Optimizado para baja latencia

### Problemas de UI
- Componentes no se renderizan: verificar imports
- WebSocket no conecta: revisar configuración de backend
- Estilos no aplican: verificar Tailwind CSS

## 📊 Rendimiento

### Objetivos de Latencia

- **Primera palabra**: < 1 segundo desde que se dice
- **Objeción resaltada**: < 1.5 segundos desde detección
- **Sugerencia mostrada**: < 2 segundos desde objeción

### Optimizaciones

- WebSocket con reconexión automática
- Scroll automático suave
- Renderizado eficiente de listas
- Lazy loading de componentes

## 🔮 Próximas Funcionalidades

- Vista post-call con resumen y descargas
- Historial de llamadas
- Exportación de datos
- Configuración de modelos de IA
- Modo oscuro
- Notificaciones push

## 📝 Notas de Desarrollo

- Optimizado para Chrome/Edge modernos
- WebSocket con heartbeat para mantener conexión
- TypeScript para type safety
- ESLint para calidad de código
- Tailwind para styling consistente
