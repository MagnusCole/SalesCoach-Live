"""
Servicio de detección de objeciones para coaching de ventas.
Reglas instantáneas; si no hay match, opcionalmente llama a GPT-5 nano/mini (barato).
No bloquea: puedes hacerlo async y con timeout corto.
"""

import os
import re
import asyncio
import json
import aiohttp
from typing import Dict, Any
from services import playbooks

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-5-nano")  # o gpt-5-mini
USE_LLM = os.environ.get("USE_LLM_FALLBACK", "true").lower() == "true"
LLM_TIMEOUT = float(os.environ.get("LLM_TIMEOUT_SEC", "0.8"))  # objetivo < 800ms

# Reglas rápidas (ajústalas a tu mercado)
_RULES = [
    ("precio", r"\b(caro|carísimo|costo|coste|presupuesto|muy alto|carita)\b"),
    ("tiempo", r"\b(ahora no|más adelante|luego|ocupad[oa]|no tengo tiempo)\b"),
    ("autoridad", r"\b(tengo que consultarlo|mi jefe|no decido yo|comité)\b"),
    ("competencia", r"\b(ya usamos|trabajo con|proveedor|competencia|{COMPETIDOR})\b"),
    ("confianza", r"\b(no estoy seguro|no confío|dudo|no sé si funcione)\b"),
]

_PROMPT = (
    "Eres un coach de ventas. Dado el texto de un cliente, responde SOLO JSON:\n"
    "{\"is_objection\": bool, \"type\": \"precio|tiempo|autoridad|competencia|confianza|otro\", "
    "\"suggestion\": \"frase breve, concreta y cortés\"}\n"
    "Texto: "
)


async def _llm_analyze(text: str) -> Dict[str, Any]:
    """Analiza texto usando LLM como fallback"""
    if not OPENAI_KEY:
        return {"is_objection": False}

    payload = {
        "model": LLM_MODEL,
        "input": _PROMPT + text[:500],  # recorta para latencia/costo
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as s:
        try:
            async with s.post("https://api.openai.com/v1/responses", headers=headers, json=payload, timeout=LLM_TIMEOUT) as r:
                data = await r.json()
                txt = data.get("output_text") or data.get("output") or data.get("content")
                if isinstance(txt, list):
                    txt = txt[0]
                if not txt:
                    return {"is_objection": False}
                return json.loads(txt)
        except Exception:
            return {"is_objection": False}


def _rule_match(text: str) -> Dict[str, Any]:
    """Detecta objeciones usando reglas rápidas"""
    t = text.lower()
    for obj_type, pat in _RULES:
        if re.search(pat, t):
            sug = playbooks.suggest(obj_type, {})
            return {
                "is_objection": True,
                "type": obj_type,
                "suggestion": sug or "",
                "source": "rule",
                "confidence": 0.85
            }
    return {"is_objection": False}


async def analyze_segment(call_id: str, speaker: int, text: str, ts_ms: int) -> Dict[str, Any]:
    """
    Entrada: segmento del PROSPECTO.
    Salida: dict {is_objection, type, suggestion, confidence, source}
    """
    # 1) Reglas (instantáneo)
    res = _rule_match(text)
    if res["is_objection"]:
        return res

    # 2) Fallback LLM (opcional)
    if USE_LLM:
        ai = await _llm_analyze(text)
        if ai.get("is_objection"):
            typ = ai.get("type", "otro")
            sug = ai.get("suggestion", "")
            # intenta enriquecer con playbook si existe
            sug_pb = playbooks.suggest(typ, {}) or sug
            return {
                "is_objection": True,
                "type": typ,
                "suggestion": sug_pb,
                "source": "llm",
                "confidence": 0.65
            }

    return {"is_objection": False}


def analyze_segment_sync(call_id: str, speaker: int, text: str, ts_ms: int) -> Dict[str, Any]:
    """
    Versión síncrona para casos donde no se puede usar async
    """
    # Solo reglas, sin LLM
    return _rule_match(text)
