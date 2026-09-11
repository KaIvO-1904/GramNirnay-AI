'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, HelpCircle } from 'lucide-react';
import { DemoBadge } from './DemoBadge';

interface ViabilityExplanationProps {
  explanation: string;
  score: number;
  isDemo?: boolean;
}

export default function ViabilityExplanation({ explanation, score, isDemo = false }: ViabilityExplanationProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full p-6 rounded-3xl border bg-[var(--surface-0)] border-[var(--border)] shadow-sm relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <Sparkles size={64} className="text-[var(--accent)]" />
      </div>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-indigo-500/20 text-indigo-500">
            <HelpCircle size={20} />
          </div>
          <h3 className="text-lg font-bold tracking-tight text-[var(--text-primary)]">
            Why this viability score?
          </h3>
        </div>
        <DemoBadge visible={isDemo} />
      </div>

      <div className="space-y-4">
        <p className="text-sm sm:text-base leading-relaxed text-[var(--text-secondary)]">
          {explanation}
        </p>

        <div className="flex items-center gap-4 pt-4 border-t border-[var(--border)]">
          <div className="flex flex-col">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-muted)]">
              Current Verdict
            </span>
            <span className="text-sm font-bold text-[var(--text-primary)]">
              {score > 80 ? 'High Potential' : score > 60 ? 'Viable with Adjustments' : 'High Risk'}
            </span>
          </div>
          <div className="h-8 w-px bg-[var(--border)]" />
          <div className="flex flex-col">
            <span className="text-[10px] font-bold uppercase tracking-widest text-[var(--text-muted)]">
              Confidence
            </span>
            <span className="text-sm font-bold text-[var(--text-primary)]">
              {score > 80 ? 'High' : 'Medium'}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
