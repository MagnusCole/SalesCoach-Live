"""
Modelos de dominio y entidades del sistema de transcripción.
"""

from .models import (
    AudioFrame,
    TranscriptionResult,
    AudioDevice,
    VADResult,
    ConnectionStatus,
    SessionStats,
    NOVA3Config
)
from .entities import (
    AudioSource,
    TranscriptionService,
    AudioProcessor,
    DeviceManager,
    TranscriptionSession
)

__all__ = [
    # Models
    "AudioFrame",
    "TranscriptionResult",
    "AudioDevice",
    "VADResult",
    "ConnectionStatus",
    "SessionStats",
    "NOVA3Config",
    # Entities
    "AudioSource",
    "TranscriptionService",
    "AudioProcessor",
    "DeviceManager",
    "TranscriptionSession"
]
