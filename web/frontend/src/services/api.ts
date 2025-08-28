import { SessionData } from '@/types/coach';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class CoachAPI {
  static async startSession(): Promise<SessionData> {
    const response = await fetch(`${API_BASE_URL}/session/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    if (!response.ok) {
      throw new Error(`Error starting session: ${response.statusText}`);
    }

    return response.json();
  }

  static async getTranscriptTXT(callId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/calls/${callId}/transcript.txt`);

    if (!response.ok) {
      throw new Error(`Error getting transcript: ${response.statusText}`);
    }

    return response.blob();
  }

  static async getTranscriptJSON(callId: string): Promise<Record<string, unknown>> {
    const response = await fetch(`${API_BASE_URL}/calls/${callId}/transcript.json`);

    if (!response.ok) {
      throw new Error(`Error getting transcript data: ${response.statusText}`);
    }

    return response.json();
  }

  static async getAudio(callId: string, audioType: 'mix' | 'mic' | 'loop'): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/calls/${callId}/audio/${audioType}.wav`);

    if (!response.ok) {
      throw new Error(`Error getting audio: ${response.statusText}`);
    }

    return response.blob();
  }

  static async listCalls(): Promise<Record<string, unknown>[]> {
    const response = await fetch(`${API_BASE_URL}/calls`);

    if (!response.ok) {
      throw new Error(`Error listing calls: ${response.statusText}`);
    }

    const data = await response.json();
    return data.calls || [];
  }
}
