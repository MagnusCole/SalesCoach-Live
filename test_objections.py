#!/usr/bin/env python3
"""
Script de prueba para el sistema de detección de objeciones.
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.objection_service import analyze_segment
from services.playbooks import suggest

async def test_objection_detection():
    """Probar la detección de objeciones"""
    print("🚀 Probando sistema de detección de objeciones...")
    print("=" * 60)

    # Casos de prueba
    test_cases = [
        ("Me parece caro", "precio"),
        ("Ahora no es buen momento", "tiempo"),
        ("Tengo que consultarlo con mi jefe", "autoridad"),
        ("Ya trabajamos con otro proveedor", "competencia"),
        ("No estoy seguro si funcionará", "confianza"),
        ("Hola, ¿cómo estás?", None),  # No es objeción
    ]

    for text, expected_type in test_cases:
        print(f"\n📝 Probando: '{text}'")

        # Probar análisis de segmento
        result = await analyze_segment(
            call_id="test_call",
            speaker=1,  # Prospecto
            text=text,
            ts_ms=1000
        )

        if result.get("is_objection"):
            print(f"   ✅ Detectada objeción: {result['type']}")
            print(f"   💡 Sugerencia: {result.get('suggestion', 'N/A')}")
            print(f"   🔍 Fuente: {result.get('source', 'N/A')}")
            print(".2f")
        else:
            print("   ❌ No es objeción")

        # Verificar si coincide con lo esperado
        if expected_type:
            if result.get("is_objection") and result.get("type") == expected_type:
                print("   🎯 ¡Coincide con lo esperado!")
            else:
                print(f"   ⚠️  Esperado: {expected_type}, Detectado: {result.get('type', 'ninguno')}")
        else:
            if not result.get("is_objection"):
                print("   🎯 ¡Correctamente identificado como no objeción!")
            else:
                print(f"   ⚠️  No debería ser objeción, pero detectada como: {result.get('type')}")

    print("\n" + "=" * 60)
    print("🏆 Prueba completada!")

if __name__ == "__main__":
    asyncio.run(test_objection_detection())
