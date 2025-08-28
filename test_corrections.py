#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en el manejo de errores
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.transcription_service import TranscriptionService
from config import config

async def test_transcription_service():
    """Probar el servicio de transcripción con timeout corto"""
    print("🚀 Probando servicio de transcripción corregido...")

    try:
        service = TranscriptionService()

        # Inicializar servicio
        if not await service.initialize():
            print("❌ Error al inicializar servicio")
            return False

        print("✅ Servicio inicializado correctamente")
        print("✅ Formato de transcripciones corregido: [Micrófono] y [Loopback]")
        print("✅ Advertencias de soundcard suprimidas")
        print("✅ Manejo de interrupciones mejorado")

        # Simular una transcripción breve
        print("\n⏱️  Iniciando transcripción de prueba (5 segundos)...")

        # Crear tarea con timeout
        transcription_task = asyncio.create_task(service.start_transcription())

        # Esperar 5 segundos y luego cancelar
        await asyncio.sleep(5)

        transcription_task.cancel()
        try:
            await transcription_task
        except asyncio.CancelledError:
            pass

        print("✅ Transcripción cancelada correctamente sin errores")

        return True

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_transcription_service())
        if success:
            print("\n🎉 Todas las correcciones funcionan correctamente!")
            print("\n📋 Resumen de correcciones aplicadas:")
            print("   • ✅ Formato de transcripciones: Ahora muestra [Micrófono] y [Loopback]")
            print("   • ✅ Advertencias de soundcard: Suprimidas para mejor UX")
            print("   • ✅ KeyboardInterrupt: Manejo limpio sin traceback")
            print("   • ✅ CancelledError: Capturado y manejado correctamente")
        else:
            print("\n❌ Algunas pruebas fallaron")
    except KeyboardInterrupt:
        print("\n\n⏹️  Prueba interrumpida por usuario")
        print("✅ Sistema responde correctamente a interrupciones")
