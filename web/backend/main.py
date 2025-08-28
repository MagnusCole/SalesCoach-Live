"""
Backend web para el sistema de coaching de ventas en tiempo real
FastAPI con WebSocket para interfaz web en tiempo real
"""

import asyncio
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Importar servicios del sistema existente
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import config
from services.transcription_service import TranscriptionService
from services.storage import StorageService
from services.transcript_exporter import TranscriptExporter
from domain.entities import Call

app = FastAPI(
    title="Sales Coach Live API",
    description="API para sistema de coaching de ventas en tiempo real",
    version="1.0.0"
)

# Configurar CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class SessionStartRequest(BaseModel):
    """Solicitud para iniciar una sesión"""
    pass

class SessionStartResponse(BaseModel):
    """Respuesta al iniciar una sesión"""
    call_id: str
    ws_url: str
    status: str

class WebSocketMessage(BaseModel):
    """Mensaje WebSocket"""
    type: str
    data: Dict

# Servicios globales
transcription_service: Optional[TranscriptionService] = None
storage_service: Optional[StorageService] = None
transcript_exporter: Optional[TranscriptExporter] = None

# Conexiones WebSocket activas
active_connections: Dict[str, WebSocket] = {}

@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al iniciar la aplicación"""
    global transcription_service, storage_service, transcript_exporter

    print("🚀 Inicializando servicios del backend web...")

    try:
        # Inicializar servicios (similar a sales_coaching_system.py)
        transcription_service = TranscriptionService()
        storage_service = StorageService()
        transcript_exporter = TranscriptExporter()

        print("✅ Servicios inicializados correctamente")

        # Configurar eventos del servicio de transcripción
        setup_transcription_events()

    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar la aplicación"""
    global transcription_service

    if transcription_service:
        await transcription_service.stop_transcription()

def setup_transcription_events():
    """Configurar el sistema de eventos para WebSocket"""

    def handle_transcript_update(data):
        """Manejar actualización de transcripción"""
        asyncio.create_task(broadcast_to_call(data.get("call_id"), "transcript_update", data))

    def handle_objection_detected(data):
        """Manejar objeción detectada"""
        asyncio.create_task(broadcast_to_call(data.get("call_id"), "objection_detected", data))

    def handle_suggestion_ready(data):
        """Manejar sugerencia lista"""
        asyncio.create_task(broadcast_to_call(data.get("call_id"), "suggestion_ready", data))

    def handle_call_completed(data):
        """Manejar llamada completada"""
        asyncio.create_task(broadcast_to_call(data.get("call_id"), "call_completed", data))

    # Registrar handlers de eventos
    if transcription_service:
        transcription_service.on_event("transcript_update", handle_transcript_update)
        transcription_service.on_event("objection_detected", handle_objection_detected)
        transcription_service.on_event("suggestion_ready", handle_suggestion_ready)
        transcription_service.on_event("call_completed", handle_call_completed)

async def broadcast_to_call(call_id: str, event_type: str, data: Dict):
    """Enviar mensaje a todas las conexiones WebSocket de una llamada"""
    if call_id in active_connections:
        message = WebSocketMessage(type=event_type, data=data)
        try:
            await active_connections[call_id].send_json(message.dict())
        except Exception as e:
            print(f"⚠️ Error enviando mensaje WebSocket: {e}")

