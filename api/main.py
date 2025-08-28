import os, json, asyncio, uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
import websockets
from objection_service import analyze_text
from playbooks import load_playbook
from google.cloud import storage
from datetime import datetime
import io
import subprocess
import tempfile

DG_KEY = os.environ["DEEPGRAM_API_KEY"]
DG_MODEL = os.getenv("DEEPGRAM_MODEL", "nova-3-general")
DG_LANG  = os.getenv("DEEPGRAM_LANGUAGE", "es")  # "es" si 90% español, "multi" si code-switching
PLAYBOOK_PATH = os.getenv("PLAYBOOK_PATH", "data/playbook.json")

# Configuración de almacenamiento y audio
USE_GCS = os.getenv("USE_GCS", "false").lower() == "true"
USE_FFMPEG = os.getenv("USE_FFMPEG", "false").lower() == "true"
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "salescoach-calls")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "calls")

app = FastAPI()
playbook = load_playbook(PLAYBOOK_PATH)

# Almacenamiento de sesiones activas
active_sessions = {}

def get_storage_client():
    if USE_GCS:
        return storage.Client()
    return None

def convert_audio_with_ffmpeg(input_data: bytes) -> bytes:
    """Convierte audio WebM/Opus a PCM16 usando ffmpeg"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as input_file:
            input_file.write(input_data)
            input_file.flush()

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                # Comando ffmpeg para convertir a PCM16
                cmd = [
                    'ffmpeg', '-y', '-i', input_file.name,
                    '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
                    output_file.name
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

                if result.returncode != 0:
                    raise Exception(f"FFmpeg error: {result.stderr}")

                with open(output_file.name, 'rb') as f:
                    output_data = f.read()

                # Limpiar archivos temporales
                os.unlink(input_file.name)
                os.unlink(output_file.name)

                return output_data

    except Exception as e:
        print(f"Error convirtiendo audio con ffmpeg: {e}")
        return input_data  # Retornar original si falla

def save_to_storage(call_id: str, filename: str, data: bytes, content_type: str = "application/octet-stream"):
    if USE_GCS:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"{call_id}/{filename}")
        blob.upload_from_string(data, content_type=content_type)
        return f"gs://{GCS_BUCKET_NAME}/{call_id}/{filename}"
    else:
        # Guardar localmente
        os.makedirs(f"{LOCAL_STORAGE_PATH}/{call_id}", exist_ok=True)
        with open(f"{LOCAL_STORAGE_PATH}/{call_id}/{filename}", "wb") as f:
            f.write(data)
        return f"{LOCAL_STORAGE_PATH}/{call_id}/{filename}"

@app.get("/healthz")
def healthz():
    return {"ok": True, "sessions_active": len(active_sessions)}

@app.get("/calls/{call_id}/transcript.txt")
def get_transcript(call_id: str):
    if USE_GCS:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"{call_id}/transcript.txt")
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Transcript not found")
        content = blob.download_as_text()
    else:
        transcript_path = f"{LOCAL_STORAGE_PATH}/{call_id}/transcript.txt"
        if not os.path.exists(transcript_path):
            raise HTTPException(status_code=404, detail="Transcript not found")
        with open(transcript_path, "r", encoding="utf-8") as f:
            content = f.read()

    return content

@app.get("/calls/{call_id}/audio.webm")
def get_audio(call_id: str):
    if USE_GCS:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"{call_id}/audio.webm")
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Audio not found")
        return blob.download_as_bytes()
    else:
        audio_path = f"{LOCAL_STORAGE_PATH}/{call_id}/audio.webm"
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio not found")
        return FileResponse(audio_path, media_type="audio/webm", filename=f"call_{call_id}.webm")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.websocket("/ws/{call_id}")
async def ws_proxy(ws: WebSocket, call_id: str):
    await ws.accept()

    # Inicializar buffers para esta sesión
    audio_buffer = io.BytesIO()
    transcript_parts = []
    session_start = datetime.now()

    # Registrar sesión activa
    active_sessions[call_id] = {
        "start_time": session_start,
        "transcript_parts": transcript_parts,
        "audio_size": 0
    }

    # Configurar URL de Deepgram según modo
    if USE_FFMPEG:
        dg_url = (
            "wss://api.deepgram.com/v1/listen?"
            f"model={DG_MODEL}&language={DG_LANG}&smart_format=true&"
            "encoding=linear16&sample_rate=16000"
        )
    else:
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
                audio_buffer.write(data)           # Guardar audio original
                active_sessions[call_id]["audio_size"] += len(data)

                # Convertir con ffmpeg si está habilitado
                if USE_FFMPEG:
                    converted_data = await asyncio.get_event_loop().run_in_executor(
                        None, convert_audio_with_ffmpeg, data
                    )
                    await dg.send(converted_data)
                else:
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

                    # Agregar al transcript acumulado
                    transcript_parts.append(f"[{datetime.now().strftime('%H:%M:%S')}] {txt}")
                    active_sessions[call_id]["transcript_parts"] = transcript_parts

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

    try:
        await asyncio.gather(upstream(), downstream())
    finally:
        # Guardar archivos al finalizar la sesión
        try:
            # Guardar transcript
            transcript_content = "\n".join(transcript_parts)
            if transcript_content:
                save_to_storage(call_id, "transcript.txt", transcript_content.encode('utf-8'), "text/plain")

            # Guardar audio
            audio_data = audio_buffer.getvalue()
            if audio_data:
                save_to_storage(call_id, "audio.webm", audio_data, "audio/webm")

            # Limpiar sesión activa
            if call_id in active_sessions:
                del active_sessions[call_id]

        except Exception as e:
            print(f"Error guardando archivos para {call_id}: {e}")
