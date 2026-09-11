'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Info } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: number;
  label?: string;
  className?: string;
}

export default function ConfidenceBadge({ confidence, label = 'Confidence', className = '' }: ConfidenceBadgeProps) {
  const getVariant = (conf: number) => {
    if (conf >= 0.8) return { color: 'var(--success)', text: 'High' };
    if (conf >= 0.5) return { color: 'var(--warning)', text: 'Medium' };
    return { color: 'var(--danger)', text: 'Low' };
  };

  const { color, text } = getVariant(confidence);

  return (
    <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-opacity-10 transition-all ${className}`}
         style={{ backgroundColor: `${color}20`, color: color }}>
      <Info size={10} />
      <span className="text-[10px] font-bold uppercase tracking-wider">{label}: {text} ({Math.round(confidence * 100)}%)</span>
    </div>
  );
}
