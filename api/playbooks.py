import json

def load_playbook(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    # Normalizar a dict por tipo
    out = {}
    for it in items:
        out[it["objection_type"]] = it["text"]
    return out
