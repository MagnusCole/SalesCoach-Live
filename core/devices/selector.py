"""
Selector inteligente de dispositivos de audio.
Proporciona selección automática y manual de dispositivos.
"""

from typing import Optional, Tuple
import re

from config import config
from domain import AudioDevice
from .manager import DeviceManager


class DeviceSelector:
    """Selector inteligente de dispositivos de audio"""

    def __init__(self):
        self.device_manager = DeviceManager()

    def select_devices(self) -> Tuple[Optional[AudioDevice], Optional[AudioDevice]]:
        """
        Seleccionar dispositivos de audio automáticamente.
        
        Returns:
            Tupla de (micrófono, altavoz)
        """
        # Intentar seleccionar por patrón configurado
        mic = self.device_manager.select_microphone(config.mic_name_substr)
        speaker = self.device_manager.select_speaker(config.spk_name_substr)

        # Si no se encuentra por patrón, usar por defecto
        if not mic:
            mic = self.device_manager.get_default_microphone()
            if config.log_events:
                print(f"⚠️  Usando micrófono por defecto: {mic.name if mic else 'Ninguno'}")
        
        if not speaker:
            speaker = self.device_manager.get_default_speaker()
            if config.log_events:
                print(f"⚠️  Usando altavoz por defecto: {speaker.name if speaker else 'Ninguno'}")

        return mic, speaker

    def select_optimal_devices(self) -> Tuple[Optional[AudioDevice], Optional[AudioDevice]]:
        """
        Seleccionar dispositivos óptimos (alias de select_devices para compatibilidad)
        
        Returns:
            Tupla de (micrófono, altavoz)
        """
        return self.select_devices()

    def get_device_info(self, mic: AudioDevice, speaker: AudioDevice) -> str:
        """Obtener información formateada de dispositivos"""
        return f"[MIC] {mic.name} (buscando: '{config.mic_name_substr}')\n[LOOP] {speaker.name} via {speaker.name} (buscando: '{config.spk_name_substr}')"
