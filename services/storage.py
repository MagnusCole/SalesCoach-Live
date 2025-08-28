"""
Servicio de almacenamiento para persistencia de llamadas.
Abstracción que permite cambiar entre disco local, S3, GCS, etc.
"""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, BinaryIO
from pathlib import Path
from datetime import datetime

from domain.entities import Call, Segment, CallSummary
from domain.models import Objection, Suggestion


class StorageBackend(ABC):
    """Interfaz abstracta para backends de almacenamiento"""

    @abstractmethod
    async def save_file(self, path: str, content: bytes) -> str:
        """Guardar archivo y retornar URL/path"""
        pass

    @abstractmethod
    async def get_file(self, path: str) -> Optional[bytes]:
        """Obtener contenido de archivo"""
        pass

    @abstractmethod
    async def list_files(self, prefix: str) -> List[str]:
        """Listar archivos con prefijo"""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Eliminar archivo"""
        pass


class LocalStorageBackend(StorageBackend):
    """Backend de almacenamiento local en disco"""

    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)

    async def save_file(self, path: str, content: bytes) -> str:
        """Guardar archivo localmente"""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'wb') as f:
            f.write(content)

        return str(full_path)

    async def get_file(self, path: str) -> Optional[bytes]:
        """Obtener archivo local"""
        full_path = self.base_path / path
        if not full_path.exists():
            return None

        with open(full_path, 'rb') as f:
            return f.read()

    async def list_files(self, prefix: str) -> List[str]:
        """Listar archivos con prefijo"""
        search_path = self.base_path / prefix
        if not search_path.exists():
            return []

        files = []
        for file_path in search_path.rglob('*'):
            if file_path.is_file():
                files.append(str(file_path.relative_to(self.base_path)))

        return files

    async def delete_file(self, path: str) -> bool:
        """Eliminar archivo local"""
        full_path = self.base_path / path
        if not full_path.exists():
            return False

        full_path.unlink()
        return True


class StorageService:
    """Servicio principal de almacenamiento"""

    def __init__(self, backend: Optional[StorageBackend] = None):
        self.backend = backend or LocalStorageBackend()

    async def save_call_data(self, call: Call) -> Dict[str, str]:
        """Guardar todos los datos de una llamada"""
        call_id = call.call_id
        base_path = f"calls/{call_id}"

        saved_paths = {}

        # Guardar segmentos como JSON
        segments_data = {
            "call_id": call.call_id,
            "segments": [
                {
                    "speaker": s.speaker,
                    "ts_ms": s.ts_ms,
                    "text": s.text,
                    "confidence": s.confidence,
                    "is_final": s.is_final,
                    "timestamp": s.timestamp.isoformat(),
                    "objection_type": s.objection_type,
                    "suggestion_text": s.suggestion_text
                }
                for s in call.segments
            ]
        }

        segments_json = json.dumps(segments_data, ensure_ascii=False, indent=2)
        saved_paths["segments_json"] = await self.backend.save_file(
            f"{base_path}/segments.json",
            segments_json.encode('utf-8')
        )

        # Guardar objeciones
        if call.objections:
            objections_data = {
                "call_id": call.call_id,
                "objections": [
                    {
                        "call_id": o.call_id,
                        "ts_ms": o.ts_ms,
                        "speaker": o.speaker,
                        "type": o.type,
                        "text": o.text,
                        "confidence": o.confidence
                    }
                    for o in call.objections
                ]
            }

            objections_json = json.dumps(objections_data, ensure_ascii=False, indent=2)
            saved_paths["objections_json"] = await self.backend.save_file(
                f"{base_path}/objections.json",
                objections_json.encode('utf-8')
            )

        # Guardar sugerencias
        if call.suggestions:
            suggestions_data = {
                "call_id": call.call_id,
                "suggestions": [
                    {
                        "call_id": s.call_id,
                        "ts_ms": s.ts_ms,
                        "type": s.type,
                        "text": s.text,
                        "source": s.source,
                        "meta": s.meta
                    }
                    for s in call.suggestions
                ]
            }

            suggestions_json = json.dumps(suggestions_data, ensure_ascii=False, indent=2)
            saved_paths["suggestions_json"] = await self.backend.save_file(
                f"{base_path}/suggestions.json",
                suggestions_json.encode('utf-8')
            )

        # Guardar resumen si existe
        if call.summary:
            summary_data = {
                "call_id": call.summary.call_id,
                "total_segments": call.summary.total_segments,
                "total_objections": call.summary.total_objections,
                "objection_types": call.summary.objection_types,
                "speakers_time": call.summary.speakers_time,
                "top_topics": call.summary.top_topics,
                "next_steps": call.summary.next_steps,
                "generated_at": call.summary.generated_at.isoformat(),
                "confidence_score": call.summary.confidence_score
            }

            summary_json = json.dumps(summary_data, ensure_ascii=False, indent=2)
            saved_paths["summary_json"] = await self.backend.save_file(
                f"{base_path}/summary.json",
                summary_json.encode('utf-8')
            )

        return saved_paths

    async def get_call(self, call_id: str) -> Optional[Call]:
        """Obtener una llamada completa por ID"""
        base_path = f"calls/{call_id}"

        # Obtener segmentos
        segments_data = await self.backend.get_file(f"{base_path}/segments.json")
        if not segments_data:
            return None

        segments_json = json.loads(segments_data.decode('utf-8'))
        segments = []
        for s_data in segments_json["segments"]:
            segments.append(Segment(
                call_id=s_data["call_id"],
                speaker=s_data["speaker"],
                ts_ms=s_data["ts_ms"],
                text=s_data["text"],
                confidence=s_data["confidence"],
                is_final=s_data["is_final"],
                timestamp=datetime.fromisoformat(s_data["timestamp"]),
                objection_type=s_data.get("objection_type"),
                suggestion_text=s_data.get("suggestion_text")
            ))

        call = Call(
            call_id=call_id,
            start_time=segments[0].timestamp if segments else datetime.now(),
            segments=segments
        )

        # Obtener objeciones si existen
        objections_data = await self.backend.get_file(f"{base_path}/objections.json")
        if objections_data:
            objections_json = json.loads(objections_data.decode('utf-8'))
            call.objections = [
                Objection(**o_data) for o_data in objections_json["objections"]
            ]

        # Obtener sugerencias si existen
        suggestions_data = await self.backend.get_file(f"{base_path}/suggestions.json")
        if suggestions_data:
            suggestions_json = json.loads(suggestions_data.decode('utf-8'))
            call.suggestions = [
                Suggestion(**s_data) for s_data in suggestions_json["suggestions"]
            ]

        return call

    async def list_calls(self) -> List[str]:
        """Listar todas las llamadas disponibles"""
        files = await self.backend.list_files("calls")
        call_ids = set()

        for file_path in files:
            # Extraer call_id del path (calls/{call_id}/...)
            parts = file_path.split("/")
            if len(parts) >= 2:
                call_ids.add(parts[1])

        return sorted(list(call_ids))

    async def save_audio_file(self, call_id: str, audio_type: str, audio_data: bytes) -> str:
        """Guardar archivo de audio"""
        path = f"calls/{call_id}/audio_{audio_type}.wav"
        return await self.backend.save_file(path, audio_data)

    async def get_audio_file(self, call_id: str, audio_type: str) -> Optional[bytes]:
        """Obtener archivo de audio"""
        path = f"calls/{call_id}/audio_{audio_type}.wav"
        return await self.backend.get_file(path)
