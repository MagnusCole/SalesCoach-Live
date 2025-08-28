"""
Modelos de dominio para el sistema de transcripción.
Define las entidades principales y tipos de datos.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class AudioFrame:
    """Representa un frame de audio"""
    data: bytes
    channels: int
    sample_rate: int
    timestamp: datetime
    duration_ms: float
    is_speech: bool = False
    rms_levels: List[float] = None

    def __post_init__(self):
        if self.rms_levels is None:
            self.rms_levels = []


@dataclass
class TranscriptionResult:
    """Resultado de transcripción"""
    transcript: str
    confidence: float
    is_final: bool
    channel_index: int
    speaker_id: Optional[str] = None
    language: Optional[str] = None
    timestamp: Optional[datetime] = None
    alternatives: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


@dataclass
@dataclass
class AudioDevice:
    """Información de dispositivo de audio"""
    id: str
    name: str
    channels: int
    sample_rate: int
    is_default: bool = False
    device_type: str = "microphone"  # microphone, speaker
    device_object: Optional[Any] = None  # Referencia al objeto real de soundcard


@dataclass
class VADResult:
    """Resultado de detección de actividad de voz"""
    has_voice: bool
    rms_levels: List[float]
    threshold: float
    confidence: float


@dataclass
class ConnectionStatus:
    """Estado de la conexión con Deepgram"""
    is_connected: bool
    url: str
    last_ping: Optional[datetime] = None
    reconnect_count: int = 0
    error_message: Optional[str] = None


@dataclass
class SessionStats:
    """Estadísticas de la sesión de transcripción"""
    start_time: datetime
    end_time: Optional[datetime] = None
    frames_sent: int = 0
    frames_silence: int = 0
    transcription_count: int = 0
    error_count: int = 0
    avg_rms_mic: float = 0.0
    avg_rms_loop: float = 0.0

    @property
    def duration(self) -> float:
        """Duración de la sesión en segundos"""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def silence_ratio(self) -> float:
        """Ratio de silencio en la sesión"""
        total = self.frames_sent + self.frames_silence
        return self.frames_silence / total if total > 0 else 0.0


@dataclass
class NOVA3Config:
    """Configuración específica de NOVA 3"""
    interim_results: bool = True
    endpointing: bool = True
    pii_redact: bool = False
    diarize: bool = False
    utterance_end_ms: int = 1000
    vad_events: bool = True
    no_delay: bool = False
    numerals: bool = True
    profanity_filter: bool = False
    smart_format: bool = True
