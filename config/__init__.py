"""
Configuración centralizada del sistema de transcripción.
"""

from .settings import config, AppConfig
from . import environment

__all__ = [
    "config",
    "AppConfig",
    "environment",
]
