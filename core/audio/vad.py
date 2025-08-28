"""
Detección de actividad de voz (VAD) usando RMS y algoritmos avanzados.
"""

import numpy as np
from typing import List

from config import config
from domain import VADResult


class VoiceActivityDetector:
    """Detector de actividad de voz usando múltiples métricas"""

    def __init__(self):
        self.threshold = config.vad_threshold
        self.history_size = 10
        self.voice_history: List[bool] = []
        self.rms_history: List[float] = []

    def detect(self, audio_data: np.ndarray) -> VADResult:
        """
        Detectar actividad de voz en datos de audio.

        Args:
            audio_data: Array numpy con forma (samples, channels)

        Returns:
            VADResult con información de detección
        """
        # Calcular RMS por canal
        rms_levels = np.sqrt(np.mean(audio_data**2, axis=0))

        # RMS promedio ponderado (dar más peso al canal principal)
        if config.stereo_layout == "LR":
            # Mic es canal izquierdo (índice 0)
            primary_rms = rms_levels[0]
            secondary_rms = rms_levels[1] if len(rms_levels) > 1 else 0
        else:
            # Loopback es canal izquierdo (índice 0)
            primary_rms = rms_levels[0]
            secondary_rms = rms_levels[1] if len(rms_levels) > 1 else 0

        # Promedio ponderado
        avg_rms = 0.7 * primary_rms + 0.3 * secondary_rms

        # Aplicar umbral básico
        has_voice = avg_rms > self.threshold

        # Aplicar filtro de historia para reducir falsos positivos
        self.voice_history.append(has_voice)
        self.rms_history.append(avg_rms)

        # Mantener tamaño de historia
        if len(self.voice_history) > self.history_size:
            self.voice_history.pop(0)
            self.rms_history.pop(0)

        # Aplicar filtro de mayoría para estabilidad
        if len(self.voice_history) >= 3:
            voice_count = sum(self.voice_history[-3:])
            has_voice = voice_count >= 2  # Al menos 2 de los últimos 3 frames

        # Calcular confianza basada en la consistencia
        if len(self.rms_history) >= 3:
            rms_std = np.std(self.rms_history[-3:])
            rms_mean = np.mean(self.rms_history[-3:])
            confidence = min(1.0, rms_mean / (rms_std + 0.001))
        else:
            confidence = 0.5

        return VADResult(
            has_voice=has_voice,
            rms_levels=rms_levels.tolist(),
            threshold=self.threshold,
            confidence=confidence
        )

    def update_threshold(self, new_threshold: float):
        """Actualizar umbral de detección"""
        self.threshold = max(0.001, min(1.0, new_threshold))

    def reset(self):
        """Reiniciar historial"""
        self.voice_history.clear()
        self.rms_history.clear()

    def get_statistics(self) -> dict:
        """Obtener estadísticas de detección"""
        if not self.rms_history:
            return {"samples": 0, "avg_rms": 0.0, "max_rms": 0.0, "voice_ratio": 0.0}

        return {
            "samples": len(self.rms_history),
            "avg_rms": np.mean(self.rms_history),
            "max_rms": np.max(self.rms_history),
            "voice_ratio": sum(self.voice_history) / len(self.voice_history) if self.voice_history else 0.0
        }
