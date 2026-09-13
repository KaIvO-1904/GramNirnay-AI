'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { Language } from '@/lib/i18n';

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  voicePreference: 'male' | 'female';
  setVoicePreference: (pref: 'male' | 'female') => void;
}

export const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Language>('en-US');
  const [voicePreference, setVoicePreferenceState] = useState<'male' | 'female'>('female');

  useEffect(() => {
    const savedLang = localStorage.getItem('app_lang') as Language;
    if (savedLang && (savedLang === 'en-US' || savedLang === 'hi-IN' || savedLang === 'kn-IN')) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setLangState(savedLang);
    }
    const savedVoice = localStorage.getItem('app_voice_pref') as 'male' | 'female';
    if (savedVoice === 'male' || savedVoice === 'female') {
      setVoicePreferenceState(savedVoice);
    }
  }, []);

  const setLang = (newLang: Language) => {
    setLangState(newLang);
    localStorage.setItem('app_lang', newLang);
  };

  const setVoicePreference = (pref: 'male' | 'female') => {
    setVoicePreferenceState(pref);
    localStorage.setItem('app_voice_pref', pref);
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, voicePreference, setVoicePreference }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used within a LanguageProvider');
  return context;
}
