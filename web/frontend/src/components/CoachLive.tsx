'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useCoach } from '@/contexts/CoachContext';
import { CoachAPI } from '@/services/api';
import { TranscriptSegment, Objection, Suggestion } from '@/types/coach';

// Componente de Transcripción
function TranscriptPanel({
  segments,
  isRecording
}: {
  segments: TranscriptSegment[],
  isRecording: boolean
}) {
  const transcriptRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
    }
  }, [segments]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-800">Transcripción</h2>
        <div className={`flex items-center space-x-2 ${isRecording ? 'text-red-500' : 'text-gray-400'}`}>
          <div className={`w-3 h-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-sm font-medium">
            {isRecording ? 'Grabando...' : 'Pausado'}
          </span>
        </div>
      </div>

      <div
        ref={transcriptRef}
        className="flex-1 overflow-y-auto bg-gray-50 rounded-lg p-4 space-y-3"
      >
        {segments.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            <p>La transcripción aparecerá aquí...</p>
            <p className="text-sm mt-2">Presiona &quot;Iniciar&quot; para comenzar</p>
          </div>
        ) : (
          segments.map((segment, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg ${
                segment.is_objection
                  ? 'bg-red-100 border-l-4 border-red-500'
                  : segment.speaker === 0
                    ? 'bg-blue-50 border-l-4 border-blue-500'
                    : 'bg-green-50 border-l-4 border-green-500'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-medium px-2 py-1 rounded ${
                  segment.speaker === 0 ? 'bg-blue-200 text-blue-800' : 'bg-green-200 text-green-800'
                }`}>
                  {segment.speaker === 0 ? 'Tú' : 'Cliente'}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(parseInt(segment.timestamp)).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-gray-800">{segment.text}</p>
              {segment.is_objection && (
                <div className="mt-2 text-xs text-red-600 font-medium">
                  ⚠️ Objeción detectada
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Componente de Objeciones
function ObjectionsPanel({ objections }: { objections: Objection[] }) {
  const objectionTypes = {
    precio: { label: 'Precio', color: 'bg-red-500' },
    tiempo: { label: 'Tiempo', color: 'bg-orange-500' },
    autoridad: { label: 'Autoridad', color: 'bg-yellow-500' },
    competencia: { label: 'Competencia', color: 'bg-purple-500' },
    confianza: { label: 'Confianza', color: 'bg-pink-500' },
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 h-full">
      <h3 className="text-lg font-bold text-gray-800 mb-4">Objeciones Detectadas</h3>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {objections.length === 0 ? (
          <div className="text-center text-gray-500 py-4">
            <p>No se han detectado objeciones aún</p>
          </div>
        ) : (
          objections.map((objection, index) => {
            const typeInfo = objectionTypes[objection.type as keyof typeof objectionTypes]
              || { label: objection.type, color: 'bg-gray-500' };

            return (
              <div key={index} className="border rounded-lg p-3 bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium text-white ${typeInfo.color}`}>
                    {typeInfo.label}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(parseInt(objection.timestamp)).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-2">&quot;{objection.text}&quot;</p>
                <div className="text-xs text-gray-500">
                  Confianza: {Math.round(objection.confidence * 100)}%
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

// Componente de Sugerencias
function SuggestionsPanel({ suggestions }: { suggestions: Suggestion[] }) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Error copying to clipboard:', err);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 h-full">
      <h3 className="text-lg font-bold text-gray-800 mb-4">Sugerencias de Respuesta</h3>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {suggestions.length === 0 ? (
          <div className="text-center text-gray-500 py-4">
            <p>Las sugerencias aparecerán aquí cuando se detecten objeciones</p>
          </div>
        ) : (
          suggestions.slice(-3).map((suggestion, index) => (
            <div key={index} className="border rounded-lg p-3 bg-blue-50">
              <div className="flex items-center justify-between mb-2">
                <span className="px-2 py-1 rounded text-xs font-medium text-white bg-blue-500">
                  {suggestion.type}
                </span>
                <button
                  onClick={() => copyToClipboard(suggestion.text, index)}
                  className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded transition-colors"
                >
                  {copiedIndex === index ? '✓ Copiado' : 'Copiar'}
                </button>
              </div>
              <p className="text-sm text-gray-700">{suggestion.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Componente de Controles
function ControlsPanel({
  isRecording,
  onStartRecording,
  onStopRecording,
  settings,
  onToggleCoach
}: {
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  settings: { coach_enabled: boolean; model: string; auto_detect_objections: boolean; show_suggestions: boolean };
  onToggleCoach: (enabled: boolean) => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h3 className="text-lg font-bold text-gray-800 mb-4">Controles</h3>

      <div className="space-y-4">
        <div className="flex space-x-2">
          {!isRecording ? (
            <button
              onClick={onStartRecording}
              className="flex-1 bg-red-500 hover:bg-red-600 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              ▶️ Iniciar Grabación
            </button>
          ) : (
            <button
              onClick={onStopRecording}
              className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-medium py-3 px-4 rounded-lg transition-colors"
            >
              ⏹️ Detener Grabación
            </button>
          )}
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Modo Coach:</span>
          <button
            onClick={() => onToggleCoach(!settings.coach_enabled)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              settings.coach_enabled ? 'bg-green-500' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                settings.coach_enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Modelo de IA:
          </label>
          <select
            value={settings.model}
            onChange={() => {/* TODO: Implementar cambio de modelo */}}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="nova-3-general">Nova 3 General</option>
            <option value="gpt-4o-mini">GPT-4o Mini</option>
          </select>
        </div>
      </div>
    </div>
  );
}

// Componente Principal Coach Live
export default function CoachLive() {
  const { settings, isRecording, setIsRecording, currentCallId, setCurrentCallId } = useCoach();
  const [sessionData, setSessionData] = useState<{ call_id: string; ws_url: string; status: string } | null>(null);

  const {
    isConnected,
    currentTranscript,
    objections,
    suggestions,
    error,
    connect,
    startTranscription,
    stopTranscription,
    toggleCoach
  } = useWebSocket(currentCallId);

  const handleStartRecording = async () => {
    try {
      if (!sessionData) {
        // Iniciar nueva sesión
        console.log('🚀 Iniciando nueva sesión...');
        const session = await CoachAPI.startSession();
        console.log('✅ Sesión iniciada:', session);
        setSessionData(session);
        setCurrentCallId(session.call_id);

        // Conectar WebSocket
        console.log('🔌 Conectando WebSocket a:', session.ws_url);
        connect(session.ws_url);
      }

      // Iniciar transcripción
      console.log('🎤 Iniciando transcripción...');
      startTranscription();
      setIsRecording(true);
    } catch (err) {
      console.error('❌ Error starting recording:', err);
      // El error será manejado por el hook useWebSocket
    }
  };

  const handleStopRecording = () => {
    stopTranscription();
    setIsRecording(false);
  };

  const handleToggleCoach = (enabled: boolean) => {
    toggleCoach(enabled);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Sales Coach Live</h1>
          <p className="text-gray-600 mt-2">
            Sistema de coaching de ventas en tiempo real
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
          {/* Panel Izquierdo Superior - Objeciones */}
          <div className="lg:col-span-1">
            <ObjectionsPanel objections={objections} />
          </div>

          {/* Panel Central - Transcripción */}
          <div className="lg:col-span-2">
            <TranscriptPanel segments={currentTranscript} isRecording={isRecording} />
          </div>

          {/* Panel Derecho - Controles y Sugerencias */}
          <div className="lg:col-span-1 space-y-6">
            <ControlsPanel
              isRecording={isRecording}
              onStartRecording={handleStartRecording}
              onStopRecording={handleStopRecording}
              settings={settings}
              onToggleCoach={handleToggleCoach}
            />
            <SuggestionsPanel suggestions={suggestions} />
          </div>
        </div>

        {/* Barra de Estado */}
        <div className="mt-6 bg-white rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-600' : 'bg-red-600'}`} />
                <span className="text-sm font-medium">
                  {isConnected ? 'Conectado' : 'Desconectado'}
                </span>
              </div>

              {currentCallId && (
                <div className="text-sm text-gray-600">
                  Call ID: <code className="bg-gray-100 px-2 py-1 rounded">{currentCallId}</code>
                </div>
              )}
            </div>

            <div className="text-sm text-gray-500">
              Segmentos: {currentTranscript.length} | Objeciones: {objections.length}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
