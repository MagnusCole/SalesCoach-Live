"""
Normalización de audio con algoritmos avanzados.
"""

import numpy as np
from typing import Optional

from config import config


class AudioNormalizer:
    """Normalizador de audio con múltiples algoritmos"""

    def __init__(self):
        self.target_level = config.normalize_target_level
        self.history_size = 50
        self.level_history: list[float] = []

    def normalize(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Normalizar audio aplicando compresión y limitación.

        Args:
            audio_data: Array numpy con forma (samples, channels)

        Returns:
            Audio normalizado
        """
        if not config.normalize_enabled:
            return audio_data

        normalized = audio_data.copy()

        for channel in range(audio_data.shape[1]):
            channel_data = audio_data[:, channel]

            # Calcular nivel RMS actual
            current_level = np.sqrt(np.mean(channel_data**2))

            # Actualizar historial
            self.level_history.append(current_level)
            if len(self.level_history) > self.history_size:
                self.level_history.pop(0)

            # Calcular nivel promedio del historial para estabilidad
            if len(self.level_history) >= 5:
                avg_level = np.mean(self.level_history[-5:])
            else:
                avg_level = current_level

            # Evitar división por cero
            if avg_level > 0.001:
                # Calcular ratio de normalización
                ratio = self.target_level / avg_level

                # Aplicar compresión suave
                ratio = self._apply_compression(ratio, current_level)

                # Limitar amplificación máxima para evitar clipping extremo
                ratio = np.clip(ratio, 0.1, 3.0)

                # Aplicar normalización
                normalized[:, channel] = np.clip(channel_data * ratio, -0.95, 0.95)

        return normalized

    def _apply_compression(self, ratio: float, current_level: float) -> float:
        """
        Aplicar compresión suave para evitar cambios bruscos.

        Args:
            ratio: Ratio de normalización calculado
            current_level: Nivel actual del audio

        Returns:
            Ratio comprimido
        """
        # Compresión suave basada en el nivel actual
        if current_level < 0.1:
            # Audio muy bajo - permitir más amplificación
            return ratio * 1.2
        elif current_level > 0.8:
            # Audio muy alto - reducir amplificación
            return ratio * 0.8
        else:
            # Audio normal - mantener ratio
            return ratio

    def reset(self):
        """Reiniciar historial de niveles"""
        self.level_history.clear()

    def get_statistics(self) -> dict:
        """Obtener estadísticas de normalización"""
        if not self.level_history:
            return {"samples": 0, "avg_level": 0.0, "max_level": 0.0, "min_level": 0.0}

        return {
            "samples": len(self.level_history),
            "avg_level": np.mean(self.level_history),
            "max_level": np.max(self.level_history),
            "min_level": np.min(self.level_history),
            "target_level": self.target_level
        }

    def set_target_level(self, level: float):
        """Establecer nivel objetivo de normalización"""
        self.target_level = max(0.1, min(1.0, level))
