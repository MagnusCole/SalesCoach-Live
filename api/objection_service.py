import re, os
USE_LLM = os.getenv("USE_LLM_FALLBACK", "false").lower() == "true"

KEYS = {
  "precio":      [r"\bcar[oa]s?\b", r"\bprecio\b", r"\bcar[íi]simo\b"],
  "tiempo":      [r"\bno tengo tiempo\b", r"\bdespu[eé]s\b", r"\bluego\b"],
  "autoridad":   [r"\btengo que (consultar|hablar)\b", r"\bmi jefe\b"],
  "confianza":   [r"\bno conf[ií]o\b", r"\bno estoy seguro\b", r"\bdem[uú]estr"],
  "competencia": [r"\botro proveedor\b", r"\bye tengo\b", r"\buso (.+)\b"],
}

def _match_rule(text: str):
    t = text.lower()
    for k, pats in KEYS.items():
        for p in pats:
            if re.search(p, t):
                return k
    return None

def analyze_text(text: str, playbook: dict) -> dict | None:
    t = text.strip()
    if not t:
        return None
    typ = _match_rule(t)
    if typ:
        return {
            "is_objection": True,
            "type": typ,
            "suggestion": playbook.get(typ) or "",
            "confidence": 0.92
        }

    # Fallback LLM opcional (puedes conectarlo luego)
    if USE_LLM:
        # TODO: llamar a gpt-5-nano con un prompt corto y devolver JSON
        pass

    return {"is_objection": False}
