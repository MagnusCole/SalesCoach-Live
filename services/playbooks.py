"""
Servicio de playbooks para respuestas ganadoras en ventas.
Repositorio in-memory con persistencia en JSON (simple para MVP).
"""

import json
import os
from typing import Optional, Dict, Any, List
from domain.models import PlaybookEntry

_PLAYBOOK_PATH = os.environ.get("PLAYBOOK_JSON", "data/playbook.json")

_DEFAULT_ENTRIES: List[PlaybookEntry] = [
    PlaybookEntry("precio", None, None, "Podemos empezar con un piloto de 2 semanas para que midas ROI sin riesgo."),
    PlaybookEntry("tiempo", None, None, "Ajustamos el inicio a tus tiempos. ¿Qué tendría que pasar para que sí sea prioridad?"),
    PlaybookEntry("autoridad", None, None, "Agendemos 15 minutos con el decisor y resolvemos todo juntos."),
    PlaybookEntry("competencia", None, None, "Te muestro dónde ganamos frente a la competencia y cómo migramos sin fricción."),
    PlaybookEntry("confianza", None, None, "Te enseño métricas y 2 casos de tu industria para decidir con evidencia."),
]

_entries: List[PlaybookEntry] = []


def _load():
    """Carga las entradas del playbook desde JSON"""
    global _entries
    if os.path.exists(_PLAYBOOK_PATH):
        try:
            with open(_PLAYBOOK_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                _entries = [PlaybookEntry(**it) for it in data]
                return
        except Exception:
            pass
    _entries = list(_DEFAULT_ENTRIES)


def _save():
    """Guarda las entradas del playbook en JSON"""
    os.makedirs(os.path.dirname(_PLAYBOOK_PATH), exist_ok=True)
    with open(_PLAYBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump([e.__dict__ for e in _entries], f, ensure_ascii=False, indent=2)


# Cargar playbook al inicializar
_load()


def suggest(objection_type: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Sugiere una respuesta para un tipo de objeción específico.

    Args:
        objection_type: Tipo de objeción ("precio", "tiempo", etc.)
        context: Contexto adicional (industry, stage, etc.)

    Returns:
        Texto de sugerencia o None si no hay match
    """
    ctx = context or {}
    inds = ctx.get("industry")
    stage = ctx.get("stage")

    # 1) Match exacto por industria/etapa
    for e in sorted(_entries, key=lambda x: x.score, reverse=True):
        if (e.objection_type == objection_type and
            e.industry == inds and
            e.stage == stage):
            try:
                return e.text.format(**ctx)
            except KeyError:
                # Si faltan variables, usar versión sin formato
                return e.text

    # 2) Match por tipo de objeción
    for e in sorted(_entries, key=lambda x: x.score, reverse=True):
        if e.objection_type == objection_type:
            try:
                return e.text.format(**ctx)
            except KeyError:
                # Si faltan variables, usar versión sin formato
                return e.text

    return None


def learn(example: PlaybookEntry):
    """Añade una entrada ganadora (después de una venta exitosa)."""
    _entries.append(example)
    _save()


def get_all_entries() -> List[PlaybookEntry]:
    """Obtiene todas las entradas del playbook"""
    return _entries.copy()


def add_entry(entry: PlaybookEntry):
    """Añade una nueva entrada al playbook"""
    _entries.append(entry)
    _save()


def remove_entry(index: int):
    """Remueve una entrada del playbook por índice"""
    if 0 <= index < len(_entries):
        _entries.pop(index)
        _save()
