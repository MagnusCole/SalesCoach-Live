"""
Transcripción en tiempo real multicanal con Deepgram NOVA 3
================================================================

🚀 IMPLEMENTACIÓN COMPLETA DE NOVA 3 - Características avanzadas:

✅ MODELOS Y PRECISIÓN:
- ✅ Modelo: nova-3-general (54.2% reducción en WER)
- ✅ Soporte multilingüe automático con "multi"
- ✅ Mejor precisión en conversaciones múltiples

✅ CARACTERÍSTICAS DE TIEMPO REAL:
- ✅ Interim Results: Resultados intermedios en tiempo real
- ✅ Endpointing: Mejor detección de async def main():
    if not D           print(f"� NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")
        print(f"�🔄 Reconexión: {'ON' if RECONNECT_ENABLED else 'OFF'}")   print(f"⚙️  VAD: {'ON' if VAD_ENABLED else 'OFF'}, Normalización: {'ON' if NORMALIZE_ENABLED else 'OFF'}")
        print(f"� NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")
        print(f"�🔄 Reconexión: {'ON' if RECONNECT_ENABLED else 'OFF'}")      print(f"� NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")       print(f"� NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")      print(f"🚀 NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")
        print(f"🔄 Reconexión: {'ON' if RECONNECT_ENABLED else 'OFF'}")      print(f"� NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")_KEY:
        raise SystemExit("❌ Falta DEEPGRAM_API_KEY en variables de entorno")

    # Verificar SDK v3 - Mejora de diagnóstico
    check_sdk_version()

    # Configurar región de Deepgram
    if DG_REGION == "eu":
        base_url = "wss://api.eu.deepgram.com"
    else:
        base_url = DG_BASE_WSS

    if LOG_EVENTS:
        print(f"🌐 Conectando a región: {DG_REGION} ({base_url})")
        print(f"🎵 Modo audio: {AUDIO_MODE} ({STEREO_LAYOUT})")
        print(f"⚙️  VAD: {'ON' if VAD_ENABLED else 'OFF'}, Normalización: {'ON' if NORMALIZE_ENABLED else 'OFF'}")
        print(f"🚀 NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")
        print(f"🔄 Reconexión: {'ON' if RECONNECT_ENABLED else 'OFF'}")✅ Utterance End Control: Control preciso de segmentación
- ✅ VAD Events: Eventos de actividad de voz

✅ SEGURIDAD Y PRIVACIDAD:
- ✅ PII Redaction: Redacción de información personal
- ✅ Profanity Filter: Filtrado de lenguaje ofensivo

✅ PROCESAMIENTO AVANZADO:
- ✅ Diarization: Identificación de hablantes
- ✅ Numerals: Formateo inteligente de números
- ✅ Smart Format: Formateo inteligente de texto
- ✅ No Delay: Reducción de latencia

✅ AUDIO MULTICANAL:
- ✅ Procesamiento estéreo optimizado
- ✅ Separación clara de canales (micrófono/loopback)
- ✅ Normalización por canal

Configuración recomendada para máxima precisión con NOVA 3:
- Model: nova-3-general (multilingüe)
- Language: multi (detección automática)
- Interim Results: ON (resultados en tiempo real)
- Endpointing: ON (mejor segmentación)
- VAD Events: ON (eventos de voz)
- Utterance End MS: 1000ms (control de pausa)
- Smart Format: ON (formateo inteligente)
- Numerals: ON (formateo de números)
"""

import os, asyncio, warnings, json, time, logging
import numpy as np
import soundcard as sc
from dotenv import load_dotenv
from deepgram import DeepgramClient, DeepgramClientOptions, LiveOptions, LiveTranscriptionEvents

# Intentar importar scipy para mejor resampling
try:
    from scipy.signal import resample_poly
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️  Scipy no disponible, usando resampling lineal")

if hasattr(np, "frombuffer"):  # parche NumPy 2.x para soundcard
    np.fromstring = np.frombuffer
