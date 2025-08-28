"""
Gestión de dispositivos de audio.
Detecta, selecciona y configura dispositivos de audio disponibles.
"""

import soundcard as sc
from typing import List, Optional

from config import config
from domain import AudioDevice


class DeviceManager:
    """Administrador de dispositivos de audio"""

    @staticmethod
    def list_microphones() -> List[AudioDevice]:
        """Listar todos los micrófonos disponibles"""
        devices = []
        for mic in sc.all_microphones():
            devices.append(AudioDevice(
                id=str(mic.id),
                name=mic.name,
                channels=1,  # Micrófonos típicamente mono
                sample_rate=48000,  # Sample rate estándar
                is_default=mic == sc.default_microphone(),
                device_type="microphone",
                device_object=mic
            ))
        return devices

    @staticmethod
    def list_speakers() -> List[AudioDevice]:
        """Listar todos los altavoces disponibles"""
        devices = []
        for speaker in sc.all_speakers():
            devices.append(AudioDevice(
                id=str(speaker.id),
                name=speaker.name,
                channels=2,  # Altavoces típicamente estéreo
                sample_rate=48000,  # Sample rate estándar
                is_default=speaker == sc.default_speaker(),
                device_type="speaker",
                device_object=speaker
            ))
        return devices

    @staticmethod
    def get_default_microphone() -> Optional[AudioDevice]:
        """Obtener micrófono por defecto"""
        try:
            mic = sc.default_microphone()
            return AudioDevice(
                id=str(mic.id),
                name=mic.name,
                channels=1,
                sample_rate=48000,
                is_default=True,
                device_type="microphone",
                device_object=mic
            )
        except Exception:
            return None

    @staticmethod
    def get_default_speaker() -> Optional[AudioDevice]:
        """Obtener altavoz por defecto"""
        try:
            speaker = sc.default_speaker()
            return AudioDevice(
                id=str(speaker.id),
                name=speaker.name,
                channels=2,
                sample_rate=48000,
                is_default=True,
                device_type="speaker",
                device_object=speaker
            )
        except Exception:
            return None

    @staticmethod
    def select_microphone(name_pattern: str) -> Optional[AudioDevice]:
        """Seleccionar micrófono por patrón de nombre"""
        for mic in sc.all_microphones():
            if name_pattern.lower() in mic.name.lower():
                return AudioDevice(
                    id=str(mic.id),
                    name=mic.name,
                    channels=1,
                    sample_rate=48000,
                    is_default=mic == sc.default_microphone(),
                    device_type="microphone",
                    device_object=mic
                )
        return None

    @staticmethod
    def select_speaker(name_pattern: str) -> Optional[AudioDevice]:
        """Seleccionar altavoz por patrón de nombre"""
        for speaker in sc.all_speakers():
            if name_pattern.lower() in speaker.name.lower():
                return AudioDevice(
                    id=str(speaker.id),
                    name=speaker.name,
                    channels=2,
                    sample_rate=48000,
                    is_default=speaker == sc.default_speaker(),
                    device_type="speaker",
                    device_object=speaker
                )
        return None

    @staticmethod
    def create_loopback_device(speaker_device: AudioDevice) -> Optional[AudioDevice]:
        """Crear dispositivo de loopback desde un altavoz"""
        try:
            # Usar soundcard para crear dispositivo de loopback
            loopback = sc.get_microphone(id=speaker_device.id, include_loopback=True)
            return AudioDevice(
                id=str(loopback.id),
                name=f"{speaker_device.name} (Loopback)",
                channels=2,
                sample_rate=48000,
                is_default=False,
                device_type="loopback",
                device_object=loopback
            )
        except Exception:
            return None

    @staticmethod
    def print_device_info():
        """Imprimir información de dispositivos disponibles"""
        if not config.logging.events:
            return

        print("🔍 Dispositivos de audio disponibles:")
        print("   Micrófonos:")
        for mic in DeviceManager.list_microphones():
            default_mark = " (default)" if mic.is_default else ""
            print(f"     - {mic.name}{default_mark}")

        print("   Altavoces:")
        for speaker in DeviceManager.list_speakers():
            default_mark = " (default)" if speaker.is_default else ""
            print(f"     - {speaker.name}{default_mark}")

    @staticmethod
    def validate_devices(mic_pattern: str, speaker_pattern: str) -> dict:
        """Validar que los dispositivos seleccionados estén disponibles"""
        mic = DeviceManager.select_microphone(mic_pattern)
        speaker = DeviceManager.select_speaker(speaker_pattern)

        issues = []

        if not mic:
            issues.append(f"No se encontró micrófono con patrón '{mic_pattern}'")
        if not speaker:
            issues.append(f"No se encontró altavoz con patrón '{speaker_pattern}'")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "devices": {
                "microphone": mic,
                "speaker": speaker
            }
        }
