"""
Punto de entrada principal del sistema de transcripción Deepgram NOVA 3.
Arquitectura modular usando frameworks de clase mundial.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos locales
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from config import config, environment
from services import TranscriptionService
from core.devices import DeviceManager


async def main():
    """Función principal del programa"""
    try:
        # Mostrar banner
        print("🚀 Deepgram NOVA 3 Transcription System")
        print("=" * 50)

        # Validar configuración
        validation = environment.env_manager.validate_configuration()
        if not validation["valid"]:
            print("❌ Errores de configuración:")
            for issue in validation["issues"]:
                print(f"   - {issue}")
            return 1

        if validation["warnings"]:
            print("⚠️  Advertencias de configuración:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")

        # Mostrar configuración actual
        if config.log_events:
            print(f"🌐 Conectando a región: {config.dg_region} ({config.dg_base_wss})")
            print(f"🎵 Modo audio: {config.audio_mode} ({config.stereo_layout})")
            print(f"⚙️  VAD: {'ON' if config.vad_enabled else 'OFF'}, Normalización: {'ON' if config.normalize_enabled else 'OFF'}")
            print(f"🚀 NOVA 3 Features: Interim={'ON' if config.deepgram_interim_results else 'OFF'}, Endpointing={'ON' if config.deepgram_endpointing else 'OFF'}, PII Redaction={'ON' if config.deepgram_pii_redact else 'OFF'}")
            print(f"🔄 Reconexión: {'ON' if config.reconnect_enabled else 'OFF'}")

        # Inicializar servicio de transcripción
        service = TranscriptionService()

        # Inicializar dispositivos y configuración
        if not await service.initialize():
            print("❌ Error al inicializar el servicio")
            return 1

        # Iniciar transcripción
        await service.start_transcription()

        return 0

    except KeyboardInterrupt:
        print("\nBye")
        return 0
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        if config.logging.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
