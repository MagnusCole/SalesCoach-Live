import os, json, asyncio, uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
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
DG_LANG  = os.getenv("DEEPGRAM_LANGUAGE", "multi")  # "multi" para mejor soporte de code-switching
PLAYBOOK_PATH = os.getenv("PLAYBOOK_PATH", "data/playbook.json")

# Configuración de almacenamiento y audio
USE_GCS = os.getenv("USE_GCS", "false").lower() == "true"
USE_FFMPEG = os.getenv("USE_FFMPEG", "false").lower() == "true"
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "salescoach-calls")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "calls")

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

playbook = load_playbook(PLAYBOOK_PATH)

# Almacenamiento de sesiones activas
active_sessions = {}

def get_storage_client():
    if USE_GCS:
        return storage.Client()
    return None

def convert_audio_with_ffmpeg(input_data: bytes) -> bytes:
    """Convierte audio WebM/Opus a PCM16 usando ffmpeg de manera optimizada"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as input_file:
            input_file.write(input_data)
            input_file.flush()

            with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as output_file:
                # Comando ffmpeg optimizado para baja latencia
                cmd = [
                    'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                    '-i', input_file.name,
                    '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
                    '-f', 's16le',  # Formato raw para menor overhead
                    output_file.name
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode != 0:
                    print(f"FFmpeg error: {result.stderr}")
                    return input_data  # Devolver original si falla

                with open(output_file.name, 'rb') as f:
                    converted_data = f.read()

        # Limpiar archivos temporales
        os.unlink(input_file.name)
        os.unlink(output_file.name)

        return converted_data

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

async def session_timeout_handler(ws: WebSocket, call_id: str, timeout_seconds: int):
    """Maneja el timeout de sesión y cierra WS de manera limpia"""
    try:
        await asyncio.sleep(timeout_seconds)

        # Verificar si la sesión aún existe
        if call_id in active_sessions:
            print(f"Session {call_id} reached {timeout_seconds//60} minute timeout, closing cleanly")

            # Enviar mensaje de timeout al frontend
            try:
                await ws.send_text(json.dumps({
                    "type": "session_timeout",
                    "message": f"Sesión finalizada automáticamente después de {timeout_seconds//60} minutos",
                    "call_id": call_id
                }))
            except Exception:
                pass  # WS ya puede estar cerrado

            # Cerrar WebSocket
            try:
                await ws.close(code=1000, reason="Session timeout")
            except Exception:
                pass

            # Limpiar sesión
            if call_id in active_sessions:
                del active_sessions[call_id]

    except asyncio.CancelledError:
        # Tarea cancelada, salir limpiamente
        pass
    except Exception as e:
        print(f"Error in session timeout handler for {call_id}: {e}")

@app.get("/healthz")
def healthz():
    return {"ok": True, "sessions_active": len(active_sessions)}

@app.post("/upload-final/{call_id}")
async def upload_final_audio(call_id: str, file: UploadFile = File(...)):
    """Recibe el blob final de audio WebM y lo guarda"""
    try:
        # Leer el contenido del archivo
        audio_data = await file.read()

        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided")

        # Guardar el audio usando la función existente
        save_to_storage(call_id, "audio.webm", audio_data, "audio/webm")

        return {"ok": True, "message": f"Audio saved for call {call_id}", "size": len(audio_data)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving audio: {str(e)}")

@app.post("/coach/{call_id}/toggle")
async def toggle_coach(call_id: str, enabled: bool):
    """Activa/desactiva el análisis de objeciones para una sesión"""
    if call_id in active_sessions:
        active_sessions[call_id]["coach_enabled"] = enabled
        return {"ok": True, "coach_enabled": enabled, "call_id": call_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

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

    return PlainTextResponse(content, media_type="text/plain", headers={"Content-Disposition": f"attachment; filename=transcript_{call_id}.txt"})

@app.get("/calls/{call_id}/audio.webm")
def get_audio(call_id: str):
    if USE_GCS:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(f"{call_id}/audio.webm")
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Audio not found")

        # Usar StreamingResponse para archivos grandes desde GCS
        def generate():
            with blob.open("rb") as f:
                while chunk := f.read(8192):  # Leer en chunks de 8KB
                    yield chunk

        return StreamingResponse(
            generate(),
            media_type="audio/webm",
            headers={"Content-Disposition": f"attachment; filename=audio_{call_id}.webm"}
        )
    else:
        audio_path = f"{LOCAL_STORAGE_PATH}/{call_id}/audio.webm"
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio not found")
        return FileResponse(audio_path, media_type="audio/webm", filename=f"call_{call_id}.webm")

@app.websocket("/ws/{call_id}")
async def ws_proxy(ws: WebSocket, call_id: str):
    await ws.accept()

    # Inicializar buffers para esta sesión (solo para transcript, no audio)
    transcript_parts = []
    session_start = datetime.now()

    # Registrar sesión activa
    active_sessions[call_id] = {
        "start_time": session_start,
        "transcript_parts": transcript_parts,
        "audio_size": 0,  # Ya no acumulamos audio aquí
        "coach_enabled": True  # Estado inicial del coach
    }

    # Configurar límite de sesión (90 minutos)
    session_timeout_task = asyncio.create_task(session_timeout_handler(ws, call_id, 90 * 60))

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

    async def handle_control_messages():
        """Maneja mensajes de control del frontend (texto)"""
        try:
            while True:
                try:
                    # Intentar recibir mensaje de texto con timeout corto
                    message = await asyncio.wait_for(ws.receive_text(), timeout=0.1)
                    data = json.loads(message)

                    # Manejar mensaje de toggle del coach
                    if data.get("type") == "coach_toggle":
                        enabled = data.get("enabled", True)
                        if call_id in active_sessions:
                            active_sessions[call_id]["coach_enabled"] = enabled
                            print(f"Coach {'enabled' if enabled else 'disabled'} for session {call_id}")

                except asyncio.TimeoutError:
                    # No hay mensajes de texto, continuar
                    continue
                except (json.JSONDecodeError, KeyError):
                    # Mensaje no válido, ignorar
                    continue

        except WebSocketDisconnect:
            pass

    async def upstream():
        try:
            while True:
                data = await ws.receive_bytes()    # Opus/webm chunks

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

                    # Analizar texto: detectar objeción + sugerencias (solo si coach está habilitado)
                    if call_id in active_sessions and active_sessions[call_id].get("coach_enabled", True):
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
        await asyncio.gather(upstream(), downstream(), handle_control_messages())
    finally:
        # Cancelar tarea de timeout si aún está corriendo
        if 'session_timeout_task' in locals():
            session_timeout_task.cancel()
            try:
                await session_timeout_task
            except asyncio.CancelledError:
                pass

        # Guardar archivos al finalizar la sesión
        try:
            # Guardar transcript
            transcript_content = "\n".join(transcript_parts)
            if transcript_content:
                save_to_storage(call_id, "transcript.txt", transcript_content.encode('utf-8'), "text/plain")

            # Nota: El audio se guarda vía POST /upload-final cuando el frontend lo envía
            # No guardamos audio automáticamente aquí para evitar problemas con WebM

            # Limpiar sesión activa
            if call_id in active_sessions:
                del active_sessions[call_id]

        except Exception as e:
            print(f"Error guardando archivos para {call_id}: {e}")
