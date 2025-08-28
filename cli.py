"""
Interfaz de línea de comandos para el sistema de transcripción.
Proporciona comandos para validación, configuración y ejecución.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

try:
    from config import config, environment
    CONFIG_AVAILABLE = True
except Exception as e:
    print(f"Error importing config: {e}")
    CONFIG_AVAILABLE = False

SERVICES_AVAILABLE = False
try:
    from services import TranscriptionService
    from core.devices import DeviceManager
    SERVICES_AVAILABLE = True
except Exception as e:
    # Crear clases dummy para modo limitado
    class DeviceManager:
        @staticmethod
        def list_microphones():
            return []
        @staticmethod
        def list_speakers():
            return []
    
    class TranscriptionService:
        async def initialize(self):
            return False


def print_banner():
    """Mostrar banner del sistema"""
    print(" Deepgram NOVA 3 Transcription System")
    print("=" * 50)
    print("Arquitectura modular usando frameworks de clase mundial")
    print()


def print_help():
    """Mostrar ayuda de comandos"""
    print("\n Comandos disponibles:")
    print("  validate    - Validar configuración del sistema")
    print("  devices     - Mostrar dispositivos de audio disponibles")
    print("  config      - Mostrar configuración actual")
    print("  transcribe  - Iniciar transcripción en tiempo real")
    print("  check       - Verificar estado del sistema")
    print("  help        - Mostrar esta ayuda")
    print()


def cmd_validate():
    """Validar configuración del sistema"""
    print("\n Validating Deepgram NOVA 3 System\n")
    
    try:
        # Importar y ejecutar validación
        from validate_sdk_v3 import validate_sdk_v3
        validate_sdk_v3()
        print("\n SDK validation completed!")
    except ImportError:
        print(" Validation module not found")
        print("   Run 'python validate_sdk_v3.py' directly")
    except Exception as e:
        print(f"\n SDK validation failed: {e}")


def cmd_devices():
    """Mostrar información de dispositivos de audio"""
    if not SERVICES_AVAILABLE:
        print("\n Device manager not available")
        return
        
    print("\n Audio Devices Information\n")
    
    print("  Microphones:")
    microphones = DeviceManager.list_microphones()
    for i, mic in enumerate(microphones):
        default = " (default)" if mic.is_default else ""
        print(f"   {i+1}. {mic.name}{default}")
    
    print("\n Speakers:")
    speakers = DeviceManager.list_speakers()
    for i, speaker in enumerate(speakers):
        default = " (default)" if speaker.is_default else ""
        print(f"   {i+1}. {speaker.name}{default}")


def cmd_config():
    """Mostrar configuración actual"""
    if not CONFIG_AVAILABLE:
        print("\n Configuration not available")
        return
        
    print("\n  Current Configuration\n")
    
    print("🔧 Deepgram Configuration:")
    print(f"   • Model: {config.deepgram_model}")
    print(f"   • Language: {config.deepgram_language}")
    print(f"   • Sample Rate: {config.deepgram_sample_rate}Hz")
    print(f"   • Interim Results: {'✅' if config.deepgram_interim_results else '❌'}")
    print(f"   • Endpointing: {'✅' if config.deepgram_endpointing else '❌'}")
    print(f"   • PII Redaction: {'✅' if config.deepgram_pii_redact else '❌'}")
    print(f"   • VAD Events: {'✅' if config.deepgram_vad_events else '❌'}")
    
    print("\n🎵 Audio Configuration:")
    print(f"   • Mic Pattern: '{config.mic_name_substr}'")
    print(f"   • Speaker Pattern: '{config.spk_name_substr}'")
    print(f"   • VAD Enabled: {'✅' if config.vad_enabled else '❌'}")
    print(f"   • Normalization: {'✅' if config.normalize_enabled else '❌'}")
    print(f"   • Audio Mode: {config.audio_mode}")
    print(f"   • Stereo Layout: {config.stereo_layout}")
    
    print("\n🌐 Connection Configuration:")
    print(f"   • Region: {config.dg_region}")
    print(f"   • Base URL: {config.dg_base_wss}")
    print(f"   • Reconnection: {'✅' if config.reconnect_enabled else '❌'}")
    print(f"   • Max Attempts: {config.max_reconnect_attempts}")


async def cmd_transcribe():
    """Iniciar sesión de transcripción"""
    if not SERVICES_AVAILABLE:
        print("\n Transcription service not available")
        return 1
        
    print("\n Starting Deepgram NOVA 3 Transcription\n")
    
    try:
        service = TranscriptionService()
        
        # Inicializar servicio
        if not await service.initialize():
            print(" Failed to initialize transcription service")
            return 1
        
        print(" Service initialized successfully!")
        print("  Ready for transcription. Speak or play audio...")
        print("   Press Ctrl+C to stop\n")
        
        # Iniciar transcripción
        await service.start_transcription()
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Audio capture interrupted by user")
        print("✅ Connection finished successfully")
        return 0
    except asyncio.CancelledError:
        print("\n\n⏹️  Audio capture interrupted by user")
        print("✅ Connection finished successfully")
        return 0
    except Exception as e:
        print(f"\n❌ Transcription error: {e}")
        if CONFIG_AVAILABLE and config.log_debug:
            import traceback
            traceback.print_exc()
        return 1


def cmd_check():
    """Verificar estado del sistema"""
    print("\n System Health Check\n")
    
    # Verificar configuración
    if CONFIG_AVAILABLE:
        try:
            validation = environment.env_manager.validate_configuration()
            
            if validation["valid"]:
                print(" Configuration is valid")
            else:
                print(" Configuration issues found:")
                for issue in validation["issues"]:
                    print(f"    {issue}")
            
            if validation["warnings"]:
                print("\n  Configuration warnings:")
                for warning in validation["warnings"]:
                    print(f"    {warning}")
        except Exception as e:
            print(f" Configuration validation error: {e}")
    else:
        print(" Configuration not available")
    
    # Verificar dispositivos
    if SERVICES_AVAILABLE:
        print("\n Checking audio devices...")
        microphones = DeviceManager.list_microphones()
        speakers = DeviceManager.list_speakers()
        
        if microphones and speakers:
            print(f" Found {len(microphones)} microphone(s) and {len(speakers)} speaker(s)")
        else:
            print(" Audio devices not found")
            if not microphones:
                print("    No microphones detected")
            if not speakers:
                print("    No speakers detected")
    else:
        print("\n Audio device check not available")
    
    # Verificar API key
    if CONFIG_AVAILABLE:
        if config.deepgram_api_key and config.deepgram_api_key != "tu_api_key_aqui":
            print(" API key is configured")
        else:
            print(" API key not configured")
            print("   → Configure DEEPGRAM_API_KEY in .env file")
            print("   → Get your API key from: https://console.deepgram.com/")
    else:
        print(" API key check not available")
    
    print("\n Health Check Complete")


def main():
    """Función principal del CLI"""
    print_banner()
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "validate":
        cmd_validate()
    elif command == "devices":
        cmd_devices()
    elif command == "config":
        cmd_config()
    elif command == "transcribe":
        try:
            exit_code = asyncio.run(cmd_transcribe())
        except KeyboardInterrupt:
            print("\n\n⏹️  Audio capture interrupted by user")
            print("✅ Connection finished successfully")
            exit_code = 0
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            exit_code = 1
        sys.exit(exit_code)
    elif command == "check":
        cmd_check()
    elif command == "help" or command == "--help" or command == "-h":
        print_help()
    else:
        print(f" Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()
