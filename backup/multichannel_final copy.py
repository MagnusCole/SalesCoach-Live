import os, asyncio, warnings, json
import numpy as np
import soundcard as sc
from dotenv import load_dotenv
from deepgram import DeepgramClient, DeepgramClientOptions, LiveOptions, LiveTranscriptionEvents

if hasattr(np, "frombuffer"):  # parche NumPy 2.x para soundcard
    np.fromstring = np.frombuffer
warnings.filterwarnings("ignore", category=UserWarning, module="soundcard")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="soundcard")  # Suprimir SoundcardRuntimeWarning
load_dotenv()

DG_KEY = os.getenv("DEEPGRAM_API_KEY") or ""
MODEL  = os.getenv("DEEPGRAM_MODEL", "nova-3")
LANG   = os.getenv("DEEPGRAM_LANGUAGE", "es")
ENC    = os.getenv("DEEPGRAM_ENCODING", "linear16")
SR     = int(os.getenv("DEEPGRAM_SAMPLE_RATE", "16000"))
CH     = 2
MC     = True
SMART  = True

MIC_NAME_SUBSTR = os.getenv("MIC_NAME_SUBSTR", "Nvidia")
SPK_NAME_SUBSTR = os.getenv("SPK_NAME_SUBSTR", "PRO")
FS_CAP, FRAME_MS = 48000, 20  # Reducido de 40ms a 20ms para enviar datos más frecuentemente
BLOCK = int(FS_CAP * FRAME_MS / 1000.0)
MIC_GAIN = float(os.getenv("MIC_GAIN", "3.0"))
LOOP_GAIN = float(os.getenv("LOOP_GAIN", "5.0"))

def pick(pred, items):
    for it in items:
        if pred(it.name): return it
    return None

def resample_f32(x, fs_in, fs_out):
    if fs_in == fs_out or x.size == 0: return x.astype(np.float32, copy=False)
    n = x.shape[0]; m = int(round(n*fs_out/fs_in))
    ti = np.linspace(0,1,n,endpoint=False,dtype=np.float32)
    to = np.linspace(0,1,m,endpoint=False,dtype=np.float32)
    return np.stack([np.interp(to, ti, x[:,c]).astype(np.float32) for c in range(x.shape[1])], axis=1)

def to_pcm16(x): return (np.clip(x, -1, 1)*32767).astype(np.int16).tobytes()

