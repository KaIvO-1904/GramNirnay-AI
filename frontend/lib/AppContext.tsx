'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authenticateWithGoogleBackend, fetchUserAnalysesBackend, saveUserAnalysisBackend } from '@/lib/api';
import { promptGoogleSignIn } from '@/lib/googleAuth';

export type FontSize = 'normal' | 'large' | 'xlarge';

export interface UserAccount {
  id: string;
  name: string;
  email: string;
  avatar: string;
  provider: 'google' | 'guest';
}

export interface AnalysisHistoryItem {
  id: string;
  businessIdea: string;
  district: string;
  state: string;
  date: string;
  score: number;
  recommendation: string;
  projectCost: number;
  data: any;
}

interface AppContextType {
  user: UserAccount | null;
  token: string | null;
  signInWithGoogle: () => Promise<void>;
  signOut: () => void;
  fontSize: FontSize;
  setFontSize: (size: FontSize) => void;
  highContrast: boolean;
  setHighContrast: (val: boolean) => void;
  reducedMotion: boolean;
  setReducedMotion: (val: boolean) => void;
  history: AnalysisHistoryItem[];
  addHistoryItem: (item: Omit<AnalysisHistoryItem, 'id' | 'date'>) => Promise<void>;
  deleteHistoryItem: (id: string) => void;
  clearHistory: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserAccount | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [fontSize, setFontSizeState] = useState<FontSize>('normal');
  const [highContrast, setHighContrastState] = useState<boolean>(false);
  const [reducedMotion, setReducedMotionState] = useState<boolean>(false);
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);

  useEffect(() => {
    // Load persisted settings
    const savedUser = localStorage.getItem('app_user');
    const savedToken = localStorage.getItem('app_token');
    if (savedUser) {
      try {
        const u = JSON.parse(savedUser);
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setUser(u);
        if (savedToken) setToken(savedToken);
      } catch {}
    }

    const savedFontSize = localStorage.getItem('app_fontsize') as FontSize;
    if (savedFontSize) setFontSizeState(savedFontSize);

    const savedContrast = localStorage.getItem('app_highcontrast') === 'true';
    setHighContrastState(savedContrast);

    const savedMotion = localStorage.getItem('app_reducedmotion') === 'true';
    setReducedMotionState(savedMotion);

    const savedHistory = localStorage.getItem('analysis_history');
    if (savedHistory) {
      try {
        const parsed = JSON.parse(savedHistory);
        if (Array.isArray(parsed)) {
          // eslint-disable-next-line react-hooks/set-state-in-effect
          setHistory(parsed);
        }
      } catch {}
    }
  }, []);

  // Sync font size to root HTML element
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('font-size-normal', 'font-size-large', 'font-size-xlarge');
    root.classList.add(`font-size-${fontSize}`);
    localStorage.setItem('app_fontsize', fontSize);
  }, [fontSize]);

  // Sync high contrast
  useEffect(() => {
    const root = document.documentElement;
    if (highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
    localStorage.setItem('app_highcontrast', String(highContrast));
  }, [highContrast]);

  // Sync reduced motion
  useEffect(() => {
    localStorage.setItem('app_reducedmotion', String(reducedMotion));
  }, [reducedMotion]);

  // Real Google Sign-In with prompt and backend verification
  const signInWithGoogle = async () => {
    try {
      // 1. Prompt Google Sign-In / Account Chooser
      const googleUser = await promptGoogleSignIn();

      // 2. Transmit to backend FastAPI /api/auth/google
      const payload = {
        credential: googleUser.idToken || undefined,
        name: googleUser.name,
        email: googleUser.email,
        avatar: googleUser.avatar,
        google_id: googleUser.id,
      };

      const res = await authenticateWithGoogleBackend(payload);
      const authenticatedUser: UserAccount = res?.user || {
        id: googleUser.id,
        name: googleUser.name,
        email: googleUser.email,
        avatar: googleUser.avatar,
        provider: 'google',
      };

      setUser(authenticatedUser);
      setToken(res?.token || `token_${Date.now()}`);
      localStorage.setItem('app_user', JSON.stringify(authenticatedUser));
      if (res?.token) localStorage.setItem('app_token', res.token);

      // 3. Sync user's remote analysis history from backend
      const remoteAnalyses = await fetchUserAnalysesBackend(authenticatedUser.id);
      if (remoteAnalyses && remoteAnalyses.length > 0) {
        setHistory(remoteAnalyses);
        localStorage.setItem('analysis_history', JSON.stringify(remoteAnalyses));
      }
    } catch (e: any) {
      if (e.message !== "Sign in cancelled") {
        console.error("Sign in error:", e);
        alert(`Google Sign-In: ${e.message || 'Authentication could not be completed'}`);
      }
    }
  };

  const signOut = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('app_user');
    localStorage.removeItem('app_token');
  };

  const setFontSize = (size: FontSize) => {
    setFontSizeState(size);
  };

  const setHighContrast = (val: boolean) => {
    setHighContrastState(val);
  };

  const setReducedMotion = (val: boolean) => {
    setReducedMotionState(val);
  };

  const addHistoryItem = async (item: Omit<AnalysisHistoryItem, 'id' | 'date'>) => {
    const newItem: AnalysisHistoryItem = {
      ...item,
      id: `analysis-${Date.now()}`,
      date: new Date().toISOString().split('T')[0],
    };
    const updated = [newItem, ...history];
    setHistory(updated);
    localStorage.setItem('analysis_history', JSON.stringify(updated));

    // Also persist to backend if logged in
    if (user?.id) {
      await saveUserAnalysisBackend(user.id, newItem);
    }
  };

  const deleteHistoryItem = (id: string) => {
    const updated = history.filter((h) => h.id !== id);
    setHistory(updated);
    localStorage.setItem('analysis_history', JSON.stringify(updated));
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('analysis_history');
  };

  return (
    <AppContext.Provider
      value={{
        user,
        token,
        signInWithGoogle,
        signOut,
        fontSize,
        setFontSize,
        highContrast,
        setHighContrast,
        reducedMotion,
        setReducedMotion,
        history,
        addHistoryItem,
        deleteHistoryItem,
        clearHistory,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within an AppProvider');
  return context;
}
