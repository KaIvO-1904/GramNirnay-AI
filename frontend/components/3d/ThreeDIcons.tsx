'use client';
import React from 'react';
import {
  Lightbulb,
  Coins,
  Target,
  Award,
  MapPin,
  Compass,
  TrendingUp,
  ShieldCheck,
  Building2,
  FileCheck2,
  PieChart,
  Layers,
  Sparkles,
  Zap,
} from 'lucide-react';

interface ThreeDIconProps {
  name:
    | 'idea'
    | 'capital'
    | 'target'
    | 'experience'
    | 'district'
    | 'state'
    | 'growth'
    | 'shield'
    | 'building'
    | 'scheme'
    | 'chart'
    | 'layers'
    | 'sparkles'
    | 'zap';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  variant?: 'blue' | 'indigo' | 'emerald' | 'amber' | 'purple' | 'cyan';
}

const colorMap = {
  blue: {
    bg: 'from-blue-500/20 via-blue-600/10 to-indigo-600/25',
    border: 'border-blue-400/30 dark:border-blue-500/30',
    shadow: 'shadow-[0_8px_20px_rgba(59,130,246,0.25)]',
    iconColor: 'text-blue-600 dark:text-blue-400',
    glow: 'rgba(59, 130, 246, 0.4)',
  },
  indigo: {
    bg: 'from-indigo-500/20 via-indigo-600/10 to-purple-600/25',
    border: 'border-indigo-400/30 dark:border-indigo-500/30',
    shadow: 'shadow-[0_8px_20px_rgba(99,102,241,0.25)]',
    iconColor: 'text-indigo-600 dark:text-indigo-400',
    glow: 'rgba(99, 102, 241, 0.4)',
  },
  emerald: {
    bg: 'from-emerald-500/20 via-teal-600/10 to-green-600/25',
    border: 'border-emerald-400/30 dark:border-emerald-500/30',
    shadow: 'shadow-[0_8px_20px_rgba(16,185,129,0.25)]',
    iconColor: 'text-emerald-600 dark:text-emerald-400',
    glow: 'rgba(16, 185, 129, 0.4)',
  },
  amber: {
    bg: 'from-amber-500/20 via-orange-600/10 to-yellow-600/25',
    border: 'border-amber-400/30 dark:border-amber-500/30',
    shadow: 'shadow-[0_8px_20px_rgba(245,158,11,0.25)]',
    iconColor: 'text-amber-600 dark:text-amber-400',
    glow: 'rgba(245, 158, 11, 0.4)',
  },
  purple: {
    bg: 'from-purple-500/20 via-fuchsia-600/10 to-indigo-600/25',
    border: 'border-purple-400/30 dark:border-purple-500/30',
    shadow: 'shadow-[0_8px_20px_rgba(168,85,247,0.25)]',
    iconColor: 'text-purple-600 dark:text-purple-400',
    glow: 'rgba(168, 85, 247, 0.4)',
  },
  cyan: {
    bg: 'from-cyan-500/20 via-sky-600/10 to-blue-600/25',
    border: 'border-cyan-400/30 dark:border-cyan-500/30',
    shadow: 'shadow-[0_8px_20px_rgba(6,182,212,0.25)]',
    iconColor: 'text-cyan-600 dark:text-cyan-400',
    glow: 'rgba(6, 182, 212, 0.4)',
  },
};

const sizeMap = {
  sm: { box: 'w-8 h-8 rounded-xl', icon: 16 },
  md: { box: 'w-11 h-11 rounded-2xl', icon: 20 },
  lg: { box: 'w-14 h-14 rounded-2xl', icon: 26 },
  xl: { box: 'w-18 h-18 rounded-3xl', icon: 34 },
};

const iconComponents = {
  idea: Lightbulb,
  capital: Coins,
  target: Target,
  experience: Award,
  district: MapPin,
  state: Compass,
  growth: TrendingUp,
  shield: ShieldCheck,
  building: Building2,
  scheme: FileCheck2,
  chart: PieChart,
  layers: Layers,
  sparkles: Sparkles,
  zap: Zap,
};

export default function ThreeDIcon({
  name,
  size = 'md',
  variant = 'blue',
  className = '',
}: ThreeDIconProps) {
  const IconComponent = iconComponents[name] || Sparkles;
  const colors = colorMap[variant] || colorMap.blue;
  const sizes = sizeMap[size] || sizeMap.md;

  return (
    <div
      className={`relative flex items-center justify-center bg-gradient-to-br ${colors.bg} ${colors.border} ${colors.shadow} ${sizes.box} border backdrop-blur-md transition-all duration-300 group-hover:scale-110 ${className}`}
      style={{
        boxShadow: `0 10px 25px -5px ${colors.glow}, inset 0 1px 1px rgba(255,255,255,0.6)`,
      }}
    >
      {/* Metallic specular rim highlight */}
      <div className="absolute inset-0 rounded-[inherit] bg-gradient-to-t from-transparent via-white/10 to-white/40 pointer-events-none opacity-80" />

      {/* Center 3D glowing icon */}
      <IconComponent
        size={sizes.icon}
        className={`${colors.iconColor} drop-shadow-[0_2px_8px_${colors.glow}] relative z-10 transition-transform duration-300 group-hover:rotate-6`}
        strokeWidth={2.2}
      />
    </div>
  );
}