async def main():
    if not DG_KEY:
        raise SystemExit("Falta DEEPGRAM_API_KEY")

    mic = pick(lambda n: MIC_NAME_SUBSTR.lower() in n.lower(), sc.all_microphones()) or sc.default_microphone()
    spk = pick(lambda n: SPK_NAME_SUBSTR.lower() in n.lower(), sc.all_speakers()) or sc.default_speaker()
    loop = sc.get_microphone(id=spk.name, include_loopback=True)

    print(f"[MIC ] {mic.name} (buscando: '{MIC_NAME_SUBSTR}')")
    print(f"[LOOP] {loop.name} via {spk.name} (buscando: '{SPK_NAME_SUBSTR}')")

    # Mostrar todos los dispositivos disponibles para diagnóstico
    print("🔍 Dispositivos de audio disponibles:")
    print("   Micrófonos:")
    for m in sc.all_microphones():
        print(f"     - {m.name}")
    print("   Altavoces:")
    for s in sc.all_speakers():
        print(f"     - {s.name}")

    dg = DeepgramClient(DG_KEY)
    conn = dg.listen.websocket.v("1")

    def on_transcript(self, result, **kwargs):
        try:
            msg = result  # El resultado viene como primer parámetro
            alts = msg.channel.alternatives or []
            if alts and alts[0].transcript:
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
                        # Si es un array de canales, buscar el que tiene transcript
                        for i, ch in enumerate(msg.channels):
                            if hasattr(ch, 'alternatives') and ch.alternatives:
                                channel_info = i
                                break
                
                # Método 3: asumir basado en el contenido o metadata
                if channel_info is None:
                    # Por ahora, alternar entre canales o usar heurísticas
                    # Esto es temporal hasta entender mejor la estructura
                    transcript_text = alts[0].transcript.lower()
                    # Heurística simple: si contiene ciertas palabras, asumir canal
                    # Esto se puede mejorar con más análisis
                    channel_info = 0  # Default a mic (usuario)
                
                # Determinar quién habla basado en el canal
                if isinstance(channel_info, (list, tuple)) and len(channel_info) > 0:
                    # Si es una lista, tomar el primer elemento
                    primary_channel = channel_info[0]
                    if primary_channel == 0:
                        who = "Tú"
                    elif primary_channel == 1:
                        who = "Amigo"
                    else:
                        who = f"Canal {primary_channel}"
                elif isinstance(channel_info, int):
                    # Si es un entero directo
                    if channel_info == 0:
                        who = "Tú"
                    elif channel_info == 1:
                        who = "Amigo"
                    else:
                        who = f"Canal {channel_info}"
                else:
                    who = f"Canal {channel_info}" if channel_info is not None else "Desconocido"
                
                print(f"[{who}] {alts[0].transcript}")
                
                # Debug: mostrar información del canal para diagnóstico
                if channel_info is None:
                    print(f"DEBUG: No se pudo determinar canal. Estructura del mensaje:")
                    print(f"  msg type: {type(msg)}")
                    print(f"  msg dir: {[attr for attr in dir(msg) if not attr.startswith('_')]}")
                    if hasattr(msg, 'channel'):
                        print(f"  channel type: {type(msg.channel)}")
                        print(f"  channel dir: {[attr for attr in dir(msg.channel) if not attr.startswith('_')]}")
        except Exception as e:
            print(f"Error processing transcript: {e}")
            print(f"Message type: {type(result)}")
            print(f"Message attributes: {dir(result) if hasattr(result, '__dict__') else 'No dict'}")

    def on_error(self, error, **kwargs):
        print(f"[DG error] {error}")

    def on_metadata(self, metadata, **kwargs):
        print(f"[DG metadata] {metadata}")

    def on_close(self, close, **kwargs):
        print(f"[DG close] {close}")

    opts = LiveOptions(model=MODEL, language=LANG, encoding=ENC,
                       sample_rate=SR, channels=CH, multichannel=MC,
                       smart_format=SMART)

    # Registrar handlers
    conn.on(LiveTranscriptionEvents.Transcript, on_transcript)
    conn.on(LiveTranscriptionEvents.Error, on_error)
    conn.on(LiveTranscriptionEvents.Metadata, on_metadata)
    conn.on(LiveTranscriptionEvents.Close, on_close)

    print(f"🔧 Configuración LiveOptions:")
    print(f"   Model: {MODEL}")
    print(f"   Language: {LANG}")
    print(f"   Encoding: {ENC}")
    print(f"   Sample Rate: {SR}")
    print(f"   Channels: {CH}")
    print(f"   Multichannel: {MC}")
    print(f"   Smart Format: {SMART}")
    print("Connecting…")

    try:
        conn.start(opts)
        print("✅ Connected to Deepgram successfully!")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        # Intentar obtener más detalles del error
        if hasattr(e, 'headers'):
            print(f"❌ Headers: {e.headers}")
        return

    with mic.recorder(FS_CAP, channels=1, blocksize=BLOCK) as mic_rec, \
         loop.recorder(FS_CAP, channels=2, blocksize=BLOCK) as loop_rec:

        print("🎙️ L=Mic | R=Loopback. Habla y reproduce algo. Ctrl+C para salir.")
        printed_shape = False
        tick = 0
        silence_frames = 0

        while True:
            mb = mic_rec.record(numframes=BLOCK)
            lb = loop_rec.record(numframes=BLOCK)

            if MIC_GAIN != 1.0: mb = np.clip(mb*MIC_GAIN, -1, 1)
            if LOOP_GAIN != 1.0: lb = np.clip(lb*LOOP_GAIN, -1, 1)

            lb = lb.mean(axis=1, keepdims=True)  # mono
            n = min(mb.shape[0], lb.shape[0])
            if n <= 0: await asyncio.sleep(0); continue

            stereo_48k = np.concatenate([mb[:n], lb[:n]], axis=1)   # (N,2)
            stereo_16k = resample_f32(stereo_48k, FS_CAP, SR)       # (M,2)
            assert stereo_16k.ndim == 2 and stereo_16k.shape[1] == 2, stereo_16k.shape

            if not printed_shape:
                print("shape@16k =", stereo_16k.shape)
                printed_shape = True

            # Enviar audio - el cliente ahora maneja keepalive automáticamente
            mic_level = float(np.sqrt(np.mean(mb[:n]**2)))
            loop_level = float(np.sqrt(np.mean(lb[:n]**2)))

            # Siempre enviar audio
            conn.send(to_pcm16(stereo_16k))

            tick += 1
            if tick % 100 == 0:
                print(f"📊 Raw RMS: Mic={mic_level:.4f}, Loop={loop_level:.4f}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye")
