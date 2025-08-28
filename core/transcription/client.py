"""
Cliente de Deepgram para transcripción en tiempo real.
Maneja conexión WebSocket y eventos de transcripción.
"""

import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from deepgram import DeepgramClient, DeepgramClientOptions, LiveOptions, LiveTranscriptionEvents

from config import config
from domain import TranscriptionResult, ConnectionStatus, AudioFrame
from domain.entities import TranscriptionService


class DeepgramTranscriptionClient(TranscriptionService):
    """Cliente de transcripción usando Deepgram NOVA 3"""

    def __init__(self):
        self.client: Optional[DeepgramClient] = None
        self.connection = None
        self._connected = False
        self._connection_status = ConnectionStatus(
            is_connected=False,
            url=config.dg_base_wss
        )

        # Callbacks
        self._transcript_callbacks: list[Callable] = []
        self._error_callbacks: list[Callable] = []
        self._metadata_callbacks: list[Callable] = []
        self._close_callbacks: list[Callable] = []

    async def connect(self) -> bool:
        """Conectar al servicio de Deepgram"""
        try:
            # Validar API key antes de intentar conectar
            if not config.deepgram_api_key or config.deepgram_api_key == "tu_api_key_aqui":
                if config.log_events:
                    print("❌ API key de Deepgram no configurada correctamente")
                    print("   Configure DEEPGRAM_API_KEY en el archivo .env")
                return False

            if config.log_events:
                print(f"🌐 Conectando a región: {config.dg_region} ({self._connection_status.url})")

            # Configurar cliente
            client_options = DeepgramClientOptions(
                options={"url": self._connection_status.url},
                verbose=config.log_debug
            )

            self.client = DeepgramClient(config.deepgram_api_key, client_options)
            self.connection = self.client.listen.websocket.v("1")

            # Configurar opciones de transcripción
            live_options = self._create_live_options()

            if config.log_events:
                print("🔧 Configuración LiveOptions:")
                self._print_live_options(live_options)
                print("Connecting…")

            # Conectar
            self.connection.start(live_options)

            # Registrar event handlers
            self._register_event_handlers()

            self._connected = True
            self._connection_status.is_connected = True
            self._connection_status.last_ping = datetime.now()

            if config.log_events:
                print("✅ Connected to Deepgram successfully!")
                print(f"🌐 SDK Version: v4.x (Optimized)")
                print("🚀 NOVA 3 Features: Active")
            return True

        except Exception as e:
            if config.log_events:
                print(f"❌ Failed to connect: {e}")
            self._connection_status.error_message = str(e)
            return False

    async def disconnect(self) -> None:
        """Desconectar del servicio"""
        try:
            if self.connection and self._connected:
                if config.log_events:
                    print("🔄 Finishing connection...")
                self.connection.finish()
                if config.log_events:
                    print("✅ Connection finished successfully")
        except Exception as e:
            if config.log_events:
                print(f"⚠️  Warning during connection cleanup: {e}")
        finally:
            self._connected = False
            self._connection_status.is_connected = False

    async def send_audio(self, frame: AudioFrame) -> None:
        """Enviar frame de audio para transcripción"""
        if self.connection and self._connected:
            try:
                self.connection.send(frame.data)
            except Exception as e:
                if config.log_events:
                    print(f"❌ Error sending audio frame: {e}")

    def on_transcript(self, callback: Callable) -> None:
        """Registrar callback para resultados de transcripción"""
        self._transcript_callbacks.append(callback)

    def on_error(self, callback: Callable) -> None:
        """Registrar callback para errores"""
        self._error_callbacks.append(callback)

    def on_metadata(self, callback: Callable) -> None:
        """Registrar callback para metadata"""
        self._metadata_callbacks.append(callback)

    def on_close(self, callback: Callable) -> None:
        """Registrar callback para cierre de conexión"""
        self._close_callbacks.append(callback)

    def _create_live_options(self) -> LiveOptions:
        """Crear opciones de transcripción para NOVA 3"""
        return LiveOptions(
            model=config.deepgram_model,
            language=config.deepgram_language,
            encoding=config.deepgram_encoding,
            sample_rate=config.deepgram_sample_rate,
            channels=2,  # Estéreo
            multichannel=config.deepgram_multichannel,
            smart_format=config.deepgram_smart_format,
            # NOVA 3 Features
            interim_results=config.deepgram_interim_results,
            endpointing=config.deepgram_endpointing,
            redact=config.deepgram_pii_redact,  # v4: usa 'redact' en lugar de 'pii_redaction'
            utterance_end_ms=config.deepgram_utterance_end_ms,
            vad_events=config.deepgram_vad_events,
            no_delay=config.deepgram_no_delay,
            numerals=config.deepgram_numerals,
            profanity_filter=config.deepgram_profanity_filter
        )

    def _print_live_options(self, options: LiveOptions) -> None:
        """Imprimir configuración de opciones de transcripción"""
        print(f"   Model: {config.deepgram_model}")
        print(f"   Language: {config.deepgram_language}")
        print(f"   Encoding: {config.deepgram_encoding}")
        print(f"   Sample Rate: {config.deepgram_sample_rate}")
        print(f"   Channels: 2")
        print(f"   Multichannel: {config.deepgram_multichannel}")
        print(f"   Diarize: False")  # Por ahora deshabilitado para stereo
        print(f"   Smart Format: {config.deepgram_smart_format}")
        print(f"   Interim Results: {config.deepgram_interim_results}")
        print(f"   Endpointing: {config.deepgram_endpointing}")
        print(f"   PII Redaction: {config.deepgram_pii_redact}")
        print(f"   Utterance End MS: {config.deepgram_utterance_end_ms}")
        print(f"   VAD Events: {config.deepgram_vad_events}")
        print(f"   No Delay: {config.deepgram_no_delay}")
        print(f"   Numerals: {config.deepgram_numerals}")
        print(f"   Profanity Filter: {config.deepgram_profanity_filter}")

    def _register_event_handlers(self) -> None:
        """Registrar manejadores de eventos"""
        # Evento de transcripción
        self.connection.on(LiveTranscriptionEvents.Transcript, self._handle_transcript)

        # Evento de error
        self.connection.on(LiveTranscriptionEvents.Error, self._handle_error)

        # Evento de metadata
        self.connection.on(LiveTranscriptionEvents.Metadata, self._handle_metadata)

        # Evento de cierre
        self.connection.on(LiveTranscriptionEvents.Close, self._handle_close)

        # Eventos VAD si están habilitados
        if config.deepgram_vad_events:
            try:
                self.connection.on(LiveTranscriptionEvents.SpeechStarted, self._handle_speech_started)
                self.connection.on(LiveTranscriptionEvents.UtteranceEnd, self._handle_utterance_end)
            except AttributeError:
                if config.log_debug:
                    print("⚠️  VAD events no disponibles en esta versión del SDK")

    def _handle_transcript(self, *args, **kwargs):
        """Manejar evento de transcripción"""
        try:
            # Extraer el resultado de transcript de kwargs o args
            result = kwargs.get('result') or (args[0] if args else None)
            msg = result
            alts = msg.channel.alternatives or []
            if alts and alts[0].transcript:
                # Crear resultado de transcripción
                transcript_result = TranscriptionResult(
                    transcript=alts[0].transcript,
                    confidence=getattr(alts[0], 'confidence', 0.5),
                    is_final=getattr(msg, 'is_final', True),
                    channel_index=getattr(msg.channel, 'index', 0) if hasattr(msg, 'channel') else 0,
                    timestamp=datetime.now()
                )

                # Notificar callbacks
                for callback in self._transcript_callbacks:
                    try:
                        callback(transcript_result)
                    except Exception as e:
                        if config.log_debug:
                            print(f"Error in transcript callback: {e}")

        except Exception as e:
            if config.log_events:
                print(f"Error processing transcript: {e}")

    def _handle_error(self, error, *args, **kwargs):
        """Manejar evento de error"""
        self._connection_status.error_message = str(error)
        for callback in self._error_callbacks:
            try:
                callback(error)
            except Exception as e:
                if config.log_debug:
                    print(f"Error in error callback: {e}")

    def _handle_metadata(self, *args, **kwargs):
        """Manejar evento de metadata"""
        # Extraer el metadata de kwargs o args
        metadata = kwargs.get('metadata') or (args[0] if args else None)
        for callback in self._metadata_callbacks:
            try:
                callback(metadata)
            except Exception as e:
                if config.log_debug:
                    print(f"Error in metadata callback: {e}")

    def _handle_close(self, close, *args, **kwargs):
        """Manejar evento de cierre"""
        self._connected = False
        self._connection_status.is_connected = False
        for callback in self._close_callbacks:
            try:
                callback(close)
            except Exception as e:
                if config.log_debug:
                    print(f"Error in close callback: {e}")

    def _handle_speech_started(self, *args, **kwargs):
        """Manejar evento de inicio de habla"""
        # Extraer el resultado de speech_started de kwargs o args
        speech_result = kwargs.get('speech_started') or (args[0] if args else None)
        if config.log_events and config.deepgram_vad_events:
            print(f"[🎤 VAD] Speech started: {speech_result}")

    def _handle_utterance_end(self, *args, **kwargs):
        """Manejar evento de fin de enunciado"""
        # Extraer el resultado de utterance_end de kwargs o args
        utterance_result = kwargs.get('utterance_end') or (args[0] if args else None)
        if config.log_events and config.deepgram_vad_events:
            print(f"[🎤 VAD] Utterance end: {utterance_result}")

    @property
    def connection_status(self) -> ConnectionStatus:
        """Estado de la conexión"""
        return self._connection_status
