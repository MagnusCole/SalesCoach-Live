import os, json, asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import websockets
from objection_service import analyze_text
from playbooks import load_playbook

DG_KEY = os.environ["DEEPGRAM_API_KEY"]
DG_MODEL = os.getenv("DEEPGRAM_MODEL", "nova-3-general")
DG_LANG  = os.getenv("DEEPGRAM_LANGUAGE", "multi")  # "es" si 100% español
PLAYBOOK_PATH = os.getenv("PLAYBOOK_PATH", "data/playbook.json")

app = FastAPI()
playbook = load_playbook(PLAYBOOK_PATH)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.websocket("/ws/{call_id}")
async def ws_proxy(ws: WebSocket, call_id: str):
    await ws.accept()
    dg_url = (
        "wss://api.deepgram.com/v1/listen?"
        f"model={DG_MODEL}&language={DG_LANG}&smart_format=true&"
        "encoding=opus&sample_rate=48000"
    )
    dg = await websockets.connect(
        dg_url,
        extra_headers=[("Authorization", f"Token {DG_KEY}")],
        ping_interval=5,
        max_size=None
    )

    async def upstream():
        try:
            while True:
                data = await ws.receive_bytes()    # Opus/webm chunks
                await dg.send(data)                # Relay → Deepgram
        except WebSocketDisconnect:
            pass
        finally:
            await dg.close()

    async def downstream():
        # Recibe JSON de Deepgram → extrae transcript → analiza objeciones
        try:
            async for msg in dg:
                try:
                    obj = json.loads(msg)
                except Exception:
                    continue

                # Transmitir bruto al front
                await ws.send_text(msg)

                # Extraer texto del canal (cliente)
                results = obj.get("results") or []
                for r in results:
                    alts = (r.get("alternatives") or
                            (r.get("channel", {}).get("alternatives") or []))
                    if not alts: 
                        continue
                    txt = (alts[0].get("transcript") or "").strip()
                    if not txt:
                        continue

                    # Analizar texto: detectar objeción + sugerencias
                    det = analyze_text(txt, playbook)
                    if det and det.get("is_objection"):
                        await ws.send_text(json.dumps({
                            "type": "objection_detected",
                            "obj_type": det["type"],
                            "snippet": txt,
                            "suggestion": det["suggestion"],
                            "confidence": det.get("confidence", 0.9)
                        }))
        finally:
            await ws.close()

    await asyncio.gather(upstream(), downstream())
