#!/usr/bin/env python3
"""
Script para configurar el repositorio remoto de GitHub
Ejecutar después de crear el repositorio en GitHub
"""

import subprocess
import sys

def setup_github_remote():
    """Configurar el repositorio remoto de GitHub"""

    print("🚀 Configuración del repositorio remoto de GitHub")
    print("=" * 50)

    # Solicitar la URL del repositorio
    repo_url = input("Ingresa la URL de tu repositorio GitHub (https://github.com/usuario/repositorio.git): ").strip()

    if not repo_url:
        print("❌ URL requerida")
        return False

    try:
        # Verificar que sea una URL válida de GitHub
        if not repo_url.startswith("https://github.com/") or not repo_url.endswith(".git"):
            print("❌ La URL debe ser del formato: https://github.com/usuario/repositorio.git")
            return False

        # Configurar el remote origin
        print(f"📡 Configurando remote origin: {repo_url}")
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

        # Verificar la configuración
        print("🔍 Verificando configuración...")
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, check=True)
        print("Remotes configurados:")
        print(result.stdout)

        # Hacer push del commit inicial
        print("📤 Subiendo el código a GitHub...")
        subprocess.run(["git", "push", "-u", "origin", "master"], check=True)

        print("✅ ¡Repositorio subido exitosamente a GitHub!")
        print(f"🔗 URL del repositorio: {repo_url.replace('.git', '')}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error al configurar el repositorio: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = setup_github_remote()
    if success:
        print("\n🎉 ¡Listo! Tu proyecto está ahora en GitHub.")
        print("Puedes continuar trabajando y hacer push con: git push")
    else:
        print("\n❌ Revisa los pasos anteriores e intenta nuevamente.")
        sys.exit(1)
