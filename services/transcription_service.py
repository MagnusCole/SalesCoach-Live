"""
Servicio principal de transcripción.
Orquesta todos los componentes del sistema.
"""

import asyncio
import sys
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from config import config
from core import (
    AudioProcessor,
    DeepgramTranscriptionClient,
    DeviceManager,
    DeviceSelector
)
from domain import (
    AudioDevice,
    TranscriptionResult,
    SessionStats,
    Objection,
    Suggestion
)
from services.objection_service import analyze_segment
from services.storage import StorageService
from services.transcript_exporter import TranscriptExporter
from services.call_analyzer import CallAnalyzer
from domain.entities import Call, Segment, CallSummary


class TranscriptionService:
    """Servicio principal que orquesta la transcripción completa"""

    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.transcription_client = DeepgramTranscriptionClient()
        self.device_selector = DeviceSelector()

        # Servicios de persistencia
        self.storage = StorageService()
        self.exporter = TranscriptExporter()
        self.analyzer = CallAnalyzer()

        self._mic_device: Optional[AudioDevice] = None
        self._speaker_device: Optional[AudioDevice] = None
        self._loop_device: Optional[AudioDevice] = None

        self._running = False
        self._stats = SessionStats(start_time=datetime.now())

        # Datos de la llamada actual
        self._current_call: Optional[Call] = None
        self._call_segments: List[Segment] = []
        self._call_objections: List[Objection] = []
        self._call_suggestions: List[Suggestion] = []

        # Sistema de eventos simple
        self._event_callbacks: Dict[str, List[Callable]] = {
            "transcript_update": [],
            "objection_detected": [],
            "suggestion_ready": [],
            "call_completed": []
        }

        # Registrar callbacks
        self._register_callbacks()

    def on_event(self, event_type: str, callback: Callable) -> None:
        """Registrar callback para eventos"""
        if event_type in self._event_callbacks:
            self._event_callbacks[event_type].append(callback)

    def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emitir evento a todos los callbacks registrados"""
        if event_type in self._event_callbacks:
            for callback in self._event_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    if config.log_debug:
                        print(f"Error in event callback {event_type}: {e}")

    async def initialize(self) -> bool:
        """
        Inicializar el servicio y seleccionar dispositivos.

        Returns:
            True si la inicialización fue exitosa
        """
        try:
            if config.log_events:
                print("🚀 Inicializando Deepgram NOVA 3 Transcription Service...")

            # Seleccionar dispositivos
            self._mic_device, self._speaker_device = self.device_selector.select_optimal_devices()

            if not self._mic_device or not self._speaker_device:
                if config.log_events:
                    print("❌ No se pudieron seleccionar dispositivos de audio")
                return False

            # Crear dispositivo de loopback
            self._loop_device = DeviceManager.create_loopback_device(self._speaker_device)

            if not self._loop_device:
                if config.log_events:
                    print("❌ No se pudo crear dispositivo de loopback")
                return False

            # Configurar procesador de audio
            self.audio_processor.set_devices(self._mic_device, self._loop_device)

            # Mostrar información de dispositivos
            if config.log_events:
                device_info = self.device_selector.get_device_info(self._mic_device, self._speaker_device)
                print(device_info)

                # Mostrar dispositivos disponibles si está en debug
                if config.log_debug:
                    DeviceManager.print_device_info()

            return True

        except Exception as e:
            if config.log_events:
                print(f"❌ Error durante inicialización: {e}")
            return False

    async def start_transcription(self) -> None:
        """Iniciar sesión de transcripción"""
        if self._running:
            return

        try:
            # Inicializar nueva llamada
            call_id = f"call_{int(datetime.now().timestamp())}"
            self._current_call = Call(
                call_id=call_id,
                start_time=datetime.now(),
                segments=[],
                objections=[],
                suggestions=[]
            )
            self._call_segments = []
            self._call_objections = []
            self._call_suggestions = []

            # Conectar a Deepgram
            if not await self.transcription_client.connect():
                raise RuntimeError("No se pudo conectar a Deepgram")

            # Iniciar captura de audio
            self._running = True
            self._stats.start_time = datetime.now()

            if config.log_events:
                layout_desc = "L=Mic/R=Loopback" if config.stereo_layout == "LR" else "L=Loopback/R=Mic"
                print(f"🎙️ {layout_desc}. Habla y reproduce algo. Ctrl+C para salir.")
                print(f"📞 Call ID: {call_id}")

            # Procesar audio en tiempo real
            async for frame in self.audio_processor.start_capture():
                if not self._running:
                    break

                # Actualizar estadísticas
                self._update_stats(frame)

                # Enviar frame si hay actividad de voz
                if frame.is_speech:
                    await self.transcription_client.send_audio(frame)
                    self._stats.frames_sent += 1
                else:
                    self._stats.frames_silence += 1

                # Logging periódico
                if self._stats.frames_sent % config.log_rms_interval == 0:
                    self._log_stats()

        except KeyboardInterrupt:
            if config.log_events:
                print("\n⏹️  Transcription interrupted by user")
        except Exception as e:
            if config.log_events:
                print(f"❌ Session error: {e}")
        finally:
            await self._cleanup()

    async def stop_transcription(self) -> None:
        """Detener sesión de transcripción"""
        self._running = False
        await self._cleanup()

    def _register_callbacks(self) -> None:
        """Registrar callbacks para eventos de transcripción"""

        @self.transcription_client.on_transcript
        def handle_transcript(result: TranscriptionResult):
            self._handle_transcript(result)

        @self.transcription_client.on_error
        def handle_error(error):
            self._handle_error(error)

        @self.transcription_client.on_metadata
        def handle_metadata(metadata):
            self._handle_metadata(metadata)

        @self.transcription_client.on_close
        def handle_close(close):
            self._handle_close(close)

    def _handle_transcript(self, result: TranscriptionResult) -> None:
        """Manejar resultado de transcripción"""
        self._stats.transcription_count += 1

        # Crear task async para análisis de objeciones
        asyncio.create_task(self._process_transcript(result))

    async def _process_transcript(self, result: TranscriptionResult) -> None:
        """Procesar resultado de transcripción (async para análisis de objeciones)"""
        # 1) Emitir transcript en vivo (para UI)
        transcript_data = {
            "call_id": getattr(result, 'call_id', 'default_call'),
            "speaker": result.channel_index,
            "ts_ms": int(result.timestamp.timestamp() * 1000) if result.timestamp else 0,
            "text": result.transcript,
            "is_final": result.is_final,
            "confidence": result.confidence
        }
        self._emit_event("transcript_update", transcript_data)

        if config.log_transcript:
            transcript_type = ""
            if config.deepgram_interim_results and not result.is_final:
                transcript_type = "[INTERIM] "
            elif result.is_final:
                transcript_type = "[FINAL] "

            speaker = "Micrófono" if result.channel_index == 0 else "Loopback"
            print(f"{transcript_type}[{speaker}] {result.transcript}")

        # 2) Agregar segmento a la llamada actual
        if self._current_call and result.is_final:
            from domain.entities import Segment
            segment = Segment(
                speaker=result.channel_index,
                text=result.transcript,
                timestamp=result.timestamp or datetime.now(),
                confidence=result.confidence,
                is_objection=False  # Se actualizará si se detecta objeción
            )
            self._call_segments.append(segment)

        # 3) Analizar SOLO al prospecto (convención: speaker == 1 para loopback/prospecto)
        if result.channel_index != 1:  # Solo procesar audio del prospecto
            return

        # 4) Detectar objeciones
        call_id = getattr(result, 'call_id', 'default_call')
        ts_ms = int(result.timestamp.timestamp() * 1000) if result.timestamp else 0

        objection_result = await analyze_segment(
            call_id=call_id,
            speaker=result.channel_index,
            text=result.transcript,
            ts_ms=ts_ms
        )

        if not objection_result.get("is_objection", False):
            return

        # 5) Marcar segmento como objeción si se detectó
        if self._current_call and self._call_segments:
            self._call_segments[-1].is_objection = True

        # 6) Agregar objeción a la llamada
        from domain.entities import Objection
        objection = Objection(
            type=objection_result["type"],
            text=result.transcript,
            timestamp=result.timestamp or datetime.now(),
            confidence=objection_result.get("confidence", 0.7),
            source=objection_result.get("source", "rule")
        )
        self._call_objections.append(objection)

        # 7) Publicar evento de objeción detectada
        objection_data = {
            "call_id": call_id,
            "speaker": result.channel_index,
            "ts_ms": ts_ms,
            "type": objection_result["type"],
            "text": result.transcript,
            "confidence": objection_result.get("confidence", 0.7),
            "source": objection_result.get("source", "rule")
        }
        self._emit_event("objection_detected", objection_data)

        # 8) Agregar sugerencia a la llamada
        from domain.entities import Suggestion
        suggestion = Suggestion(
            type=objection_result["type"],
            text=objection_result.get("suggestion", ""),
            timestamp=result.timestamp or datetime.now(),
            source=objection_result.get("source", "rule")
        )
        self._call_suggestions.append(suggestion)

        # 9) Publicar sugerencia de respuesta
        suggestion_data = {
            "call_id": call_id,
            "ts_ms": ts_ms,
            "type": objection_result["type"],
            "text": objection_result.get("suggestion", ""),
            "source": objection_result.get("source", "rule")
        }
        self._emit_event("suggestion_ready", suggestion_data)

    def _handle_error(self, error) -> None:
        """Manejar error de transcripción"""
        self._stats.error_count += 1
        if config.log_events:
            print(f"[DG error] {error}")

    def _handle_metadata(self, metadata) -> None:
        """Manejar metadata de transcripción"""
        if config.log_events:
            print(f"[DG metadata] {metadata}")

    def _handle_close(self, close) -> None:
        """Manejar cierre de conexión"""
        if config.log_events:
            print(f"[DG close] {close}")

    def _update_stats(self, frame) -> None:
        """Actualizar estadísticas con el frame actual"""
        self._stats.avg_rms_mic = 0.9 * self._stats.avg_rms_mic + 0.1 * frame.rms_levels[0]
        self._stats.avg_rms_loop = 0.9 * self._stats.avg_rms_loop + 0.1 * frame.rms_levels[1]

    def _log_stats(self) -> None:
        """Registrar estadísticas periódicas"""
        if config.log_events:
            total_frames = self._stats.frames_sent + self._stats.frames_silence
            silence_ratio = self._stats.frames_silence / total_frames if total_frames > 0 else 0
            print(f"📊 RMS: Mic={self._stats.avg_rms_mic:.4f}, Loop={self._stats.avg_rms_loop:.4f} | VAD: {self._stats.frames_sent}/{total_frames} ({silence_ratio:.1%} silence)")

    async def _cleanup(self) -> None:
        """Limpiar recursos y guardar datos de la llamada"""
        try:
            if self._current_call:
                # Finalizar la llamada
                self._current_call.end_time = datetime.now()
                self._current_call.duration = (self._current_call.end_time - self._current_call.start_time).total_seconds()

                # Agregar segmentos restantes
                for segment in self._call_segments:
                    self._current_call.segments.append(segment)

                # Agregar objeciones y sugerencias
                self._current_call.objections.extend(self._call_objections)
                self._current_call.suggestions.extend(self._call_suggestions)

                # Generar resumen automático
                if self.call_analyzer:
                    summary = await self.call_analyzer.analyze_call(self._current_call)
                    self._current_call.summary = summary

                # Guardar la llamada
                if self.storage_service:
                    await self.storage_service.save_call_data(self._current_call)

                    # Exportar transcripción si está configurado
                    if config.auto_export_transcript:
                        if self.transcript_exporter:
                            export_path = config.export_path or "exports"
                            await self.transcript_exporter.save_txt(
                                self._current_call,
                                f"{export_path}/{self._current_call.call_id}_transcript.txt"
                            )
                            await self.transcript_exporter.save_json(
                                self._current_call,
                                f"{export_path}/{self._current_call.call_id}_data.json"
                            )

                if config.log_events:
                    print(f"💾 Call data saved: {self._current_call.call_id}")
                    print(f"📊 Duration: {self._current_call.duration:.1f}s")
                    print(f"🎯 Objections detected: {len(self._current_call.objections)}")
                    if self._current_call.summary:
                        print(f"📝 Summary: {self._current_call.summary.overview[:100]}...")

            # Limpiar estado
            self._current_call = None
            self._call_segments = []
            self._call_objections = []
            self._call_suggestions = []

            # Limpiar recursos existentes
            await self.audio_processor.stop_capture()
            await self.transcription_client.disconnect()

            self._stats.end_time = datetime.now()

            if config.log_events and self._stats.frames_sent > 0:
                total_frames = self._stats.frames_sent + self._stats.frames_silence
                silence_ratio = self._stats.frames_silence / total_frames if total_frames > 0 else 0
                print(f"📈 Final Statistics: {self._stats.frames_sent} frames sent, {silence_ratio:.1%} silence, {self._stats.transcription_count} transcriptions")

        except Exception as e:
            if config.log_events:
                print(f"⚠️  Warning during cleanup: {e}")

    @property
    def is_running(self) -> bool:
        """Verificar si el servicio está ejecutándose"""
        return self._running

    @property
    def stats(self) -> SessionStats:
        """Obtener estadísticas de la sesión"""
        return self._stats
