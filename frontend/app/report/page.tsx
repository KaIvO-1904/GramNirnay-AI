'use client';
import React, { useEffect, useState, useMemo, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import {
  calculateEMI,
  calculateBreakEven,
  calculateROI,
  calculateSubsidyBenefit,
  calculateCapitalEfficiency
} from '@/lib/financials';
import { useLanguage } from '@/lib/LanguageContext';
import { t } from '@/lib/i18n';
import { AnalysisResult, Scheme } from '@/types';
import { Reveal, Stagger, HoverLift, FadeIn } from '@/components/motion';
import Card3DTilt from '@/components/3d/Card3DTilt';
import ThreeDIcon from '@/components/3d/ThreeDIcons';
import {
  ArrowLeft, TrendingUp, AlertTriangle, ShieldCheck,
  CheckCircle, ExternalLink, Zap, Target, Rocket,
  DollarSign, Activity, LayoutDashboard
} from 'lucide-react';

/* ─────────────────────────────────────────
   Animated counter hook
───────────────────────────────────────── */
function useAnimatedNumber(target: number, duration = 900) {
  const [value, setValue] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (!isInView) return;
    let start: number | null = null;
    const step = (ts: number) => {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, isInView]);

  return { value, ref };
}

/* ─────────────────────────────────────────
   UI Components
───────────────────────────────────────── */

function HealthPulse({ score, recommendation }: { score: number; recommendation: string }) {
  const { value, ref } = useAnimatedNumber(score, 1200);

  const status = {
    'Proceed': { color: 'var(--success)', label: 'Ready for Launch', icon: <CheckCircle size={18} /> },
    'Proceed with Modification': { color: 'var(--warning)', label: 'Strategic Pivot Needed', icon: <AlertTriangle size={18} /> },
    'Reconsider': { color: 'var(--danger)', label: 'High Risk', icon: <ShieldCheck size={18} /> },
  }[recommendation] || { color: 'var(--border)', label: 'Evaluating', icon: <Activity size={18} /> };

  return (
    <div className="flex flex-col md:flex-row items-center gap-8 p-6 rounded-3xl border shadow-sm backdrop-blur-md"
         style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }} ref={ref}>
      <div className="relative w-32 h-32 flex items-center justify-center">
        <svg width="120" height="120" className="rotate-[-90deg]">
          <circle cx="60" cy="60" r="50" fill="none" stroke="var(--surface-3)" strokeWidth="12" />
          <motion.circle
            cx="60" cy="60" r="50" fill="none" stroke={status.color} strokeWidth="12" strokeLinecap="round"
            strokeDasharray={2 * Math.PI * 50}
            initial={{ strokeDashoffset: 2 * Math.PI * 50 }}
            animate={{ strokeDashoffset: (2 * Math.PI * 50) * (1 - value / 100) }}
            transition={{ duration: 1.5, ease: [0.16, 1, 0.3, 1] }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-black font-mono">{value}</span>
          <span className="text-[10px] font-bold uppercase opacity-50">Score</span>
        </div>
      </div>
      <div className="flex flex-col items-center md:items-start gap-2">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider"
             style={{ backgroundColor: `${status.color}20`, color: status.color }}>
          {status.icon}
          {status.label}
        </div>
        <h2 className="text-2xl font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
          Business Viability Analysis
        </h2>
        <p className="text-sm opacity-70 max-w-md">
          {recommendation === 'Proceed'
            ? 'Strong market indicators and financial health. Ideal for immediate implementation.'
            : recommendation === 'Proceed with Modification'
            ? 'Viable potential, but requires strategic adjustments to reduce risk.'
            : 'Significant risks detected. We recommend pivoting the model before investing capital.'}
        </p>
      </div>
    </div>
  );
}

function LiveGauge({ label, value, unit = '', threshold = 0, inverse = false }: { label: string; value: number; unit?: string; threshold?: number; inverse?: boolean }) {
  const isCritical = inverse ? value > threshold : value < threshold;
  const color = isCritical ? 'var(--danger)' : 'var(--success)';

  return (
    <div className="p-4 rounded-2xl border transition-all hover:shadow-sm"
         style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }}>
      <div className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-50">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-black font-mono" style={{ color }}>{value.toLocaleString()}</span>
        <span className="text-xs font-bold opacity-50">{unit}</span>
      </div>
    </div>
  );
}

