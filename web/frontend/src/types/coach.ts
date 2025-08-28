// Tipos TypeScript para la aplicación de coaching de ventas

export interface TranscriptSegment {
  speaker: number;
  text: string;
  timestamp: string;
  confidence: number;
  is_objection?: boolean;
}

export interface Objection {
  type: string;
  text: string;
  timestamp: string;
  confidence: number;
  source: string;
}

export interface Suggestion {
  type: string;
  text: string;
  timestamp: string;
  source: string;
}

export interface CallData {
  call_id: string;
  start_time: string;
  end_time?: string;
  duration?: number;
  segments: TranscriptSegment[];
  objections: Objection[];
  suggestions: Suggestion[];
  summary?: CallSummary;
}

export interface CallSummary {
  overview: string;
  key_topics: string[];
  next_steps: string[];
  confidence_score: number;
  total_objections: number;
  objection_types: Record<string, number>;
}

export interface WebSocketMessage {
  type: string;
  data: Record<string, unknown>;
}

export interface SessionData {
  call_id: string;
  ws_url: string;
  status: string;
}

export interface CoachSettings {
  coach_enabled: boolean;
  model: string;
  auto_detect_objections: boolean;
  show_suggestions: boolean;
}

export type AudioType = 'mix' | 'mic' | 'loop';
export type CoachModel = 'nova-3-general' | 'nova-3-general' | 'gpt-4o-mini';