@app.post("/session/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    """Iniciar una nueva sesión de coaching"""
    try:
        # Generar ID único para la llamada
        call_id = f"web_{uuid.uuid4().hex[:8]}"

        # Crear URL WebSocket firmada
        ws_url = f"ws://localhost:8000/ws/{call_id}"

        # Inicializar nueva llamada en el servicio de transcripción
        if transcription_service:
            # Aquí podríamos pasar el call_id al servicio si es necesario
            pass

        return SessionStartResponse(
            call_id=call_id,
            ws_url=ws_url,
            status="started"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")

@app.websocket("/ws/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """Endpoint WebSocket para comunicación en tiempo real"""
    await websocket.accept()

    # Registrar conexión
    active_connections[call_id] = websocket

    try:
        # Enviar mensaje de bienvenida
        welcome_message = WebSocketMessage(
            type="session_started",
            data={
                "call_id": call_id,
                "message": "Conectado al sistema de coaching",
                "timestamp": datetime.now().isoformat()
            }
        )
        await websocket.send_json(welcome_message.dict())

        # Mantener conexión abierta y escuchar mensajes del cliente
        while True:
            try:
                # Recibir mensaje del cliente (con timeout)
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)

                # Procesar mensaje del cliente
                await handle_client_message(call_id, data, websocket)

            except asyncio.TimeoutError:
                # Enviar ping para mantener conexión viva
                ping_message = WebSocketMessage(
                    type="ping",
                    data={"timestamp": datetime.now().isoformat()}
                )
                await websocket.send_json(ping_message.dict())

    except WebSocketDisconnect:
        print(f"📡 WebSocket desconectado para call_id: {call_id}")
    except Exception as e:
        print(f"❌ Error en WebSocket: {e}")
    finally:
        # Limpiar conexión
        if call_id in active_connections:
            del active_connections[call_id]

async def handle_client_message(call_id: str, data: Dict, websocket: WebSocket):
    """Manejar mensajes del cliente"""
    message_type = data.get("type", "")

    if message_type == "start_transcription":
        if transcription_service:
            await transcription_service.start_transcription()

    elif message_type == "stop_transcription":
        if transcription_service:
            await transcription_service.stop_transcription()

    elif message_type == "toggle_coach":
        # Aquí podríamos implementar toggle del modo coach
        pass

    elif message_type == "ping":
        # Responder al ping del cliente
        pong_message = WebSocketMessage(
            type="pong",
            data={"timestamp": datetime.now().isoformat()}
        )
        await websocket.send_json(pong_message.dict())

@app.get("/calls/{call_id}/transcript.txt")
async def get_transcript_txt(call_id: str):
    """Obtener transcripción en formato TXT"""
    try:
        if not storage_service:
            raise HTTPException(status_code=500, detail="Storage service not available")

        # Obtener datos de la llamada
        call_data = await storage_service.get_call(call_id)
        if not call_data:
            raise HTTPException(status_code=404, detail="Call not found")

        # Generar archivo TXT
        if transcript_exporter:
            export_path = f"exports/{call_id}_transcript.txt"
            await transcript_exporter.save_txt(call_data, export_path)

            return FileResponse(
                path=export_path,
                filename=f"{call_id}_transcript.txt",
                media_type="text/plain"
            )
        else:
            raise HTTPException(status_code=500, detail="Transcript exporter not available")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating transcript: {str(e)}")

@app.get("/calls/{call_id}/transcript.json")
async def get_transcript_json(call_id: str):
    """Obtener transcripción en formato JSON"""
    try:
        if not storage_service:
            raise HTTPException(status_code=500, detail="Storage service not available")

        # Obtener datos de la llamada
        call_data = await storage_service.get_call(call_id)
        if not call_data:
            raise HTTPException(status_code=404, detail="Call not found")

        return call_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving transcript: {str(e)}")

@app.get("/calls/{call_id}/audio/{audio_type}.wav")
async def get_audio(call_id: str, audio_type: str):
    """Obtener archivo de audio (mix, mic, loop)"""
    try:
        if audio_type not in ["mix", "mic", "loop"]:
            raise HTTPException(status_code=400, detail="Invalid audio type")

        if not storage_service:
            raise HTTPException(status_code=500, detail="Storage service not available")

        # Obtener archivo de audio
        audio_path = f"data/calls/{call_id}_{audio_type}.wav"
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")

        return FileResponse(
            path=audio_path,
            filename=f"{call_id}_{audio_type}.wav",
            media_type="audio/wav"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audio: {str(e)}")

@app.get("/calls")
async def list_calls():
    """Listar todas las llamadas disponibles"""
    try:
        if not storage_service:
            raise HTTPException(status_code=500, detail="Storage service not available")

        # Obtener lista de llamadas (esto necesitaría ser implementado en StorageService)
        calls = []  # Placeholder
        return {"calls": calls}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing calls: {str(e)}")

@app.get("/")
async def root():
    """Página de inicio con información del API"""
    return {
        "message": "Sales Coach Live API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/{call_id}"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
