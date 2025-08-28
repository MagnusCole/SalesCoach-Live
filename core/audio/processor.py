"""
Procesador de audio principal.
Maneja captura, procesamiento y normalización de audio.
"""

import asyncio
import numpy as np
import soundcard as sc
import warnings
from typing import Optional, List, AsyncGenerator
from datetime import datetime

# Parche para NumPy 2.x y soundcard
if hasattr(np, "frombuffer"):
    np.fromstring = np.frombuffer

# Suprimir advertencias de soundcard para mejor UX
warnings.filterwarnings("ignore", category=UserWarning, module="soundcard")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="soundcard")

from config import config
from domain import AudioFrame, AudioDevice, VADResult
from domain.entities import AudioSource
from .vad import VoiceActivityDetector
from .normalizer import AudioNormalizer


class AudioProcessor:
    """Procesador principal de audio con todas las funcionalidades"""

    def __init__(self):
        self.vad_detector = VoiceActivityDetector()
        self.normalizer = AudioNormalizer()
        self._mic_device: Optional[AudioDevice] = None
        self._loop_device: Optional[AudioDevice] = None
        self._running = False

    def set_devices(self, mic_device: AudioDevice, loop_device: AudioDevice):
        """Configurar dispositivos de audio"""
        self._mic_device = mic_device
        self._loop_device = loop_device

    async def start_capture(self) -> AsyncGenerator[AudioFrame, None]:
        """Iniciar captura de audio y generar frames procesados"""
        if not self._mic_device or not self._loop_device:
            raise RuntimeError("Devices not configured")

        self._running = True

        # Configurar constantes de audio
        fs_cap = 48000
        block = int(fs_cap * config.frame_ms / 1000.0)

        try:
            with self._mic_device.device_object.recorder(fs_cap, channels=1, blocksize=block) as mic_rec, \
                 self._loop_device.device_object.recorder(fs_cap, channels=2, blocksize=block) as loop_rec:

                if config.log_events:
                    layout_desc = "L=Mic/R=Loopback" if config.stereo_layout == "LR" else "L=Loopback/R=Mic"
                    print(f"🎙️ {layout_desc}. Habla y reproduce algo. Ctrl+C para salir.")

                printed_shape = False

                while self._running:
                    # Capturar audio
                    mic_buffer = mic_rec.record(numframes=block)
                    loop_buffer = loop_rec.record(numframes=block)

                    # Aplicar ganancia
                    if config.mic_gain != 1.0:
                        mic_buffer = np.clip(mic_buffer * config.mic_gain, -1, 1)
                    if config.loop_gain != 1.0:
                        loop_buffer = np.clip(loop_buffer * config.loop_gain, -1, 1)

                    # Convertir loopback a mono
                    loop_mono = loop_buffer.mean(axis=1, keepdims=True)

                    n = min(mic_buffer.shape[0], loop_mono.shape[0])
                    if n <= 0:
                        await asyncio.sleep(0)
                        continue

                    # Configurar canales según layout
                    if config.stereo_layout == "LR":
                        # L=Mic, R=Loopback
                        stereo_48k = np.concatenate([mic_buffer[:n], loop_mono[:n]], axis=1)
                    else:
                        # L=Loopback, R=Mic
                        stereo_48k = np.concatenate([loop_mono[:n], mic_buffer[:n]], axis=1)

                    # Normalizar si está habilitado
                    if config.normalize_enabled:
                        stereo_48k = self.normalizer.normalize(stereo_48k)

                    # Resampling a 16kHz para Deepgram
                    stereo_16k = self._resample_audio(stereo_48k, fs_cap, config.deepgram_sample_rate)

                    if not printed_shape and config.log_debug:
                        print("shape@16k =", stereo_16k.shape)
                        printed_shape = True

                    # Detectar actividad de voz
                    vad_result = self.vad_detector.detect(stereo_16k)

                    # Calcular niveles RMS
                    mic_level = float(np.sqrt(np.mean(mic_buffer[:n]**2)))
                    loop_level = float(np.sqrt(np.mean(loop_mono[:n]**2)))

                    # Crear frame de audio
                    frame = AudioFrame(
                        data=self._to_pcm16(stereo_16k),
                        channels=2,
                        sample_rate=config.deepgram_sample_rate,
                        timestamp=datetime.now(),
                        duration_ms=config.frame_ms,
                        is_speech=vad_result.has_voice,
                        rms_levels=[mic_level, loop_level]
                    )

                    yield frame

        except KeyboardInterrupt:
            if config.log_events:
                print("\n⏹️  Audio capture interrupted by user")
        except Exception as e:
            if config.log_events:
                print(f"❌ Audio capture error: {e}")
        finally:
            self._running = False

    def stop_capture(self):
        """Detener captura de audio"""
        self._running = False

    def _resample_audio(self, audio_data: np.ndarray, fs_in: int, fs_out: int) -> np.ndarray:
        """Resampling mejorado con soporte para scipy"""
        if fs_in == fs_out or audio_data.size == 0:
            return audio_data.astype(np.float32, copy=False)

        n = audio_data.shape[0]
        m = int(round(n * fs_out / fs_in))

        try:
            # Intentar usar scipy para mejor calidad
            from scipy.signal import resample_poly
            ratio = fs_out / fs_in
            up = int(np.ceil(ratio * 100))
            down = 100
            gcd = np.gcd(up, down)
            up, down = up // gcd, down // gcd

            resampled = np.zeros((m, audio_data.shape[1]), dtype=np.float32)
            for c in range(audio_data.shape[1]):
                resampled[:, c] = resample_poly(audio_data[:, c], up, down)
            return resampled[:m]
        except ImportError:
            # Fallback a interpolación lineal
            ti = np.linspace(0, 1, n, endpoint=False, dtype=np.float32)
            to = np.linspace(0, 1, m, endpoint=False, dtype=np.float32)
            return np.stack([np.interp(to, ti, audio_data[:, c]).astype(np.float32)
                           for c in range(audio_data.shape[1])], axis=1)

    def _to_pcm16(self, x: np.ndarray) -> bytes:
        """Convertir audio float32 a PCM 16-bit"""
        return (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()

    @property
    def is_capturing(self) -> bool:
        """Verificar si está capturando audio"""
        return self._running
