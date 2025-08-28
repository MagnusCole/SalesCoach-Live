"""
Sistema completo de coaching de ventas con persistencia
======================================================

Integra:
- Transcripción en tiempo real con Deepgram NOVA 3
- Detección de objeciones en tiempo real
- Persistencia completa de datos de llamadas
- Análisis automático de llamadas
- Exportación de transcripciones
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from services.transcription_service import TranscriptionService

async def main():
    """Función principal del sistema de coaching de ventas"""

    print("🚀 Iniciando sistema de coaching de ventas...")
    print("=" * 60)

    # Mostrar configuración
    if config.log_events:
        print(f"🌐 Deepgram Region: {config.dg_region}")
        print(f"🎵 Audio Mode: {config.audio_mode} ({config.stereo_layout})")
        print(f"🎯 Objection Detection: {'ON' if config.use_llm_fallback else 'OFF'}")
        print(f"💾 Storage: Always ON (local)")
        print(f"📊 Call Analysis: Always ON")
        print(f"📄 Auto Export: Always ON")
        print(f"🔄 Reconnect: {'ON' if config.reconnect_enabled else 'OFF'}")
        print()

    try:
        # Inicializar servicio de transcripción
        print("🔧 Inicializando servicio de transcripción...")
        transcription_service = TranscriptionService()

        print("✅ Servicio inicializado correctamente")
        print()

        # Iniciar transcripción
        print("🎙️ Iniciando transcripción... (Ctrl+C para detener)")
        print("-" * 40)

        await transcription_service.start_transcription()

    except KeyboardInterrupt:
        print("\n⏹️ Transcripción interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")
        if config.log_debug:
            import traceback
            traceback.print_exc()
    finally:
        print("\n🔚 Sistema finalizado")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        sys.exit(1)
