"""
Servicio de exportación de transcripciones.
Genera archivos TXT y JSON con el contenido completo de las llamadas.
"""

import json
import os
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from domain.entities import Call, Segment, CallSummary
from domain.models import Objection, Suggestion


class TranscriptExporter:
    """Servicio para exportar transcripciones en diferentes formatos"""

    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_txt(self, call: Call) -> str:
        """Guardar transcripción en formato TXT legible"""
        call_dir = self.output_dir / call.call_id
        call_dir.mkdir(exist_ok=True)

        txt_path = call_dir / "transcript.txt"

        with open(txt_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 60 + "\n")
            f.write(f"TRANSCRIPCIÓN DE LLAMADA\n")
            f.write(f"Call ID: {call.call_id}\n")
            f.write(f"Fecha: {call.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if call.end_time:
                duration = (call.end_time - call.start_time).total_seconds()
                f.write(f"Duración: {duration:.1f} segundos\n")
            f.write("=" * 60 + "\n\n")

            # Contenido
            for segment in sorted(call.segments, key=lambda s: s.ts_ms):
                speaker_name = "Tú" if segment.speaker == 0 else "Prospecto"
                timestamp = f"[{segment.ts_ms//1000:02d}:{(segment.ts_ms%1000)//100:01d}s]"

                f.write(f"{timestamp} {speaker_name}: {segment.text}\n")

                # Agregar info de objeción si existe
                if segment.objection_type:
                    f.write(f"      [OBJECIÓN: {segment.objection_type.upper()}]")
                    if segment.suggestion_text:
                        f.write(f" Sugerencia: {segment.suggestion_text}")
                    f.write("\n")

                f.write("\n")

            # Footer con resumen
            if call.summary:
                f.write("\n" + "=" * 60 + "\n")
                f.write("RESUMEN DE LA LLAMADA\n")
                f.write("=" * 60 + "\n")
                f.write(f"Total de segmentos: {call.summary.total_segments}\n")
                f.write(f"Total de objeciones: {call.summary.total_objections}\n")

                if call.summary.objection_types:
                    f.write("Tipos de objeciones:\n")
                    for obj_type, count in call.summary.objection_types.items():
                        f.write(f"  - {obj_type}: {count}\n")

                if call.summary.top_topics:
                    f.write("Temas principales:\n")
                    for topic in call.summary.top_topics:
                        f.write(f"  - {topic}\n")

                if call.summary.next_steps:
                    f.write("Próximos pasos recomendados:\n")
                    for step in call.summary.next_steps:
                        f.write(f"  - {step}\n")

        return str(txt_path)

    def save_json(self, call: Call) -> str:
        """Guardar transcripción completa en formato JSON estructurado"""
        call_dir = self.output_dir / call.call_id
        call_dir.mkdir(exist_ok=True)

        json_path = call_dir / "transcript.json"

        # Estructura completa de datos
        data = {
            "call_metadata": {
                "call_id": call.call_id,
                "start_time": call.start_time.isoformat(),
                "end_time": call.end_time.isoformat() if call.end_time else None,
                "duration_ms": call.duration_ms,
                "exported_at": datetime.now().isoformat()
            },
            "segments": [
                {
                    "speaker": segment.speaker,
                    "speaker_name": "Tú" if segment.speaker == 0 else "Prospecto",
                    "ts_ms": segment.ts_ms,
                    "text": segment.text,
                    "confidence": segment.confidence,
                    "is_final": segment.is_final,
                    "timestamp": segment.timestamp.isoformat(),
                    "objection_type": segment.objection_type,
                    "suggestion_text": segment.suggestion_text
                }
                for segment in sorted(call.segments, key=lambda s: s.ts_ms)
            ],
            "objections": [
                {
                    "call_id": objection.call_id,
                    "ts_ms": objection.ts_ms,
                    "speaker": objection.speaker,
                    "type": objection.type,
                    "text": objection.text,
                    "confidence": objection.confidence
                }
                for objection in call.objections
            ] if call.objections else [],
            "suggestions": [
                {
                    "call_id": suggestion.call_id,
                    "ts_ms": suggestion.ts_ms,
                    "type": suggestion.type,
                    "text": suggestion.text,
                    "source": suggestion.source,
                    "meta": suggestion.meta
                }
                for suggestion in call.suggestions
            ] if call.suggestions else [],
            "summary": {
                "total_segments": call.summary.total_segments if call.summary else 0,
                "total_objections": call.summary.total_objections if call.summary else 0,
                "objection_types": call.summary.objection_types if call.summary else {},
                "speakers_time": call.summary.speakers_time if call.summary else {},
                "top_topics": call.summary.top_topics if call.summary else [],
                "next_steps": call.summary.next_steps if call.summary else [],
                "confidence_score": call.summary.confidence_score if call.summary else 0.0
            } if call.summary else None
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(json_path)

    def export_call(self, call: Call, formats: List[str] = None) -> Dict[str, str]:
        """Exportar llamada en múltiples formatos"""
        if formats is None:
            formats = ["txt", "json"]

        exported_files = {}

        if "txt" in formats:
            exported_files["txt"] = self.save_txt(call)

        if "json" in formats:
            exported_files["json"] = self.save_json(call)

        return exported_files

    def get_call_exports(self, call_id: str) -> List[str]:
        """Obtener lista de archivos exportados para una llamada"""
        call_dir = self.output_dir / call_id
        if not call_dir.exists():
            return []

        return [str(f) for f in call_dir.glob("*") if f.is_file()]
