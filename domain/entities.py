"""
Entidades del dominio para el sistema de transcripción.
Representan los conceptos principales del negocio.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Optional, List, AsyncGenerator
from .models import AudioFrame, TranscriptionResult, AudioDevice, ConnectionStatus


class AudioSource(ABC):
    """Interfaz para fuentes de audio"""

    @abstractmethod
    async def start(self) -> None:
        """Iniciar captura de audio"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Detener captura de audio"""
        pass

    @abstractmethod
    async def get_frames(self) -> AsyncGenerator[AudioFrame, None]:
        """Obtener frames de audio"""
        pass

    @property
    @abstractmethod
    def device_info(self) -> AudioDevice:
        """Información del dispositivo"""
        pass


class TranscriptionService(Protocol):
    """Protocolo para servicios de transcripción"""

    async def connect(self) -> bool:
        """Conectar al servicio de transcripción"""
        pass

    async def disconnect(self) -> None:
        """Desconectar del servicio"""
        pass

    async def send_audio(self, frame: AudioFrame) -> None:
        """Enviar frame de audio para transcripción"""
        pass

    def on_transcript(self, callback: callable) -> None:
        """Registrar callback para resultados de transcripción"""
        pass

    def on_error(self, callback: callable) -> None:
        """Registrar callback para errores"""
        pass

    @property
    def connection_status(self) -> ConnectionStatus:
        """Estado de la conexión"""
        pass


class AudioProcessor(ABC):
    """Procesador de audio"""

    @abstractmethod
    def process_frame(self, frame: AudioFrame) -> AudioFrame:
        """Procesar un frame de audio"""
        pass

    @abstractmethod
    def detect_voice_activity(self, frame: AudioFrame) -> bool:
        """Detectar actividad de voz"""
        pass

    @abstractmethod
    def normalize_audio(self, frame: AudioFrame) -> AudioFrame:
        """Normalizar niveles de audio"""
        pass


class DeviceManager(ABC):
    """Administrador de dispositivos de audio"""

    @abstractmethod
    def list_microphones(self) -> List[AudioDevice]:
        """Listar micrófonos disponibles"""
        pass

    @abstractmethod
    def list_speakers(self) -> List[AudioDevice]:
        """Listar altavoces disponibles"""
        pass

    @abstractmethod
    def get_default_microphone(self) -> Optional[AudioDevice]:
        """Obtener micrófono por defecto"""
        pass

    @abstractmethod
    def get_default_speaker(self) -> Optional[AudioDevice]:
        """Obtener altavoz por defecto"""
        pass

    @abstractmethod
    def select_microphone(self, name_pattern: str) -> Optional[AudioDevice]:
        """Seleccionar micrófono por patrón de nombre"""
        pass

    @abstractmethod
    def select_speaker(self, name_pattern: str) -> Optional[AudioDevice]:
        """Seleccionar altavoz por patrón de nombre"""
        pass


class TranscriptionSession:
    """Sesión de transcripción completa"""

    def __init__(self,
                 audio_source: AudioSource,
                 transcription_service: TranscriptionService,
                 audio_processor: AudioProcessor):
        self.audio_source = audio_source
        self.transcription_service = transcription_service
        self.audio_processor = audio_processor
        self._running = False

    async def start(self) -> None:
        """Iniciar sesión de transcripción"""
        if self._running:
            return

        await self.transcription_service.connect()
        await self.audio_source.start()
        self._running = True

        # Procesar audio en tiempo real
        async for frame in self.audio_source.get_frames():
            if not self._running:
                break

            # Procesar frame
            processed_frame = self.audio_processor.process_frame(frame)

            # Enviar a transcripción si hay actividad de voz
            if self.audio_processor.detect_voice_activity(processed_frame):
                await self.transcription_service.send_audio(processed_frame)

    async def stop(self) -> None:
        """Detener sesión de transcripción"""
        self._running = False
        await self.audio_source.stop()
        await self.transcription_service.disconnect()

    @property
    def is_running(self) -> bool:
        """Verificar si la sesión está activa"""
        return self._running
