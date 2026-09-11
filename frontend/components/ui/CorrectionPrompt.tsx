'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CorrectionPromptProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (value: string) => void;
  hint: string;
  suggestedValue?: string;
  currentValue: string;
}

export default function CorrectionPrompt({
  isOpen,
  onClose,
  onConfirm,
  hint,
  suggestedValue,
  currentValue,
}: CorrectionPromptProps) {
  const [value, setValue] = useState(currentValue);

  useEffect(() => {
    setValue(currentValue);
  }, [currentValue]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className="w-full max-w-md rounded-3xl border bg-[var(--surface-0)] p-6 shadow-2xl"
            style={{ borderColor: 'var(--border)' }}
          >
            <div className="flex items-start gap-4 mb-6">
              <div className="p-2 rounded-full bg-amber-500/20 text-amber-500">
                <AlertCircle size={24} />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-[var(--text-primary)]">Wait a moment...</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed mt-1">
                  {hint}
                </p>
              </div>
              <button onClick={onClose} className="p-1 rounded-full hover:bg-[var(--surface-1)] text-[var(--text-muted)]">
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4 mb-8">
              <div className="space-y-1">
                <label className="text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">Your value</label>
                <input
                  type="text"
                  value={value}
                  onChange={(e) => setValue(e.target.value)}
                  className="w-full p-3 rounded-xl bg-[var(--surface-1)] border border-[var(--border)] text-[var(--text-primary)] outline-none focus:ring-2 focus:ring-[var(--accent)] transition-all"
                />
              </div>

              {suggestedValue && (
                <button
                  onClick={() => setValue(suggestedValue)}
                  className="w-full p-3 rounded-xl border border-dashed border-[var(--accent)] bg-[var(--accent)]/5 text-[var(--accent-text)] text-sm font-medium hover:bg-[var(--accent)]/10 transition-all flex items-center justify-center gap-2"
                >
                  <CheckCircle2 size={16} />
                  Use suggested value: {suggestedValue}
                </button>
              )}
            </div>

            <div className="flex gap-3">
              <Button variant="outline" onClick={onClose} className="flex-1 rounded-xl">
                Cancel
              </Button>
              <Button variant="primary" onClick={() => onConfirm(value)} className="flex-1 rounded-xl bg-[var(--accent)] text-white font-bold">
                Confirm Corrected Value
              </Button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
