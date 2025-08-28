"""
Gestión de variables de entorno con validación y valores por defecto.
"""

import os
from typing import Optional, Any
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class EnvironmentManager:
    """Administrador de variables de entorno con validación"""

    @staticmethod
    def get_string(key: str, default: Optional[str] = None) -> Optional[str]:
        """Obtener variable de entorno como string"""
        return os.getenv(key, default)

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Obtener variable de entorno como boolean"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Obtener variable de entorno como integer"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            return default

    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        """Obtener variable de entorno como float"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            return default

    @staticmethod
    def require_string(key: str) -> str:
        """Obtener variable de entorno requerida"""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    @staticmethod
    def get_deepgram_url() -> str:
        """Construir URL de Deepgram basada en la región"""
        region = os.getenv("DG_REGION", "us")
        if region == "eu":
            return "wss://api.eu.deepgram.com"
        else:
            return os.getenv("DG_BASE_WSS", "wss://api.deepgram.com")

    @staticmethod
    def validate_configuration() -> dict[str, Any]:
        """Validar configuración completa y retornar estado"""
        issues = []
        warnings = []

        # Verificar API key
        if not os.getenv("DEEPGRAM_API_KEY"):
            issues.append("DEEPGRAM_API_KEY is required")

        # Verificar configuración de audio
        mic_substr = os.getenv("MIC_NAME_SUBSTR", "Blue Snowball")
        spk_substr = os.getenv("SPK_NAME_SUBSTR", "PRO")

        # Verificar valores numéricos
        try:
            frame_ms = int(os.getenv("FRAME_MS", "20"))
            if frame_ms <= 0:
                issues.append("FRAME_MS must be positive")
        except ValueError:
            issues.append("FRAME_MS must be a valid integer")

        try:
            sample_rate = int(os.getenv("DEEPGRAM_SAMPLE_RATE", "16000"))
            if sample_rate not in [8000, 16000, 22050, 44100, 48000]:
                warnings.append(f"Sample rate {sample_rate} may not be optimal")
        except ValueError:
            issues.append("DEEPGRAM_SAMPLE_RATE must be a valid integer")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config": {
                "region": os.getenv("DG_REGION", "us"),
                "audio_mode": os.getenv("AUDIO_MODE", "stereo"),
                "model": os.getenv("DEEPGRAM_MODEL", "nova-3-general"),
                "language": os.getenv("DEEPGRAM_LANGUAGE", "multi")
            }
        }


# Instancia global
env_manager = EnvironmentManager()