function FundingBridge({ totalCost, userCapital, schemes }: { totalCost: number, userCapital: number, schemes: Scheme[] }) {
  const bestScheme = schemes[0] || { benefit: { subsidyPercent: 0 } };
  const subsidyAmount = calculateSubsidyBenefit(totalCost, bestScheme.benefit.subsidyPercent);
  const loanRequired = Math.max(0, totalCost - userCapital - subsidyAmount);

  const total = totalCost || 1;
  const userPct = (userCapital / total) * 100;
  const subsidyPct = (subsidyAmount / total) * 100;
  const loanPct = (loanRequired / total) * 100;

  return (
    <div className="p-6 rounded-3xl border shadow-sm" style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }}>
      <div className="flex items-center gap-2 mb-4">
        <DollarSign size={16} style={{ color: 'var(--accent)' }} />
        <h3 className="text-sm font-bold uppercase tracking-wider">Funding Bridge</h3>
      </div>
      <div className="h-4 w-full rounded-full overflow-hidden flex mb-6" style={{ backgroundColor: 'var(--surface-2)' }}>
        <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${userPct}%` }} title="User Capital" />
        <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: `${subsidyPct}%` }} title="Subsidy" />
        <div className="h-full bg-amber-500 transition-all duration-500" style={{ width: `${loanPct}%` }} title="Loan" />
      </div>
      <div className="space-y-2">
        <div className="flex justify-between text-xs">
          <span className="opacity-60">User Capital</span>
          <span className="font-mono font-bold">₹{userCapital.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="opacity-60">Best Subsidy ({bestScheme.benefit.subsidyPercent}%)</span>
          <span className="font-mono font-bold text-emerald-500">₹{subsidyAmount.toLocaleString()}</span>
        </div>
        <div className="flex justify-between text-xs border-t pt-2 mt-2">
          <span className="font-bold">Total Loan Needed</span>
          <span className="font-mono font-black text-amber-500">₹{loanRequired.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────
   Main Report Page
───────────────────────────────────────── */
type ScenarioPreset = 'conservative' | 'base' | 'optimistic';

export default function ReportPage() {
  const { lang } = useLanguage();
  const router = useRouter();
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [activePreset, setActivePreset] = useState<ScenarioPreset>('base');
  const [levers, setLevers] = useState({
    leanMode: false,
    growthMode: false,
    appliedSubsidy: false,
  });
  const [sandbox, setSandbox] = useState({
    setupCost: 0,
    monthlyRevenue: 0,
    monthlyExpenses: 0,
    loanAmount: 0,
    interestRate: 9,
    tenureYears: 5,
  });

  useEffect(() => {
    const stored = localStorage.getItem('analysis_result');
    const demo = localStorage.getItem('demo_data');
    const source = stored || demo;
    if (source) {
      try {
        const parsed: AnalysisResult = JSON.parse(source);
        setData(parsed);
        const fin = parsed.financials;
        setSandbox({
          setupCost: fin.total_project_cost || 0,
          monthlyRevenue: fin.monthly_revenue || 0,
          monthlyExpenses: fin.monthly_expenses || 0,
          loanAmount: fin.financing_required || 0,
          interestRate: 9,
          tenureYears: 5,
        });
      } catch { router.push('/'); }
    } else { router.push('/'); }
  }, [router]);

  const effectiveSandbox = useMemo(() => {
    let revMult = 1, expMult = 1, costMult = 1;
    if (activePreset === 'conservative') { revMult = 0.85; expMult = 1.1; }
    if (activePreset === 'optimistic') { revMult = 1.15; expMult = 0.9; }

    // Strategic Levers
    if (levers.leanMode) costMult = 0.85;
    if (levers.growthMode) revMult *= 1.2;

    const bestScheme = data?.matchedSchemes?.[0];
    const subsidyPercent = bestScheme?.benefit.subsidyPercent || 0;
    const subsidyAmount = levers.appliedSubsidy ? calculateSubsidyBenefit(sandbox.setupCost, subsidyPercent) : 0;

    return {
      ...sandbox,
      setupCost: (sandbox.setupCost * costMult) - subsidyAmount,
      monthlyRevenue: sandbox.monthlyRevenue * revMult,
      monthlyExpenses: sandbox.monthlyExpenses * expMult,
    };
  }, [sandbox, activePreset, levers, data]);

  const emi = calculateEMI(effectiveSandbox.loanAmount, effectiveSandbox.interestRate, effectiveSandbox.tenureYears);
  const breakEven = calculateBreakEven(effectiveSandbox.setupCost, effectiveSandbox.monthlyRevenue, effectiveSandbox.monthlyExpenses + emi);
  const monthlyNet = effectiveSandbox.monthlyRevenue - effectiveSandbox.monthlyExpenses - emi;
  const annualProfit = monthlyNet * 12;
  const roi = calculateROI(annualProfit, effectiveSandbox.setupCost);

  const chartData = Array.from({ length: 12 }, (_, i) => ({
    month: `Mo ${i + 1}`,
    cash: Math.round(monthlyNet * (i + 1)),
  }));

  if (!data) return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--surface-1)', color: 'var(--text-primary)' }}>
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-full border-3 border-t-[var(--accent)] animate-spin" style={{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }} />
        <p className="text-sm font-medium opacity-60">Analyzing venture viability...</p>
      </div>
    </div>
  );

  const sandboxSliders = [
    { label: 'Project Cost', key: 'setupCost', min: 10000, max: 5000000, step: 10000 },
    { label: 'Monthly Revenue', key: 'monthlyRevenue', min: 5000, max: 500000, step: 1000 },
    { label: 'Monthly Expenses', key: 'monthlyExpenses', min: 1000, max: 200000, step: 1000 },
    { label: 'Funding (Loan)', key: 'loanAmount', min: 0, max: 5000000, step: 10000 },
  ] as const;

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--surface-1)', color: 'var(--text-primary)' }}>
      <div className="pointer-events-none fixed inset-0 opacity-20" style={{ backgroundImage: 'url(/media/grid-pattern.svg)', backgroundSize: '280px 280px', backgroundRepeat: 'repeat' }} />

      <div className="relative z-10 max-w-[1400px] mx-auto px-4 sm:px-6 md:px-10 pt-24 pb-20">

        {/* ── TOP NAVIGATION ── */}
        <div className="flex justify-between items-center mb-10">
          <div className="flex items-center gap-3">
            <ThreeDIcon name="chart" size="sm" variant="blue" />
            <h1 className="text-xl font-black tracking-tight uppercase">{t(lang, 'report.title')}</h1>
          </div>
          <Button variant="outline" onClick={() => router.push('/')} className="gap-2 rounded-2xl">
            <ArrowLeft size={16} />
            New Analysis
          </Button>
        </div>

        {/* ── VENTURE HEALTH PULSE ── */}
        <Reveal>
          <HealthPulse score={data.viabilityScore} recommendation={data.recommendation} />
        </Reveal>

        {/* ── MAIN DASHBOARD GRID ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-10">

          {/* COLUMN 1: The Command Center */}
          <div className="lg:col-span-3 space-y-6">
            <div className="flex items-center gap-2 mb-2">
              <Activity size={16} style={{ color: 'var(--accent)' }} />
              <h3 className="text-xs font-bold uppercase tracking-widest opacity-60">KPI Command Center</h3>
            </div>
            <Stagger stagger={0.1}>
              <LiveGauge label="Annual ROI" value={roi} unit="%" threshold={15} />
              <LiveGauge label="Break-even" value={breakEven} unit="Mo" threshold={36} inverse />
              <LiveGauge label="Monthly Net" value={monthlyNet} unit="₹" threshold={5000} />
              <LiveGauge label="Debt Burden" value={(emi / effectiveSandbox.monthlyRevenue) * 100 || 0} unit="%" threshold={40} inverse />
            </Stagger>
            <FundingBridge totalCost={effectiveSandbox.setupCost} userCapital={sandbox.loanAmount} schemes={data.matchedSchemes} />
          </div>

          {/* COLUMN 2: The Strategy Simulator */}
          <div className="lg:col-span-6 space-y-8">
            <Reveal>
              <Card3DTilt intensity={1.2}>
                <div className="p-8 rounded-3xl border shadow-md backdrop-blur-xl" style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }}>
                  <div className="flex justify-between items-center mb-8">
                    <div>
                      <h2 className="text-2xl font-black tracking-tight flex items-center gap-2">
                        <Rocket size={24} style={{ color: 'var(--accent)' }} />
                        Strategy Simulator
                      </h2>
                      <p className="text-xs opacity-60">Simulate strategic levers to optimize viability.</p>
                    </div>
                    <div className="flex p-1 rounded-2xl border gap-0.5 bg-var(--surface-1)">
                      {(['conservative', 'base', 'optimistic'] as ScenarioPreset[]).map((p) => (
                        <button
                          key={p}
                          onClick={() => setActivePreset(p)}
                          className="relative px-3 py-1 text-[10px] font-bold uppercase rounded-xl transition-colors capitalize cursor-pointer"
                          style={{ color: activePreset === p ? 'var(--surface-0)' : 'var(--text-muted)' }}
                        >
                          {activePreset === p && (
                            <motion.span layoutId="preset-pill" className="absolute inset-0 rounded-xl" style={{ backgroundColor: 'var(--text-primary)' }} />
                          )}
                          <span className="relative z-10">{p}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Strategic Levers */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
                    <LeverToggle
                      label="Govt Subsidy"
                      active={levers.appliedSubsidy}
                      onClick={() => setLevers(l => ({...l, appliedSubsidy: !l.appliedSubsidy}))}
                      icon={<DollarSign size={14} />}
                    />
                    <LeverToggle
                      label="Lean Startup"
                      active={levers.leanMode}
                      onClick={() => setLevers(l => ({...l, leanMode: !l.leanMode}))}
                      icon={<Zap size={14} />}
                    />
                    <LeverToggle
                      label="Aggressive Growth"
                      active={levers.growthMode}
                      onClick={() => setLevers(l => ({...l, growthMode: !l.growthMode}))}
                      icon={<TrendingUp size={14} />}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                    <div className="space-y-6">
                      {sandboxSliders.map((ctrl) => (
                        <div key={ctrl.key} className="space-y-2">
                          <div className="flex justify-between text-[11px] font-bold uppercase opacity-60">
                            <span>{ctrl.label}</span>
                            <span className="font-mono" style={{ color: 'var(--accent-text)' }}>
                              ₹{Math.round(sandbox[ctrl.key]).toLocaleString()}
                            </span>
                          </div>
                          <Slider
                            value={[sandbox[ctrl.key] as number]}
                            min={ctrl.min} max={ctrl.max} step={ctrl.step}
                            onValueChange={(val) => setSandbox({ ...sandbox, [ctrl.key]: val[0] })}
                          />
                        </div>
                      ))}
                    </div>
                    <div className="flex flex-col gap-6">
                      <div className="h-48 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                            <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v / 1000}k`} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" dataKey="cash" name="Cumulative Cash" stroke="var(--accent)" strokeWidth={3} dot={false} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="p-4 rounded-2xl border bg-var(--surface-1) text-center">
                        <div className="text-[10px] font-bold uppercase opacity-50 mb-1">Projected Break-even</div>
                        <div className="text-3xl font-black font-mono" style={{ color: 'var(--accent)' }}>
                          {breakEven === 999 ? 'Never' : `${Math.round(breakEven)} Mo`}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card3DTilt>
            </Reveal>

            {/* Execution Roadmap */}
            <Reveal delay={0.1}>
              <div className="p-8 rounded-3xl border shadow-sm" style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-2 mb-6">
                  <Target size={20} style={{ color: 'var(--accent)' }} />
                  <h3 className="text-lg font-black tracking-tight">Execution Roadmap</h3>
                </div>
                <div className="space-y-4">
                  {data.modifications.length > 0 ? (
                    data.modifications.map((mod, i) => (
                      <div key={i} className="group flex items-start gap-4 p-4 rounded-2xl border transition-all hover:bg-var(--surface-1) cursor-pointer" style={{ borderColor: 'var(--border)' }}>
                        <div className="w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 group-hover:bg-var(--accent) group-hover:border-var(--accent) transition-colors">
                          <div className="w-2 h-2 rounded-full bg-transparent group-hover:bg-white" />
                        </div>
                        <span className="text-sm leading-relaxed opacity-80 group-hover:opacity-100">{mod}</span>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm italic opacity-50">No specific strategic pivots recommended.</p>
                  )}
                </div>
              </div>
            </Reveal>
          </div>

          {/* COLUMN 3: Market Intelligence */}
          <div className="lg:col-span-3 space-y-6">
            <div className="flex items-center gap-2 mb-2">
              <LayoutDashboard size={16} style={{ color: 'var(--accent)' }} />
              <h3 className="text-xs font-bold uppercase tracking-widest opacity-60">Market Intelligence</h3>
            </div>
            <Reveal>
              <div className="grid grid-cols-1 gap-4">
                <IntelSection title="Demand" value={data.marketAnalysis.demand} variant="emerald" icon={<TrendingUp size={14} />} evidence={data.marketAnalysis.source} />
                <IntelSection title="Competition" value={data.marketAnalysis.competition} variant="rose" icon={<ShieldCheck size={14} />} evidence={data.marketAnalysis.source} />
                <IntelSection title="Accessibility" value={data.marketAnalysis.accessibility} variant="blue" icon={<Rocket size={14} />} evidence={data.marketAnalysis.source} />
                <IntelSection title="Seasonality" value={data.marketAnalysis.seasonality} variant="amber" icon={<Activity size={14} />} evidence={data.marketAnalysis.source} />
              </div>
            </Reveal>
            <div className="p-6 rounded-3xl border shadow-sm backdrop-blur-md" style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }}>
              <div className="text-xs font-bold uppercase mb-3 opacity-60">Analyst's Perspective</div>
              <p className="text-xs leading-relaxed opacity-80 italic">
                "{data.interpreter_reasoning || 'Based on regional benchmarks and projected market demand.'}"
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────
   Sub-components
