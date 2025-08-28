"use client";
import { useEffect, useRef, useState } from "react";

const API_WS = process.env.NEXT_PUBLIC_API_WS || "ws://localhost:8000/ws/demo";

export default function Live() {
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const [log, setLog] = useState<string[]>([]);
  const [hint, setHint] = useState<string>("");
  const [isConnected, setIsConnected] = useState(false);
  const [coachEnabled, setCoachEnabled] = useState(true);
  const [callId, setCallId] = useState<string>("");
  const [callEnded, setCallEnded] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const audioChunksRef = useRef<Blob[]>([]);

  const cleanup = () => {
    // Limpiar MediaRecorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    // Limpiar tracks del stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }

    // Limpiar WebSocket
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Limpiar timeout de reconexión
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  };

  const connectWebSocket = () => {
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      setLog(prev => [...prev, "❌ Máximo número de reconexiones alcanzado"]);
      return;
    }

    // Generar ID único para la llamada
    const newCallId = `call_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setCallId(newCallId);

    const ws = new WebSocket(`${API_WS.replace('/ws/demo', `/ws/${newCallId}`)}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;
      setLog(prev => [...prev, "🔗 Conectado al servidor"]);
    };

    ws.onclose = () => {
      setIsConnected(false);
      setCallEnded(true);
      setLog(prev => [...prev, "🔌 Desconectado del servidor"]);

      // Intentar reconectar con backoff exponencial
      const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
      reconnectAttemptsRef.current++;

      reconnectTimeoutRef.current = setTimeout(() => {
        setLog(prev => [...prev, `🔄 Intentando reconectar... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`]);
        connectWebSocket();
      }, delay);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setLog(prev => [...prev, "⚠️ Error de conexión"]);
    };

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.results) {
          const alt = msg.results[0]?.alternatives?.[0];
          if (alt?.transcript) setLog((l) => [...l, `👤 ${alt.transcript}`]);
        } else if (msg.type === "objection_detected" && coachEnabled) {
          setLog((l) => [...l, `⚠️ Objeción: ${msg.obj_type} → ${msg.snippet}`]);
          setHint(msg.suggestion || "");
        }
      } catch {}
    };
  };

  useEffect(() => {
    (async () => {
      try {
        // Conectar WebSocket
        connectWebSocket();

        // Obtener stream de pantalla/audio
        const stream = await (navigator.mediaDevices as any).getDisplayMedia({
          audio: true,
          video: false
        });
        streamRef.current = stream;

        // Configurar MediaRecorder
        const rec = new MediaRecorder(stream, {
          mimeType: "audio/webm;codecs=opus",
          audioBitsPerSecond: 128000
        });
        mediaRecorderRef.current = rec;

        // Limpiar chunks anteriores
        audioChunksRef.current = [];

        rec.ondataavailable = (e) => {
          if (e.data.size > 0) {
            // Almacenar chunk localmente para el blob final
            audioChunksRef.current.push(e.data);

            // Enviar chunk al WebSocket para transcripción en tiempo real
            if (wsRef.current?.readyState === WebSocket.OPEN) {
              e.data.arrayBuffer().then(buf => wsRef.current?.send(new Uint8Array(buf)));
            }
          }
        };

        rec.onstop = async () => {
          setLog(prev => [...prev, "⏹️ Grabación detenida"]);

          // Crear blob final y enviarlo al servidor
          if (audioChunksRef.current.length > 0) {
            const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });

            try {
              const formData = new FormData();
              formData.append("file", audioBlob, "audio.webm");

              // Construir URL base dinámicamente
              const apiBase = new URL(API_WS).origin.replace('ws', 'http').replace('wss', 'https');
              const uploadUrl = `${apiBase}/upload-final/${callId}`;

              const response = await fetch(uploadUrl, {
                method: 'POST',
                body: formData
              });

              if (response.ok) {
                setLog(prev => [...prev, "💾 Audio guardado exitosamente"]);
              } else {
                setLog(prev => [...prev, "❌ Error al guardar audio"]);
              }
            } catch (error) {
              console.error("Error uploading audio:", error);
              setLog(prev => [...prev, "❌ Error al subir audio"]);
            }
          }

          setIsRecording(false);
        };

        // Iniciar grabación
        rec.start(250);
        setIsRecording(true);
        setLog(prev => [...prev, "🎤 Grabación iniciada"]);

      } catch (error) {
        console.error("Error al inicializar:", error);
        setLog(prev => [...prev, "❌ Error al acceder al audio de pantalla"]);
      }
    })();

    // Cleanup al desmontar
    return cleanup;
  }, []);

  const toggleCoach = (enabled: boolean) => {
    setCoachEnabled(enabled);

    // Enviar mensaje al backend si hay conexión WebSocket
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "coach_toggle",
        enabled: enabled
      }));
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  const downloadTranscript = async () => {
    if (!callId) return;
    try {
      // Construir URL base dinámicamente
      const apiBase = new URL(API_WS).origin.replace('ws', 'http').replace('wss', 'https');
      const response = await fetch(`${apiBase}/calls/${callId}/transcript.txt`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcript_${callId}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        setLog(prev => [...prev, "❌ Error descargando transcript"]);
      }
    } catch (error) {
      setLog(prev => [...prev, "❌ Error de conexión al descargar transcript"]);
    }
  };

  const downloadAudio = async () => {
    if (!callId) return;
    try {
      // Construir URL base dinámicamente
      const apiBase = new URL(API_WS).origin.replace('ws', 'http').replace('wss', 'https');
      const response = await fetch(`${apiBase}/calls/${callId}/audio.webm`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audio_${callId}.webm`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        setLog(prev => [...prev, "❌ Error descargando audio"]);
      }
    } catch (error) {
      setLog(prev => [...prev, "❌ Error de conexión al descargar audio"]);
    }
  };

  return (
    <main className="p-6 grid grid-cols-3 gap-4">
      <section className="col-span-2 border rounded p-3 h-[70vh] overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold flex items-center gap-2">
            Transcripción (Prospecto)
            <span className={`text-xs px-2 py-1 rounded ${isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
            </span>
            {callId && (
              <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                ID: {callId}
              </span>
            )}
          </h2>
          <div className="flex items-center gap-2">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={coachEnabled}
                onChange={(e) => toggleCoach(e.target.checked)}
                className="rounded"
              />
              Coach Activo
            </label>
          </div>
        </div>
        <pre className="whitespace-pre-wrap text-sm">{log.join("\n")}</pre>
        <div className="mt-4 flex gap-2 flex-wrap">
          <button
            className="px-3 py-2 rounded bg-red-500 text-white hover:bg-red-600"
            onClick={stopRecording}
          >
            Detener Grabación
          </button>
          {callEnded && callId && (
            <>
              <button
                className="px-3 py-2 rounded bg-blue-500 text-white hover:bg-blue-600"
                onClick={downloadTranscript}
              >
                📄 Descargar Transcript
              </button>
              <button
                className="px-3 py-2 rounded bg-green-500 text-white hover:bg-green-600"
                onClick={downloadAudio}
              >
                🎵 Descargar Audio
              </button>
            </>
          )}
        </div>
      </section>
      <aside className="border rounded p-3">
        <h2 className="font-semibold mb-2">💡 Sugerencia</h2>
        <p className="text-sm">{hint || "—"}</p>
        {hint && (
          <button className="mt-3 px-3 py-2 rounded bg-black text-white" onClick={() => navigator.clipboard.writeText(hint)}>
            Copiar
          </button>
        )}
      </aside>
    </main>
  );
}
