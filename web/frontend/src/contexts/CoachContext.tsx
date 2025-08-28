'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { CoachSettings } from '@/types/coach';

interface CoachContextType {
  settings: CoachSettings;
  updateSettings: (newSettings: Partial<CoachSettings>) => void;
  isRecording: boolean;
  setIsRecording: (recording: boolean) => void;
  currentCallId: string | null;
  setCurrentCallId: (callId: string | null) => void;
}

const CoachContext = createContext<CoachContextType | undefined>(undefined);

const defaultSettings: CoachSettings = {
  coach_enabled: true,
  model: 'nova-3-general',
  auto_detect_objections: true,
  show_suggestions: true,
};

export function CoachProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<CoachSettings>(defaultSettings);
  const [isRecording, setIsRecording] = useState(false);
  const [currentCallId, setCurrentCallId] = useState<string | null>(null);

  const updateSettings = useCallback((newSettings: Partial<CoachSettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  }, []);

  const value: CoachContextType = {
    settings,
    updateSettings,
    isRecording,
    setIsRecording,
    currentCallId,
    setCurrentCallId,
  };

  return (
    <CoachContext.Provider value={value}>
      {children}
    </CoachContext.Provider>
  );
}

export function useCoach() {
  const context = useContext(CoachContext);
  if (context === undefined) {
    throw new Error('useCoach must be used within a CoachProvider');
  }
  return context;
}