───────────────────────────────────────── */

function LeverToggle({ label, active, onClick, icon }: { label: string, active: boolean, onClick: () => void, icon: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center gap-2 p-3 rounded-2xl border transition-all font-bold text-[11px] uppercase tracking-wider ${
        active ? 'shadow-md' : 'opacity-60'
      }`}
      style={{
        backgroundColor: active ? 'var(--accent)' : 'var(--surface-1)',
        borderColor: active ? 'var(--accent)' : 'var(--border)',
        color: active ? 'var(--surface-0)' : 'var(--text-primary)'
      }}
    >
      {icon}
      {label}
    </button>
  );
}

function IntelSection({ title, value, variant, icon, evidence }: { title: string, value: number, variant: string, icon: React.ReactNode, evidence: string }) {
  const colors = {
    emerald: 'var(--success)',
    rose: 'var(--danger)',
    blue: 'var(--accent)',
    amber: 'var(--warning)',
  };

  return (
    <div className="p-4 rounded-2xl border transition-all hover:shadow-sm" style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest opacity-60">
          {icon}
          {title}
        </div>
        <span className="text-lg font-black font-mono" style={{ color: colors[variant as keyof typeof colors] }}>
          {value}%
        </span>
      </div>
      <div className="text-[10px] opacity-50 truncate italic">Source: {evidence}</div>
    </div>
  );
}

function CustomTooltip ({ active, payload, label }: { active?: boolean, payload?: any[], label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border p-3 text-xs shadow-xl backdrop-blur-md" style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border-strong)', color: 'var(--text-primary)' }}>
      <p className="font-bold mb-1 opacity-60">{label}</p>
      {payload.map((p: any) => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
          <span className="opacity-60">{p.name}:</span>
          <span className="font-bold font-mono">₹{p.value?.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
}
