#!/usr/bin/env python3
"""
Ejemplo de uso de NOVA 3 con Deepgram
=====================================

Este script demuestra las nuevas funcionalidades avanzadas de NOVA 3:
- Interim Results en tiempo real
- VAD Events para detección de voz
- PII Redaction para protección de datos
- Control avanzado de utterances
- Diarization para identificación de hablantes
"""

import asyncio
import os
from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents

async def ejemplo_nova_3_basico():
    """Ejemplo básico con NOVA 3 - SDK v3 Best Practices"""
    print("🚀 Ejemplo Básico de NOVA 3 (SDK v3)")

    # Configuración básica optimizada para NOVA 3
    options = LiveOptions(
        model="nova-3-general",
        language="multi",  # Detección automática multilingüe
        interim_results=True,  # Resultados en tiempo real
        endpointing=True,  # Mejor segmentación
        smart_format=True,  # Formateo inteligente
    )

    # Inicialización correcta del cliente v3
    deepgram = DeepgramClient("YOUR_API_KEY")
    connection = deepgram.listen.websocket.v("1")

    @connection.on(LiveTranscriptionEvents.Transcript)
    def handle_transcript(result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        is_final = getattr(result, 'is_final', True)
        status = "[FINAL]" if is_final else "[INTERIM]"
        print(f"{status} {transcript}")

    try:
        connection.start(options)
        print("🎤 Conectado a NOVA 3 (SDK v3). Habla para ver transcripción en tiempo real...")

        # Simular envío de audio (reemplaza con tu fuente de audio real)
        # connection.send(audio_data)

        await asyncio.sleep(10)  # Mantener conexión por 10 segundos
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
    finally:
        connection.finish()

async def ejemplo_nova_3_avanzado():
    """Ejemplo avanzado con todas las features de NOVA 3"""
    print("\n🚀 Ejemplo Avanzado de NOVA 3")

    # Configuración completa con todas las features de NOVA 3
    options = LiveOptions(
        model="nova-3-general",
        language="multi",
        interim_results=True,      # Resultados en tiempo real
        endpointing=True,          # Mejor detección de fin de habla
        vad_events=True,           # Eventos de actividad de voz
        pii_redaction=True,        # Redacción de información personal
        diarize=True,              # Identificación de hablantes
        utterance_end_ms=1500,     # Control de pausa entre utterances
        no_delay=False,            # Reducir latencia (experimental)
        numerals=True,             # Formateo inteligente de números
        profanity_filter=True,     # Filtrar lenguaje ofensivo
        smart_format=True,         # Formateo inteligente del texto
    )

    deepgram = DeepgramClient("YOUR_API_KEY")
    connection = deepgram.listen.websocket.v("1")

    @connection.on(LiveTranscriptionEvents.Transcript)
    def handle_transcript(result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        is_final = getattr(result, 'is_final', True)
        speech_final = getattr(result, 'speech_final', True)

        # Mostrar diferentes tipos de resultados
        if is_final:
            print(f"[FINAL] {transcript}")
        elif speech_final:
            print(f"[SPEECH_FINAL] {transcript}")
        else:
            print(f"[INTERIM] {transcript}")

    @connection.on(LiveTranscriptionEvents.SpeechStarted)
    def handle_speech_started(speech_started, **kwargs):
        print(f"[🎤 VAD] Inicio de habla detectado: {speech_started}")

    @connection.on(LiveTranscriptionEvents.UtteranceEnd)
    def handle_utterance_end(utterance_end, **kwargs):
        print(f"[🎤 VAD] Fin de utterance: {utterance_end}")

    connection.start(options)
    print("🎤 Conectado con configuración avanzada de NOVA 3")
    print("Características activas:")
    print("  ✅ Interim Results - Resultados en tiempo real")
    print("  ✅ VAD Events - Detección de actividad de voz")
    print("  ✅ PII Redaction - Protección de datos personales")
    print("  ✅ Diarization - Identificación de hablantes")
    print("  ✅ Endpointing - Mejor segmentación")
    print("  ✅ Numerals - Formateo inteligente de números")
    print("  ✅ Profanity Filter - Filtrado de lenguaje ofensivo")

    await asyncio.sleep(15)  # Mantener conexión por 15 segundos
    connection.finish()

async def ejemplo_configuracion_optima():
    """Configuración óptima recomendada para NOVA 3"""
    print("\n🚀 Configuración Óptima para NOVA 3")

    # Configuración recomendada para máxima precisión
    options_optimas = {
        "model": "nova-3-general",
        "language": "multi",
        "interim_results": True,      # Siempre activado para tiempo real
        "endpointing": True,          # Mejor segmentación de habla
        "vad_events": True,           # Eventos de voz para mejor control
        "utterance_end_ms": 1000,     # 1 segundo de pausa
        "smart_format": True,         # Formateo inteligente
        "numerals": True,             # Números formateados
        "pii_redaction": False,       # Activar solo si es necesario
        "diarize": False,             # Activar para múltiples hablantes
        "profanity_filter": False,    # Depende de la aplicación
        "no_delay": False,            # Experimental, usar con cuidado
    }

    print("Configuración óptima recomendada:")
    for key, value in options_optimas.items():
        print(f"  {key}: {value}")

    # Crear opciones con configuración óptima
    options = LiveOptions(**options_optimas)

    deepgram = DeepgramClient("YOUR_API_KEY")
    connection = deepgram.listen.websocket.v("1")

    @connection.on(LiveTranscriptionEvents.Transcript)
    def handle_transcript(result, **kwargs):
        transcript = result.channel.alternatives[0].transcript
        confidence = result.channel.alternatives[0].confidence
        print(".3f")

    connection.start(options)
    print("🎤 Usando configuración óptima de NOVA 3")

    await asyncio.sleep(10)
    connection.finish()

def mostrar_variables_entorno():
    """Mostrar todas las variables de entorno disponibles para NOVA 3"""
    print("\n🔧 Variables de Entorno para NOVA 3:")
    print("""
# Configuración básica
DEEPGRAM_API_KEY=tu_api_key_aqui
DEEPGRAM_MODEL=nova-3-general
DEEPGRAM_LANGUAGE=multi

# Características avanzadas de NOVA 3
DEEPGRAM_INTERIM_RESULTS=true       # Resultados en tiempo real
DEEPGRAM_ENDPOINTING=true           # Mejor segmentación
DEEPGRAM_VAD_EVENTS=true            # Eventos de voz
DEEPGRAM_PII_REDACTION=false        # Protección de datos
DEEPGRAM_DIARIZE=false              # Identificación de hablantes
DEEPGRAM_UTTERANCE_END_MS=1000      # Control de pausa (ms)
DEEPGRAM_NO_DELAY=false             # Reducir latencia
DEEPGRAM_NUMERALS=true              # Formateo de números
DEEPGRAM_PROFANITY_FILTER=false     # Filtrar lenguaje ofensivo

# Configuración de audio
DEEPGRAM_MULTICHANNEL=true
DEEPGRAM_SMART_FORMAT=true
DEEPGRAM_SAMPLE_RATE=16000
    """)

async def main():
    """Función principal para ejecutar ejemplos"""
    print("🎯 Ejemplos de NOVA 3 con Deepgram")
    print("=" * 50)

    # Mostrar información sobre las variables de entorno
    mostrar_variables_entorno()

    print("\nSelecciona un ejemplo:")
    print("1. Básico - Configuración simple")
    print("2. Avanzado - Todas las características")
    print("3. Óptimo - Configuración recomendada")
    print("4. Solo mostrar configuración")

    try:
        choice = input("\nElige una opción (1-4): ").strip()

        if choice == "1":
            await ejemplo_nova_3_basico()
        elif choice == "2":
            await ejemplo_nova_3_avanzado()
        elif choice == "3":
            await ejemplo_configuracion_optima()
        elif choice == "4":
            mostrar_variables_entorno()
        else:
            print("Opción no válida")

    except KeyboardInterrupt:
        print("\nEjemplo interrumpido por el usuario")
    except Exception as e:
        print(f"Error en el ejemplo: {e}")

if __name__ == "__main__":
    print(__doc__)
    asyncio.run(main())
