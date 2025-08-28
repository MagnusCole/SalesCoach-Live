"use client";
import { useEffect, useRef, useState } from "react";

const API_WS = process.env.NEXT_PUBLIC_API_WS || "ws://localhost:8000/ws/demo";

export default function Live() {
  const wsRef = useRef<WebSocket | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [hint, setHint] = useState<string>("");

  useEffect(() => {
    (async () => {
      const ws = new WebSocket(API_WS);
      wsRef.current = ws;
      ws.onmessage = (evt) => {
        try {
          const msg = JSON.parse(evt.data);
          if (msg.results) {
            const alt = msg.results[0]?.alternatives?.[0];
            if (alt?.transcript) setLog((l) => [...l, `👤 ${alt.transcript}`]);
          } else if (msg.type === "objection_detected") {
            setLog((l) => [...l, `⚠️ Objeción: ${msg.obj_type} → ${msg.snippet}`]);
            setHint(msg.suggestion || "");
          }
        } catch {}
      };

      const stream = await (navigator.mediaDevices as any).getDisplayMedia({ audio:true, video:false });
      const rec = new MediaRecorder(stream, { mimeType: "audio/webm;codecs=opus", audioBitsPerSecond: 128000 });
      rec.ondataavailable = (e) => e.data.arrayBuffer().then(buf => ws.send(new Uint8Array(buf)));
      rec.start(250);
    })();

    return () => { wsRef.current?.close(); };
  }, []);

  return (
    <main className="p-6 grid grid-cols-3 gap-4">
      <section className="col-span-2 border rounded p-3 h-[70vh] overflow-auto">
        <h2 className="font-semibold mb-2">Transcripción (Prospecto)</h2>
        <pre className="whitespace-pre-wrap text-sm">{log.join("\n")}</pre>
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
