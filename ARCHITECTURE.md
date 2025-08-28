"""
Deepgram NOVA 3 Transcription System - Modular Architecture
================================================================

Estructura modular usando frameworks y patrones de clase mundial:

📁 ESTRUCTURA DEL PROYECTO:
├── config/                 # Configuración centralizada
│   ├── __init__.py
│   ├── settings.py         # Configuración Pydantic
│   └── environment.py      # Variables de entorno
├── core/                   # Lógica de negocio central
│   ├── __init__.py
│   ├── audio/             # Procesamiento de audio
│   │   ├── __init__.py
│   │   ├── processor.py   # Procesador de audio
│   │   ├── vad.py         # Detección de voz
│   │   └── normalizer.py  # Normalización
│   ├── transcription/     # Transcripción Deepgram
│   │   ├── __init__.py
│   │   ├── client.py      # Cliente Deepgram
│   │   ├── session.py     # Sesión de transcripción
│   │   └── events.py      # Manejadores de eventos
│   └── devices/           # Gestión de dispositivos
│       ├── __init__.py
│       ├── manager.py     # Administrador de dispositivos
│       └── selector.py    # Selector de dispositivos
├── infrastructure/        # Capa de infraestructura
│   ├── __init__.py
│   ├── logging/           # Sistema de logging
│   │   ├── __init__.py
│   │   └── config.py
│   └── metrics/           # Métricas y monitoreo
│       ├── __init__.py
│       └── collector.py
├── domain/                # Modelos de dominio
│   ├── __init__.py
│   ├── models.py          # Modelos de datos
│   └── entities.py        # Entidades del dominio
├── interfaces/            # Interfaces y contratos
│   ├── __init__.py
│   ├── audio_interface.py
│   └── transcription_interface.py
├── services/              # Servicios de aplicación
│   ├── __init__.py
│   ├── transcription_service.py
│   └── audio_service.py
├── utils/                 # Utilidades
│   ├── __init__.py
│   ├── async_utils.py
│   └── validation.py
├── main.py               # Punto de entrada
├── cli.py                # Interfaz de línea de comandos
└── pyproject.toml        # Configuración del proyecto
"""

# Este archivo servirá como documentación de la arquitectura
__version__ = "1.0.0"
__author__ = "Deepgram NOVA 3 Team"
