'use client';
import React from 'react';
import { useLanguage } from '@/lib/LanguageContext';
import { motion } from 'framer-motion';

export default function LanguageSwitcher() {
  const { lang, setLang } = useLanguage();

  return (
    <div
      className="flex items-center gap-0.5 p-1 rounded-full border"
      style={{ backgroundColor: 'var(--surface-2)', borderColor: 'var(--border)' }}
    >
      {(['en', 'hi'] as const).map((l) => (
        <button
          key={l}
          onClick={() => setLang(l)}
          className="relative px-3 py-1 text-xs font-semibold uppercase tracking-wider rounded-full transition-colors duration-[var(--duration-base)]"
          style={{
            color: lang === l ? 'var(--surface-0)' : 'var(--text-muted)',
          }}
          aria-label={`Switch to ${l === 'en' ? 'English' : 'Hindi'}`}
        >
          {lang === l && (
            <motion.span
              layoutId="lang-pill"
              className="absolute inset-0 rounded-full"
              style={{ backgroundColor: 'var(--text-primary)' }}
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            />
          )}
          <span className="relative z-10">{l.toUpperCase()}</span>
        </button>
      ))}
    </div>
  );
}