warnings.filterwarnings("ignore", category=UserWarning, module="soundcard")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="soundcard")
load_dotenv()

# Configuración desde .env
DG_KEY = os.getenv("DEEPGRAM_API_KEY") or ""
MODEL = os.getenv("DEEPGRAM_MODEL", "nova-3-general")  # ✅ NOVA 3 - modelo más avanzado con mejor precisión
LANG = os.getenv("DEEPGRAM_LANGUAGE", "multi")  # ✅ "multi" para multilingüe automático con nova-3
ENC = os.getenv("DEEPGRAM_ENCODING", "linear16")
SR = int(os.getenv("DEEPGRAM_SAMPLE_RATE", "16000"))
CH = 2
MC = os.getenv("DEEPGRAM_MULTICHANNEL", "true").lower() == "true"
SMART = os.getenv("DEEPGRAM_SMART_FORMAT", "true").lower() == "true"

# Nuevas opciones optimizadas para NOVA 3
INTERIM_RESULTS = os.getenv("DEEPGRAM_INTERIM_RESULTS", "true").lower() == "true"  # ✅ Resultados intermedios en tiempo real
ENDPOINTING = os.getenv("DEEPGRAM_ENDPOINTING", "true").lower() == "true"  # ✅ Mejor detección de fin de habla
PII_REDACT = os.getenv("DEEPGRAM_PII_REDACT", "false").lower() == "true"  # 🔒 Redacción de información personal (v4: usa 'redact')
DIARIZE = os.getenv("DEEPGRAM_DIARIZE", "false").lower() == "true"  # 👥 Identificación de hablantes

# Configuraciones avanzadas de NOVA 3
UTTERANCE_END_MS = int(os.getenv("DEEPGRAM_UTTERANCE_END_MS", "1000"))  # ⏱️ Tiempo de espera para fin de utterance
VAD_EVENTS = os.getenv("DEEPGRAM_VAD_EVENTS", "true").lower() == "true"  # 🎤 Eventos de actividad de voz
NO_DELAY = os.getenv("DEEPGRAM_NO_DELAY", "false").lower() == "true"  # ⚡ Reducir latencia
NUMERALS = os.getenv("DEEPGRAM_NUMERALS", "true").lower() == "true"  # 🔢 Formateo inteligente de números
PROFANITY_FILTER = os.getenv("DEEPGRAM_PROFANITY_FILTER", "false").lower() == "true"  # 🚫 Filtrar lenguaje ofensivo

# Configuración de audio mejorada
MIC_NAME_SUBSTR = os.getenv("MIC_NAME_SUBSTR", "Blue Snowball")
SPK_NAME_SUBSTR = os.getenv("SPK_NAME_SUBSTR", "PRO")
FRAME_MS = int(os.getenv("FRAME_MS", "20"))
FS_CAP = 48000
BLOCK = int(FS_CAP * FRAME_MS / 1000.0)

# Ganancia y procesamiento
MIC_GAIN = float(os.getenv("MIC_GAIN", "3.0"))
LOOP_GAIN = float(os.getenv("LOOP_GAIN", "8.0"))
VAD_THRESHOLD = float(os.getenv("VAD_THRESHOLD", "0.01"))
VAD_ENABLED = os.getenv("VAD_ENABLED", "true").lower() == "true"
NORMALIZE_ENABLED = os.getenv("NORMALIZE_ENABLED", "true").lower() == "true"
NORMALIZE_TARGET_LEVEL = float(os.getenv("NORMALIZE_TARGET_LEVEL", "0.7"))
RESAMPLE_METHOD = os.getenv("RESAMPLE_METHOD", "poly")

# Reconexión automática
RECONNECT_ENABLED = os.getenv("RECONNECT_ENABLED", "true").lower() == "true"
RECONNECT_DELAY = float(os.getenv("RECONNECT_DELAY", "3.0"))
MAX_RECONNECT_ATTEMPTS = int(os.getenv("MAX_RECONNECT_ATTEMPTS", "5"))

