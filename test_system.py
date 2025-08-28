"""
Script de prueba para verificar que el sistema de coaching de ventas funciona correctamente
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

async def test_imports():
    """Probar que todas las importaciones funcionan correctamente"""
    try:
        print("🔧 Probando importaciones...")

        # Importar configuración
        from config import config
        print("✅ Configuración importada")

        # Importar servicios
        from services.transcription_service import TranscriptionService
        print("✅ Servicio de transcripción importado")

        from services.storage import StorageService
        print("✅ Servicio de almacenamiento importado")

        from services.transcript_exporter import TranscriptExporter
        print("✅ Exportador de transcripciones importado")

        from services.call_analyzer import CallAnalyzer
        print("✅ Analizador de llamadas importado")

        from services.objection_service import analyze_segment
        print("✅ Servicio de objeciones importado")

        # Importar dominio
        from domain.entities import Call, Segment, Objection, Suggestion
        print("✅ Entidades del dominio importadas")

        print("\n🎉 Todas las importaciones funcionan correctamente!")
        return True

    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_service_initialization():
    """Probar que el servicio se puede inicializar"""
    try:
        print("\n🔧 Probando inicialización del servicio...")

        from services.transcription_service import TranscriptionService

        service = TranscriptionService()
        print("✅ Servicio de transcripción inicializado")

        # Verificar que tiene los atributos necesarios
        assert hasattr(service, 'storage'), "Falta atributo storage"
        assert hasattr(service, 'exporter'), "Falta atributo exporter"
        assert hasattr(service, 'analyzer'), "Falta atributo analyzer"
        print("✅ Todos los servicios internos están presentes")

        return True

    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Función principal de prueba"""
    print("🚀 Probando sistema de coaching de ventas...")
    print("=" * 60)

    # Probar importaciones
    imports_ok = await test_imports()

    if not imports_ok:
        print("\n❌ Las importaciones fallaron. Abortando pruebas.")
        return False

    # Probar inicialización
    init_ok = await test_service_initialization()

    if not init_ok:
        print("\n❌ La inicialización falló. Abortando pruebas.")
        return False

    print("\n🎉 Todas las pruebas pasaron exitosamente!")
    print("\n💡 El sistema está listo para usar. Ejecuta:")
    print("   python sales_coaching_system.py")
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Prueba interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Error crítico en pruebas: {e}")
        sys.exit(1)
