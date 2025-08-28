'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { WebSocketMessage, CallData, TranscriptSegment, Objection, Suggestion, CallSummary } from '@/types/coach';

export const useWebSocket = (callId: string | null) => {
  const [isConnected, setIsConnected] = useState(false);
  const [callData, setCallData] = useState<CallData | null>(null);
  const [currentTranscript, setCurrentTranscript] = useState<TranscriptSegment[]>([]);
  const [objections, setObjections] = useState<Objection[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback((wsUrl: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('🔌 WebSocket conectado');
        setIsConnected(true);
        setError(null);

        // Iniciar ping para mantener conexión viva
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleMessage(message);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket desconectado');
        setIsConnected(false);
        cleanup();

        // Intentar reconectar después de 3 segundos
        reconnectTimeoutRef.current = setTimeout(() => {
          if (callId) {
            console.log('🔄 Intentando reconectar...');
            connect(wsUrl);
          }
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Error de conexión WebSocket');
      };

    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Error al crear conexión WebSocket');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callId]);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    const { type, data } = message;
    const dataTyped = data as Record<string, unknown>; // Type assertion for WebSocket data

    switch (type) {
      case 'session_started':
        console.log('📡 Sesión iniciada:', data);
        setCallData({
          call_id: dataTyped.call_id as string,
          start_time: dataTyped.timestamp as string,
          segments: [],
          objections: [],
          suggestions: []
        });
        break;

      case 'transcript_update':
        setCurrentTranscript(prev => {
          const newSegment: TranscriptSegment = {
            speaker: dataTyped.speaker as number,
            text: dataTyped.text as string,
            timestamp: dataTyped.ts_ms as string,
            confidence: dataTyped.confidence as number,
            is_objection: false
          };
          return [...prev, newSegment];
        });
        break;

      case 'objection_detected':
        const objection: Objection = {
          type: dataTyped.type as string,
          text: dataTyped.text as string,
          timestamp: dataTyped.ts_ms as string,
          confidence: dataTyped.confidence as number,
          source: dataTyped.source as string
        };
        setObjections(prev => [...prev, objection]);

        // Marcar el último segmento como objeción
        setCurrentTranscript(prev =>
          prev.map((segment, index) =>
            index === prev.length - 1
              ? { ...segment, is_objection: true }
              : segment
          )
        );
        break;

      case 'suggestion_ready':
        const suggestion: Suggestion = {
          type: dataTyped.type as string,
          text: dataTyped.text as string,
          timestamp: dataTyped.ts_ms as string,
          source: dataTyped.source as string
        };
        setSuggestions(prev => [...prev, suggestion]);
        break;

      case 'call_completed':
        console.log('📞 Llamada completada:', data);
        if (callData) {
          setCallData(prev => prev ? {
            ...prev,
            end_time: dataTyped.end_time as string,
            duration: dataTyped.duration as number,
            summary: dataTyped.summary as CallSummary
          } : null);
        }
        break;

      case 'pong':
        // Respuesta al ping - conexión viva
        break;

      default:
        console.log('Mensaje WebSocket desconocido:', type, data);
    }
  }, [callData]);

  const sendMessage = useCallback((type: string, data: Record<string, unknown> = {}) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, ...data }));
    }
  }, []);

  const startTranscription = useCallback(() => {
    sendMessage('start_transcription');
  }, [sendMessage]);

  const stopTranscription = useCallback(() => {
    sendMessage('stop_transcription');
  }, [sendMessage]);

  const toggleCoach = useCallback((enabled: boolean) => {
    sendMessage('toggle_coach', { enabled });
  }, [sendMessage]);

  const cleanup = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  useEffect(() => {
    return () => {
      cleanup();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [cleanup]);

  return {
    isConnected,
    callData,
    currentTranscript,
    objections,
    suggestions,
    error,
    connect,
    startTranscription,
    stopTranscription,
    toggleCoach,
    sendMessage
  };
};