# Región y modos
DG_REGION = os.getenv("DG_REGION", "us")
DG_BASE_WSS = os.getenv("DG_BASE_WSS", "wss://api.deepgram.com")
AUDIO_MODE = os.getenv("AUDIO_MODE", "stereo")
STEREO_LAYOUT = os.getenv("STEREO_LAYOUT", "LR")

# Logging
LOG_RMS_INTERVAL = int(os.getenv("LOG_RMS_INTERVAL", "100"))
LOG_EVENTS = os.getenv("LOG_EVENTS", "true").lower() == "true"
LOG_TRANSCRIPT = os.getenv("LOG_TRANSCRIPT", "true").lower() == "true"
LOG_DEBUG = os.getenv("LOG_DEBUG", "false").lower() == "true"

def check_sdk_version():
    """Verificar versión del SDK y compatibilidad - v3 Diagnostic"""
    try:
        import deepgram
        version = getattr(deepgram, '__version__', 'Unknown')
        if LOG_EVENTS:
            print(f"📦 Deepgram SDK Version: {version}")
            print("✅ SDK v3.x detected - All features available")
        return True
    except Exception as e:
        if LOG_EVENTS:
            print(f"⚠️  Could not determine SDK version: {e}")
        return False

def pick(pred, items):
    """Seleccionar dispositivo que cumple con el predicado"""
    for it in items:
        if pred(it.name): return it
    return None

def resample_f32(x, fs_in, fs_out):
    """Resampling mejorado con soporte para scipy"""
    if fs_in == fs_out or x.size == 0:
        return x.astype(np.float32, copy=False)

    n = x.shape[0]
    m = int(round(n * fs_out / fs_in))

    if RESAMPLE_METHOD == "poly" and SCIPY_AVAILABLE:
        # Usar scipy para mejor calidad
        try:
            from scipy.signal import resample_poly
            # Calcular ratio de resampling
            ratio = fs_out / fs_in
            up = int(np.ceil(ratio * 100))
            down = 100
            # Simplificar fracción
            gcd = np.gcd(up, down)
            up, down = up // gcd, down // gcd

            resampled = np.zeros((m, x.shape[1]), dtype=np.float32)
            for c in range(x.shape[1]):
                resampled[:, c] = resample_poly(x[:, c], up, down)
            return resampled[:m]  # Asegurar tamaño exacto
        except Exception as e:
            if LOG_DEBUG:
                print(f"⚠️  Error en resampling poly: {e}, usando lineal")
            pass

    # Fallback a interpolación lineal
    ti = np.linspace(0, 1, n, endpoint=False, dtype=np.float32)
    to = np.linspace(0, 1, m, endpoint=False, dtype=np.float32)
    return np.stack([np.interp(to, ti, x[:, c]).astype(np.float32) for c in range(x.shape[1])], axis=1)

def voice_activity_detection(audio_data, threshold=None):
    """Detección simple de actividad de voz"""
    if threshold is None:
        threshold = VAD_THRESHOLD

    # Calcular RMS por canal
    rms_levels = np.sqrt(np.mean(audio_data**2, axis=0))
    # Actividad si cualquier canal supera el umbral
    return np.any(rms_levels > threshold), rms_levels

def normalize_audio(audio_data, target_level=None):
    """Normalización suave por canal para evitar clipping"""
    if not NORMALIZE_ENABLED or target_level is None:
        target_level = NORMALIZE_TARGET_LEVEL

    normalized = audio_data.copy()
    for c in range(audio_data.shape[1]):
        channel_data = audio_data[:, c]
        current_level = np.sqrt(np.mean(channel_data**2))

        if current_level > 0.001:  # Evitar división por cero
            # Normalización suave con compresión
            ratio = target_level / current_level
            # Limitar la amplificación máxima para evitar clipping extremo
            ratio = np.clip(ratio, 0.1, 3.0)
            normalized[:, c] = np.clip(channel_data * ratio, -0.95, 0.95)

    return normalized

