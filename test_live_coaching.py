#!/usr/bin/env python3
"""
Prueba del sistema completo de coaching con audio real.
Instrucciones para el usuario para probar el sistema.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.transcription_service import TranscriptionService

async def test_live_coaching():
    """Prueba el sistema de coaching con audio real"""
    print("🎯 Prueba del Sistema de Coaching con Audio Real")
    print("=" * 60)
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Asegúrate de tener configurado tu DEEPGRAM_API_KEY en .env")
    print("2. Habla al micrófono y reproduce audio para probar multichannel")
    print("3. Di frases con objeciones para ver la detección en acción:")
    print("   • 'Me parece caro'")
    print("   • 'Ahora no es buen momento'")
    print("   • 'Tengo que consultarlo con mi jefe'")
    print("   • 'Ya trabajamos con otro proveedor'")
    print("   • 'No estoy seguro si funcionará'")
    print()
    print("4. Presiona Ctrl+C para detener")
    print()

    # Crear servicio de transcripción
    service = TranscriptionService()

    # Configurar callbacks para mostrar eventos de coaching
    def on_transcript_update(data):
        speaker_name = "Tú" if data["speaker"] == 0 else "Prospecto"
        print(f"📝 [{speaker_name}] {data['text']}")

    def on_objection_detected(data):
        print(f"\n🚨 ¡OBJECIÓN DETECTADA!")
        print(f"   Tipo: {data['type'].upper()}")
        print(f"   Texto: '{data['text']}'")
        print(".2f")
        print(f"   Fuente: {data['source']}\n")

    def on_suggestion_ready(data):
        print(f"💡 RESPUESTA SUGERIDA:")
        print(f"   '{data['text']}'")
        print("   (Esta respuesta está lista para copiar y usar)\n")

    # Registrar callbacks
    service.on_event("transcript_update", on_transcript_update)
    service.on_event("objection_detected", on_objection_detected)
    service.on_event("suggestion_ready", on_suggestion_ready)

    try:
        print("🎙️  Inicializando sistema...")
        print("🔄 Conectando a Deepgram...")

        # Inicializar servicio
        if not await service.initialize():
            print("❌ Error al inicializar el servicio")
            return

        print("✅ Sistema listo!")
        print("🎤 Comienza a hablar... (Presiona Ctrl+C para detener)")
        print("-" * 60)

        # Iniciar transcripción
        await service.start_transcription()

    except KeyboardInterrupt:
        print("\n\n⏹️  Prueba finalizada por el usuario")
        print("✅ Sistema de coaching funcionando correctamente!")
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await service.stop_transcription()

if __name__ == "__main__":
    print("🚀 Iniciando prueba del sistema de coaching con audio real...")
    asyncio.run(test_live_coaching())
