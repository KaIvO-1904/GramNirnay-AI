import React from 'react';
import { motion } from 'framer-motion';
import Card3DTilt from '@/components/3d/Card3DTilt';
import ThreeDIcon from '@/components/3d/ThreeDIcons';
import ConfidenceBadge from './ConfidenceBadge';
import { DemoBadge } from './DemoBadge';

interface LocalIntelligenceCardProps {
  title: string;
  value: string;
  evidence: string;
  iconName: any;
  variant: any;
  confidence: number;
  isDemo?: boolean;
}

export default function LocalIntelligenceCard({
  title,
  value,
  evidence,
  iconName,
  variant,
  confidence,
  isDemo = false,
}: LocalIntelligenceCardProps) {
  return (
    <Card3DTilt intensity={1.5} glareOpacity={0.05}>
      <div
        className="h-full p-6 rounded-3xl border backdrop-blur-md relative overflow-hidden shadow-sm transition-all group"
        style={{
          backgroundColor: 'var(--surface-0)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="flex items-start justify-between mb-6">
          <ThreeDIcon name={iconName} variant={variant} size="md" />
          <div className="flex flex-col items-end gap-2">
            <ConfidenceBadge confidence={confidence} />
            <DemoBadge visible={isDemo} />
          </div>
        </div>

        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-widest text-[var(--text-muted)]">
            {title}
          </h3>
          <div className="text-2xl font-black tracking-tight text-[var(--text-primary)] leading-tight">
            {value}
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-[var(--border)]">
          <p className="text-[11px] italic text-[var(--text-secondary)] flex items-center gap-1.5">
            <span className="font-bold uppercase text-[9px] opacity-60">Source:</span> {evidence}
          </p>
        </div>
      </div>
    </Card3DTilt>
  );
}