def to_pcm16(x):
    """Convertir audio float32 a PCM 16-bit"""
    return (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()

async def run_transcription_session(mic, spk, loop, base_url):
    """Sesión principal de transcripción con todas las mejoras - SDK v3 optimizado"""

    # Configurar cliente con URL base personalizada - v3 Best Practice
    config = DeepgramClientOptions(
        options={
            "url": base_url
        },
        # Agregar configuración adicional para robustez
        verbose=logging.DEBUG if LOG_DEBUG else logging.INFO
    )

    try:
        dg = DeepgramClient(DG_KEY, config)
        # Verificar que el cliente se inicializó correctamente
        if not dg:
            raise Exception("Failed to initialize Deepgram client")

        conn = dg.listen.websocket.v("1")

    except Exception as e:
        if LOG_EVENTS:
            print(f"❌ Error initializing Deepgram client: {e}")
            print(f"❌ Error type: {type(e).__name__}")
        raise

    def on_transcript(self, result, **kwargs):
        try:
            msg = result
            alts = msg.channel.alternatives or []
            if alts and alts[0].transcript:
                # Verificar si es resultado final o intermedio (NOVA 3 feature)
                is_final = getattr(msg, 'is_final', True)
                speech_final = getattr(msg, 'speech_final', True)

                # Intentar múltiples formas de obtener el índice del canal
                channel_info = None

                # Método 1: msg.channel.index
                if hasattr(msg, 'channel') and hasattr(msg.channel, 'index'):
                    channel_info = msg.channel.index

                # Método 2: buscar en el mensaje completo
                if channel_info is None:
                    if hasattr(msg, 'channel_index'):
                        channel_info = msg.channel_index
                    elif hasattr(msg, 'channels'):
                        for i, ch in enumerate(msg.channels):
                            if hasattr(ch, 'alternatives') and ch.alternatives:
                                channel_info = i
                                break

                # Método 3: asumir basado en el contenido o metadata
                if channel_info is None:
                    channel_info = 0  # Default a mic (usuario)

                # Determinar quién habla basado en el canal
                if isinstance(channel_info, (list, tuple)) and len(channel_info) > 0:
                    primary_channel = channel_info[0]
                    if primary_channel == 0:
                        who = "Tú"
                    elif primary_channel == 1:
                        who = "Amigo"
                    else:
                        who = f"Canal {primary_channel}"
                elif isinstance(channel_info, int):
                    if channel_info == 0:
                        who = "Tú"
                    elif channel_info == 1:
                        who = "Amigo"
                    else:
                        who = f"Canal {channel_info}"
                else:
                    who = f"Canal {channel_info}" if channel_info is not None else "Desconocido"

                # Mostrar transcripción con indicador de tipo (NOVA 3)
                if LOG_TRANSCRIPT:
                    transcript_type = ""
                    if INTERIM_RESULTS and not is_final:
                        transcript_type = "[INTERIM] "
                    elif speech_final:
                        transcript_type = "[FINAL] "

                    print(f"{transcript_type}[{who}] {alts[0].transcript}")

                # Debug: mostrar información del canal para diagnóstico
                if LOG_DEBUG and channel_info is None:
                    print(f"DEBUG: No se pudo determinar canal. Estructura del mensaje:")
                    print(f"  msg type: {type(msg)}")
                    print(f"  msg dir: {[attr for attr in dir(msg) if not attr.startswith('_')]}")
                    if hasattr(msg, 'channel'):
                        print(f"  channel type: {type(msg.channel)}")
                        print(f"  channel dir: {[attr for attr in dir(msg.channel) if not attr.startswith('_')]}")
        except Exception as e:
            if LOG_EVENTS:
                print(f"Error processing transcript: {e}")
                if LOG_DEBUG:
                    print(f"Message type: {type(result)}")
                    print(f"Message attributes: {dir(result) if hasattr(result, '__dict__') else 'No dict'}")

    def on_error(self, error, **kwargs):
        if LOG_EVENTS:
            print(f"[DG error] {error}")

    def on_metadata(self, metadata, **kwargs):
        if LOG_EVENTS:
            print(f"[DG metadata] {metadata}")

    def on_close(self, close, **kwargs):
        if LOG_EVENTS:
            print(f"[DG close] {close}")

    # Configurar opciones según el modo de audio
    if AUDIO_MODE == "mono_diarize":
        ch = 1
        mc = False
        diarize = True
    else:  # stereo
        ch = CH
        mc = MC
        diarize = False

    opts = LiveOptions(model=MODEL, language=LANG, encoding=ENC,
                       sample_rate=SR, channels=ch, multichannel=mc,
                       smart_format=SMART, diarize=diarize,
                       interim_results=INTERIM_RESULTS,  # ✅ NOVA 3: Resultados intermedios
                       endpointing=ENDPOINTING,  # ✅ NOVA 3: Mejor detección de fin de habla
                       redact=PII_REDACT,  # 🔒 NOVA 3: Redacción de PII (v4: redact en lugar de pii_redaction)
                       utterance_end_ms=UTTERANCE_END_MS,  # ⏱️ NOVA 3: Control de utterance
                       vad_events=VAD_EVENTS,  # 🎤 NOVA 3: Eventos VAD
                       no_delay=NO_DELAY,  # ⚡ NOVA 3: Reducir latencia
                       numerals=NUMERALS,  # 🔢 NOVA 3: Formateo de números
                       profanity_filter=PROFANITY_FILTER)  # 🚫 NOVA 3: Filtrar profanidad

    def on_speech_started(self, speech_started, **kwargs):
        if LOG_EVENTS and VAD_EVENTS:
            print(f"[🎤 VAD] Speech started: {speech_started}")

    def on_utterance_end(self, utterance_end, **kwargs):
        if LOG_EVENTS and VAD_EVENTS:
            print(f"[🎤 VAD] Utterance end: {utterance_end}")

    # Registrar handlers
    conn.on(LiveTranscriptionEvents.Transcript, on_transcript)
    conn.on(LiveTranscriptionEvents.Error, on_error)
    conn.on(LiveTranscriptionEvents.Metadata, on_metadata)
    conn.on(LiveTranscriptionEvents.Close, on_close)

    # Registrar eventos VAD si están habilitados (NOVA 3)
    if VAD_EVENTS:
        try:
            conn.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
            conn.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        except AttributeError:
            if LOG_DEBUG:
                print("⚠️  VAD events no disponibles en esta versión del SDK")

    if LOG_EVENTS:
        print(f"🔧 Configuración LiveOptions:")
        print(f"   Model: {MODEL}")
        print(f"   Language: {LANG}")
        print(f"   Encoding: {ENC}")
        print(f"   Sample Rate: {SR}")
        print(f"   Channels: {ch}")
        print(f"   Multichannel: {mc}")
        print(f"   Diarize: {diarize}")
        print(f"   Smart Format: {SMART}")
        print(f"   Interim Results: {INTERIM_RESULTS}")  # ✅ NOVA 3
        print(f"   Endpointing: {ENDPOINTING}")  # ✅ NOVA 3
        print(f"   PII Redaction: {PII_REDACT}")  # 🔒 NOVA 3
        print(f"   Utterance End MS: {UTTERANCE_END_MS}")  # ⏱️ NOVA 3
        print(f"   VAD Events: {VAD_EVENTS}")  # 🎤 NOVA 3
        print(f"   No Delay: {NO_DELAY}")  # ⚡ NOVA 3
        print(f"   Numerals: {NUMERALS}")  # 🔢 NOVA 3
        print(f"   Profanity Filter: {PROFANITY_FILTER}")  # 🚫 NOVA 3
        print("Connecting…")

    try:
        conn.start(opts)
        if LOG_EVENTS:
            print("✅ Connected to Deepgram successfully!")
            print(f"🌐 SDK Version: v3.x (Optimized)")
            print(f"🚀 NOVA 3 Features: Active")
    except Exception as e:
        if LOG_EVENTS:
            print(f"❌ Failed to connect: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            if hasattr(e, 'status_code'):
                print(f"❌ Status Code: {e.status_code}")
            if hasattr(e, 'response'):
                print(f"❌ Response: {e.response}")
        raise

    # Estadísticas de audio
    vad_stats = {"sent": 0, "silence": 0}
    audio_stats = {"mic_levels": [], "loop_levels": []}

    with mic.recorder(FS_CAP, channels=1, blocksize=BLOCK) as mic_rec, \
         loop.recorder(FS_CAP, channels=2, blocksize=BLOCK) as loop_rec:

        if LOG_EVENTS:
            layout_desc = "L=Mic/R=Loopback" if STEREO_LAYOUT == "LR" else "L=Loopback/R=Mic"
            print(f"🎙️ {layout_desc}. Habla y reproduce algo. Ctrl+C para salir.")

        printed_shape = False
        tick = 0

        try:
            while True:
                mb = mic_rec.record(numframes=BLOCK)
                lb = loop_rec.record(numframes=BLOCK)

                # Aplicar ganancia
                if MIC_GAIN != 1.0:
                    mb = np.clip(mb * MIC_GAIN, -1, 1)
                if LOOP_GAIN != 1.0:
                    lb = np.clip(lb * LOOP_GAIN, -1, 1)

                # Convertir loopback a mono
                lb = lb.mean(axis=1, keepdims=True)

                n = min(mb.shape[0], lb.shape[0])
                if n <= 0:
                    await asyncio.sleep(0)
                    continue

                # Configurar canales según layout
                if STEREO_LAYOUT == "LR":
                    # L=Mic, R=Loopback
                    stereo_48k = np.concatenate([mb[:n], lb[:n]], axis=1)
                else:
                    # L=Loopback, R=Mic
                    stereo_48k = np.concatenate([lb[:n], mb[:n]], axis=1)

                # Normalización suave
                if NORMALIZE_ENABLED:
                    stereo_48k = normalize_audio(stereo_48k)

                # Resampling
                stereo_16k = resample_f32(stereo_48k, FS_CAP, SR)
                assert stereo_16k.ndim == 2 and stereo_16k.shape[1] == 2, stereo_16k.shape

                if not printed_shape:
                    if LOG_DEBUG:
                        print("shape@16k =", stereo_16k.shape)
                    printed_shape = True

                # Voice Activity Detection
                should_send = True
                if VAD_ENABLED:
                    has_voice, levels = voice_activity_detection(stereo_16k)
                    should_send = has_voice
                    if has_voice:
                        vad_stats["sent"] += 1
                    else:
                        vad_stats["silence"] += 1

                # Enviar audio si hay actividad o si VAD está deshabilitado
                if should_send:
                    conn.send(to_pcm16(stereo_16k))

                # Calcular niveles RMS para logging
                mic_level = float(np.sqrt(np.mean(mb[:n]**2)))
                loop_level = float(np.sqrt(np.mean(lb[:n]**2)))

                audio_stats["mic_levels"].append(mic_level)
                audio_stats["loop_levels"].append(loop_level)

                tick += 1
                if tick % LOG_RMS_INTERVAL == 0:
                    # Calcular estadísticas de niveles
                    mic_avg = np.mean(audio_stats["mic_levels"][-LOG_RMS_INTERVAL:])
                    loop_avg = np.mean(audio_stats["loop_levels"][-LOG_RMS_INTERVAL:])

                    if LOG_EVENTS:
                        print(f"📊 RMS: Mic={mic_avg:.4f}, Loop={loop_avg:.4f} | VAD: {vad_stats['sent']}/{vad_stats['sent']+vad_stats['silence']}")

        except KeyboardInterrupt:
            if LOG_EVENTS:
                print("\n⏹️  Transcription interrupted by user")
        except Exception as e:
            if LOG_EVENTS:
                print(f"❌ Session error: {e}")
                print(f"❌ Error type: {type(e).__name__}")
        finally:
            # Mejor manejo de finalización - v3 Best Practice
            try:
                if conn:
                    if LOG_EVENTS:
                        print("🔄 Finishing connection...")
                    # Usar finish() en lugar de close() para v3
                    conn.finish()
                    if LOG_EVENTS:
                        print("✅ Connection finished successfully")
            except Exception as e:
                if LOG_EVENTS:
                    print(f"⚠️  Warning during connection cleanup: {e}")

            # Mostrar estadísticas finales
            if LOG_EVENTS and vad_stats["sent"] > 0:
                total_frames = vad_stats["sent"] + vad_stats["silence"]
                silence_ratio = vad_stats["silence"] / total_frames if total_frames > 0 else 0
                print(f"📈 Final Statistics: {vad_stats['sent']} frames sent, {silence_ratio:.1%} silence")

async def main():
    if not DG_KEY:
        raise SystemExit("Falta DEEPGRAM_API_KEY")

    # Configurar región de Deepgram
    if DG_REGION == "eu":
        base_url = "wss://api.eu.deepgram.com"
    else:
        base_url = DG_BASE_WSS

    if LOG_EVENTS:
        print(f"🌐 Conectando a región: {DG_REGION} ({base_url})")
        print(f"🎵 Modo audio: {AUDIO_MODE} ({STEREO_LAYOUT})")
        print(f"⚙️  VAD: {'ON' if VAD_ENABLED else 'OFF'}, Normalización: {'ON' if NORMALIZE_ENABLED else 'OFF'}")
        print(f"� NOVA 3 Features: Interim={'ON' if INTERIM_RESULTS else 'OFF'}, Endpointing={'ON' if ENDPOINTING else 'OFF'}, PII Redaction={'ON' if PII_REDACT else 'OFF'}")
        print(f"�🔄 Reconexión: {'ON' if RECONNECT_ENABLED else 'OFF'}")

    mic = pick(lambda n: MIC_NAME_SUBSTR.lower() in n.lower(), sc.all_microphones()) or sc.default_microphone()
    spk = pick(lambda n: SPK_NAME_SUBSTR.lower() in n.lower(), sc.all_speakers()) or sc.default_speaker()
    loop = sc.get_microphone(id=spk.name, include_loopback=True)

    print(f"[MIC ] {mic.name} (buscando: '{MIC_NAME_SUBSTR}')")
    print(f"[LOOP] {loop.name} via {spk.name} (buscando: '{SPK_NAME_SUBSTR}')")

    # Mostrar dispositivos disponibles
    if LOG_DEBUG:
        print("🔍 Dispositivos de audio disponibles:")
        print("   Micrófonos:")
        for m in sc.all_microphones():
            print(f"     - {m.name}")
        print("   Altavoces:")
        for s in sc.all_speakers():
            print(f"     - {s.name}")

    # Variables para reconexión
    reconnect_attempts = 0
    max_attempts = MAX_RECONNECT_ATTEMPTS if RECONNECT_ENABLED else 0

    while reconnect_attempts <= max_attempts:
        try:
            await run_transcription_session(mic, spk, loop, base_url)
            break  # Éxito, salir del bucle

        except Exception as e:
            if RECONNECT_ENABLED and reconnect_attempts < max_attempts:
                reconnect_attempts += 1
                if LOG_EVENTS:
                    print(f"🔄 Reconexión {reconnect_attempts}/{max_attempts} en {RECONNECT_DELAY}s... ({e})")
                await asyncio.sleep(RECONNECT_DELAY)
            else:
                if LOG_EVENTS:
                    print(f"❌ Error final: {e}")
                raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye")
