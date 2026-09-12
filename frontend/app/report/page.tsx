'use client';
import React, { useEffect, useState, useMemo, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, useInView } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { calculateEMI, calculateBreakEven, calculateROI } from '@/lib/financials';
import { useLanguage } from '@/lib/LanguageContext';
import { t } from '@/lib/i18n';
import { AnalysisResult, Scheme } from '@/types';
import { Reveal, Stagger, HoverLift, FadeIn } from '@/components/motion';
import Card3DTilt from '@/components/3d/Card3DTilt';
import ThreeDIcon from '@/components/3d/ThreeDIcons';
import LocalIntelligenceCard from '@/components/ui/LocalIntelligenceCard';
import ViabilityExplanation from '@/components/ui/ViabilityExplanation';
import { ArrowLeft, ArrowRight, TrendingUp, AlertTriangle, ShieldCheck, CheckCircle, ExternalLink } from 'lucide-react';

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
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setValue(Math.round(eased * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, isInView]);

  return { value, ref };
}

/* ─────────────────────────────────────────
   Animated Viability Score Ring
───────────────────────────────────────── */
function ViabilityRing({ score, recommendation }: { score: number; recommendation: string }) {
  const { value, ref } = useAnimatedNumber(score, 1200);
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDash = (score / 100) * circumference;

  const color =
    recommendation === 'Proceed'
      ? 'var(--success)'
      : recommendation === 'Proceed with Modification'
      ? 'var(--warning)'
      : 'var(--danger)';

  const badgeVariant =
    recommendation === 'Proceed'
      ? ('success' as const)
      : recommendation === 'Proceed with Modification'
      ? ('warning' as const)
      : ('danger' as const);

  return (
    <div className="flex flex-col items-center gap-4 py-2" ref={ref}>
      <div className="relative w-40 h-40 flex items-center justify-center">
        {/* Track */}
        <svg width="150" height="150" className="rotate-[-90deg]">
          <circle
            cx="75" cy="75" r={radius}
            fill="none"
            stroke="var(--surface-3)"
            strokeWidth="10"
          />
          <motion.circle
            cx="75" cy="75" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - strokeDash }}
            transition={{ duration: 1.2, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-black tracking-tighter font-mono" style={{ color: 'var(--text-primary)' }}>
            {value}
          </span>
          <span className="text-xs font-bold" style={{ color: 'var(--text-muted)' }}>/100</span>
        </div>
      </div>
      <Badge variant={badgeVariant} className="text-xs px-4 py-1 font-bold uppercase tracking-wider shadow-sm">
        {recommendation}
      </Badge>
    </div>
  );
}

/* ─────────────────────────────────────────
   Metric tile
───────────────────────────────────────── */
function MetricTile({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div
      className="p-4 rounded-2xl border flex flex-col gap-1 shadow-xs transition-all hover:shadow-sm"
      style={{
        backgroundColor: accent ? 'var(--accent-subtle)' : 'var(--surface-1)',
        borderColor: accent ? 'color-mix(in srgb, var(--accent) 25%, transparent)' : 'var(--border)',
      }}
    >
      <div className="text-[10px] font-bold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>
        {label}
      </div>
      <div
        className="text-xl font-black tracking-tight font-mono"
        style={{ color: accent ? 'var(--accent-text)' : 'var(--text-primary)' }}
      >
        {value}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────
   Custom recharts tooltip
───────────────────────────────────────── */
interface TooltipPayloadEntry {
  name: string;
  value?: number;
  color: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="rounded-xl border p-3 text-xs shadow-xl backdrop-blur-md"
      style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border-strong)', color: 'var(--text-primary)' }}
    >
      <p className="font-bold mb-1" style={{ color: 'var(--text-secondary)' }}>{label}</p>
      {payload.map((p) => (
        <div key={p.name} className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
          <span style={{ color: 'var(--text-secondary)' }}>{p.name}:</span>
          <span className="font-bold font-mono">₹{p.value?.toLocaleString()}</span>
        </div>
      ))}
    </div>
  );
};

/* ─────────────────────────────────────────
   Main Report Page
───────────────────────────────────────── */
type ScenarioPreset = 'conservative' | 'base' | 'optimistic';

export default function ReportPage() {
  const { lang } = useLanguage();
  const router = useRouter();
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [activePreset, setActivePreset] = useState<ScenarioPreset>('base');
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
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setData(parsed);
        const fin = parsed.financials;
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setSandbox({
          setupCost: fin.total_project_cost || 0,
          monthlyRevenue: fin.monthly_revenue || 0,
          monthlyExpenses: fin.monthly_expenses || 0,
          loanAmount: fin.financing_required || 0,
          interestRate: 9,
          tenureYears: 5,
        });
      } catch {
        router.push('/');
      }
    } else {
      router.push('/');
    }
  }, [router]);

  const effectiveSandbox = useMemo(() => {
    let revMult = 1, expMult = 1;
    if (activePreset === 'conservative') { revMult = 0.85; expMult = 1.1; }
    if (activePreset === 'optimistic') { revMult = 1.15; expMult = 0.9; }
    return {
      ...sandbox,
      monthlyRevenue: sandbox.monthlyRevenue * revMult,
      monthlyExpenses: sandbox.monthlyExpenses * expMult,
    };
  }, [sandbox, activePreset]);

  const emi = calculateEMI(effectiveSandbox.loanAmount, effectiveSandbox.interestRate, effectiveSandbox.tenureYears);
  const breakEven = calculateBreakEven(effectiveSandbox.setupCost, effectiveSandbox.monthlyRevenue, effectiveSandbox.monthlyExpenses + emi);
  const monthlyNet = effectiveSandbox.monthlyRevenue - effectiveSandbox.monthlyExpenses - emi;
  const annualProfit = monthlyNet * 12;
  const roi = calculateROI(annualProfit, effectiveSandbox.setupCost);

  const chartData = Array.from({ length: 12 }, (_, i) => ({
    month: `Mo ${i + 1}`,
    profit: Math.round(monthlyNet),
    cash: Math.round(monthlyNet * (i + 1)),
  }));

  const deriveRisks = () => {
    const risks: { label: string; impact: 'High' | 'Medium'; note: string }[] = [];
    if (breakEven > 36)
      risks.push({ label: 'Long Payback Period', impact: 'High', note: 'Break-even exceeds 3 years, increasing capital risk.' });
    if (effectiveSandbox.monthlyRevenue > 0 && monthlyNet / effectiveSandbox.monthlyRevenue < 0.15)
      risks.push({ label: 'Low Profit Margin', impact: 'Medium', note: 'Thin margins make the business sensitive to cost increases.' });
    if (effectiveSandbox.setupCost > 0 && effectiveSandbox.loanAmount / effectiveSandbox.setupCost > 0.7)
      risks.push({ label: 'High Debt Reliance', impact: 'Medium', note: 'Heavy reliance on external funding increases monthly EMI pressure.' });
    if (data?.marketAnalysis.competition !== undefined && data.marketAnalysis.competition > 70)
      risks.push({ label: 'Market Saturation', impact: 'High', note: 'High local competition may compress pricing and revenue.' });
    return risks;
  };

  if (!data) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: 'var(--surface-1)', color: 'var(--text-primary)' }}
      >
        <div className="flex flex-col items-center gap-4">
          <div
            className="w-12 h-12 rounded-full border-3 border-t-[var(--accent)] animate-spin"
            style={{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }}
          />
          <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Loading analysis…</p>
        </div>
      </div>
    );
  }

  const confMap: Record<string, number> = { High: 0.95, Medium: 0.75, Low: 0.5 };
  const marketConfidence = confMap[data.marketAnalysis.confidence] || 0.6;

  const sandboxSliders = [
    { label: 'Total Project Cost', key: 'setupCost', min: 10000, max: 5000000, step: 10000 },
    { label: 'Estimated Monthly Revenue', key: 'monthlyRevenue', min: 5000, max: 500000, step: 1000 },
    { label: 'Fixed Monthly Expenses', key: 'monthlyExpenses', min: 1000, max: 200000, step: 1000 },
    { label: 'Funding Required (Loan)', key: 'loanAmount', min: 0, max: 5000000, step: 10000 },
  ] as const;

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: 'var(--surface-1)', color: 'var(--text-primary)' }}
    >
      {/* Background */}
      <div
        className="pointer-events-none fixed inset-0 opacity-20"
        aria-hidden="true"
        style={{
          backgroundImage: 'url(/media/grid-pattern.svg)',
          backgroundSize: '280px 280px',
          backgroundRepeat: 'repeat',
          color: 'var(--border)',
        }}
      />

      <div className="relative z-10 max-w-[1240px] mx-auto px-4 sm:px-6 md:px-10 pt-24 pb-20">

        {/* ── HEADER ── */}
        <FadeIn y={-16} duration={0.5} className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10">
          <div>
            <div
              className="text-xs font-bold uppercase tracking-widest mb-1.5 flex items-center gap-2"
              style={{ color: 'var(--accent-text)' }}
            >
              <ThreeDIcon name="chart" size="sm" variant="blue" />
              <span>Business Intelligence Report</span>
            </div>
            <h1
              className="text-3xl sm:text-4xl md:text-5xl font-black tracking-tight mb-1"
              style={{ color: 'var(--text-primary)' }}
            >
              {t(lang, 'report.title')}
            </h1>
            <p className="text-base font-medium" style={{ color: 'var(--text-secondary)' }}>
              {t(lang, 'report.subtitle')}
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => router.push('/')}
            className="gap-2 shrink-0 rounded-2xl"
          >
            <ArrowLeft size={16} />
            {t(lang, 'report.new_analysis')}
          </Button>
        </FadeIn>

        {/* Divider */}
        <div className="mb-10 h-px" style={{ backgroundColor: 'var(--border)' }} />

        {/* ── MAIN GRID ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* ── LEFT COLUMN ── */}
          <div className="lg:col-span-4 space-y-6">

            {/* Viability Score Card with Subtle Micro-Elevation */}
            <Reveal>
              <Card3DTilt intensity={1.5} glareOpacity={0.05}>
                <div
                  className="p-7 rounded-3xl border text-center shadow-sm backdrop-blur-xl"
                  style={{
                    backgroundColor: 'var(--surface-0)',
                    borderColor: 'var(--border)',
                  }}
                >
                  <div
                    className="text-[11px] font-bold uppercase tracking-widest mb-3"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    Overall Viability Score
                  </div>
                  <ViabilityRing score={data.viabilityScore} recommendation={data.recommendation} />
                  <p
                    className="mt-4 text-xs sm:text-sm leading-relaxed"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    {data.recommendation === 'Proceed'
                      ? 'Strong indicators suggest this venture is viable.'
                      : data.recommendation === 'Proceed with Modification'
                      ? 'Viable, provided certain strategic adjustments are made.'
                      : 'Current analysis indicates high risk; reconsider business model.'}
                  </p>
                </div>
              </Card3DTilt>
            </Reveal>

            {/* Quick Metrics */}
            <Reveal delay={0.05}>
              <Stagger stagger={0.07} className="grid grid-cols-2 gap-3">
                <MetricTile label="Annual ROI" value={`${roi.toFixed(1)}%`} accent />
                <MetricTile
                  label="Break-even"
                  value={breakEven === 999 ? 'Never' : `${Math.round(breakEven)} Mo`}
                />
                <MetricTile
                  label="Monthly Net"
                  value={`₹${Math.round(monthlyNet).toLocaleString()}`}
                />
                <MetricTile
                  label="Debt Burden"
                  value={`${Math.round((emi / effectiveSandbox.monthlyRevenue) * 100 || 0)}%`}
                />
              </Stagger>
            </Reveal>

            {/* Analyst Note */}
            <Reveal delay={0.1}>
              <ViabilityExplanation
                explanation={data.interpreter_reasoning || 'Analysis based on regional benchmarks and projected market demand.'}
                score={data.viabilityScore}
              />
            </Reveal>
          </div>

          {/* ── RIGHT COLUMN ── */}
          <div className="lg:col-span-8 space-y-8">

            {/* Local Intelligence Insights */}
            <Reveal>
              <div className="space-y-6">
                <div className="flex items-center gap-3 mb-2">
                  <ThreeDIcon name="sparkles" size="md" variant="indigo" />
                  <div>
                    <h3 className="text-xl font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                      Hyper-Local Intelligence
                    </h3>
                    <p className="text-xs text-[var(--text-muted)]">
                      Evidence-backed market proxies and regional viability drivers
                    </p>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <LocalIntelligenceCard
                    title="Market Demand"
                    value={`${data.marketAnalysis.demand}%`}
                    evidence={data.marketAnalysis.source}
                    iconName="trending"
                    variant="emerald"
                                          confidence={marketConfidence}
                      
                      
                   isDemo={data.is_demo} />
                  <LocalIntelligenceCard
                    title="Competitive Landscape"
                    value={`${data.marketAnalysis.competition}%`}
                    evidence={data.marketAnalysis.source}
                    iconName="shield"
                    variant="rose"
                                          confidence={marketConfidence}
                      
                      
                   isDemo={data.is_demo} />
                  <LocalIntelligenceCard
                    title="Logistics & Accessibility"
                    value={`${data.marketAnalysis.accessibility}%`}
                    evidence={data.marketAnalysis.source}
                    iconName="cart"
                    variant="blue"
                                          confidence={marketConfidence}
                      
                      
                   isDemo={data.is_demo} />
                  <LocalIntelligenceCard
                    title="Seasonality Risk"
                    value={`${data.marketAnalysis.seasonality}%`}
                    evidence={data.marketAnalysis.source}
                    iconName="chart"
                    variant="amber"
                                          confidence={marketConfidence}
                      
                      
                   isDemo={data.is_demo} />
                </div>
              </div>
            </Reveal>

            {/* Financial Sandbox */}
            <Reveal>

              <Card3DTilt intensity={1.5} glareOpacity={0.05}>
                <div
                  className="p-6 sm:p-8 rounded-3xl border shadow-md backdrop-blur-xl"
                  style={{
                    backgroundColor: 'var(--surface-0)',
                    borderColor: 'var(--border)',
                  }}
                >
                  {/* Sandbox Header */}
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                    <div>
                      <h2 className="text-xl font-black tracking-tight mb-0.5" style={{ color: 'var(--text-primary)' }}>
                        {t(lang, 'report.sandbox_title')}
                      </h2>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        Adjust assumptions to simulate real-time business outcomes.
                      </p>
                    </div>

                    {/* Scenario selector */}
                    <div
                      className="flex p-1 rounded-2xl border gap-0.5"
                      style={{ backgroundColor: 'var(--surface-1)', borderColor: 'var(--border)' }}
                    >
                      {(['conservative', 'base', 'optimistic'] as ScenarioPreset[]).map((p) => (
                        <button
                          key={p}
                          onClick={() => setActivePreset(p)}
                          className="relative px-3.5 py-1.5 text-[11px] font-bold uppercase rounded-xl transition-colors duration-[var(--duration-base)] capitalize cursor-pointer"
                          style={{
                            color: activePreset === p ? 'var(--surface-0)' : 'var(--text-muted)',
                          }}
                        >
                          {activePreset === p && (
                            <motion.span
                              layoutId="preset-pill"
                              className="absolute inset-0 rounded-xl"
                              style={{ backgroundColor: 'var(--text-primary)' }}
                              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                            />
                          )}
                          <span className="relative z-10">{p}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Sliders */}
                    <div className="space-y-6">
                      {sandboxSliders.map((ctrl) => {
                        const displayVal =
                          ctrl.key === 'monthlyRevenue' || ctrl.key === 'monthlyExpenses'
                            ? effectiveSandbox[ctrl.key]
                            : sandbox[ctrl.key];
                        return (
                          <div key={ctrl.key} className="space-y-2.5">
                            <div className="flex justify-between text-[11px] font-semibold uppercase">
                              <span style={{ color: 'var(--text-secondary)' }}>{ctrl.label}</span>
                              <span className="font-black font-mono" style={{ color: 'var(--accent-text)' }}>
                                ₹{Math.round(displayVal).toLocaleString()}
                              </span>
                            </div>
                            <Slider
                              value={[sandbox[ctrl.key] as number]}
                              min={ctrl.min}
                              max={ctrl.max}
                              step={ctrl.step}
                              onValueChange={(val) => setSandbox({ ...sandbox, [ctrl.key]: val[0] })}
                            />
                          </div>
                        );
                      })}
                    </div>

                    {/* Live Results + Chart */}
                    <div
                      className="rounded-2xl border p-5 space-y-5"
                      style={{ backgroundColor: 'var(--surface-1)', borderColor: 'var(--border)' }}
                    >
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-[10px] font-bold uppercase tracking-widest mb-1" style={{ color: 'var(--text-muted)' }}>
                            Monthly EMI
                          </div>
                          <div className="text-2xl font-black font-mono" style={{ color: 'var(--text-primary)' }}>
                            ₹{Math.round(emi).toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold uppercase tracking-widest mb-1" style={{ color: 'var(--text-muted)' }}>
                            Break-even
                          </div>
                          <div className="text-2xl font-black font-mono" style={{ color: 'var(--text-primary)' }}>
                            {breakEven === 999 ? 'Never' : `${Math.round(breakEven)} Mo`}
                          </div>
                        </div>
                      </div>

                      {/* Chart */}
                      <div className="h-44 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={chartData}>
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="var(--border)"
                              vertical={false}
                            />
                            <XAxis
                              dataKey="month"
                              stroke="var(--text-muted)"
                              fontSize={10}
                              tickLine={false}
                              axisLine={false}
                            />
                            <YAxis
                              stroke="var(--text-muted)"
                              fontSize={10}
                              tickLine={false}
                              axisLine={false}
                              tickFormatter={(v) => `₹${v / 1000}k`}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Line
                              type="monotone"
                              dataKey="cash"
                              name="Cumulative Cash"
                              stroke="var(--accent)"
                              strokeWidth={2}
                              dot={false}
                              activeDot={{ r: 4, fill: 'var(--accent)' }}
                            />
                            <Line
                              type="monotone"
                              dataKey="profit"
                              name="Monthly Profit"
                              stroke="var(--text-muted)"
                              strokeWidth={1.5}
                              strokeDasharray="5 4"
                              dot={false}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                </div>
              </Card3DTilt>
            </Reveal>

            {/* Risk Assessment + Recommendations */}
            <Reveal delay={0.05}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Risk Assessment */}
                <div className="p-6 rounded-3xl border bg-[var(--surface-0)] border-[var(--border)] shadow-xs space-y-4">
                  <div className="flex items-center gap-3">
                    <ThreeDIcon name="shield" size="sm" variant="amber" />
                    <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">
                      Risk Evaluation
                    </span>
                  </div>

                  <div className="space-y-3">
                    {deriveRisks().length > 0 ? (
                      deriveRisks().map((risk, i) => (
                        <div
                          key={i}
                          className="flex gap-3 p-3 rounded-2xl border"
                          style={{
                            backgroundColor: risk.impact === 'High' ? 'var(--danger-bg)' : 'var(--warning-bg)',
                            borderColor: risk.impact === 'High' ? 'var(--danger-border)' : 'var(--warning-border)',
                          }}
                        >
                          <div
                            className="w-1 rounded-full shrink-0 mt-0.5"
                            style={{ backgroundColor: risk.impact === 'High' ? 'var(--danger)' : 'var(--warning)' }}
                          />
                          <div>
                            <div
                              className="text-xs font-bold mb-0.5"
                              style={{ color: risk.impact === 'High' ? 'var(--danger)' : 'var(--warning)' }}
                            >
                              {risk.label}
                            </div>
                            <div className="text-[11px] leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                              {risk.note}
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs sm:text-sm italic" style={{ color: 'var(--text-muted)' }}>
                        No significant financial risks detected under current assumptions.
                      </p>
                    )}
                  </div>
                </div>

                {/* Recommended Actions */}
                <div className="p-6 rounded-3xl border bg-[var(--surface-0)] border-[var(--border)] shadow-xs space-y-4">
                  <div className="flex items-center gap-3">
                    <ThreeDIcon name="zap" size="sm" variant="emerald" />
                    <span className="text-xs font-bold uppercase tracking-wider text-[var(--text-muted)]">
                      Recommended Strategic Actions
                    </span>
                  </div>

                  <div className="space-y-3">
                    {data.modifications.length > 0 ? (
                      data.modifications.map((mod, i) => (
                        <div key={i} className="flex items-start gap-3 text-xs sm:text-sm">
                          <span
                            className="font-black font-mono text-xs mt-0.5 shrink-0 w-6 h-6 rounded-xl flex items-center justify-center bg-[var(--accent-subtle)] text-[var(--accent-text)] border border-[var(--accent)]/20"
                          >
                            {i + 1}
                          </span>
                          <span style={{ color: 'var(--text-secondary)' }}>{mod}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs sm:text-sm italic" style={{ color: 'var(--text-muted)' }}>
                        No specific modifications suggested.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </Reveal>

            {/* Financing Roadmap & Recommended Capital Advisory */}
            <Reveal delay={0.1}>
              <div className="space-y-6">
                {/* Section header */}
                <div className="flex items-center gap-3 mb-2">
                  <ThreeDIcon name="scheme" size="md" variant="purple" />
                  <div>
                    <h3 className="text-xl font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                      Recommended Capital & Financing Roadmap
                    </h3>
                    <p className="text-xs text-[var(--text-muted)]">
                      AI-benchmarked capital requirement, asset allocation, and eligible credit subsidies
                    </p>
                  </div>
                </div>

                {/* Capital Advisory Overview Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <MetricTile
                    label="Recommended Setup Capital"
                    value={`₹${(data.financials?.total_project_cost || 0).toLocaleString()}`}
                    accent
                  />
                  <MetricTile
                    label="Min. Viable Launch Capital"
                    value={`₹${(data.financials?.min_viable_capital || Math.round((data.financials?.total_project_cost || 0) * 0.6)).toLocaleString()}`}
                    accent={false}
                  />
                  <MetricTile
                    label="Projected Monthly Revenue"
                    value={`₹${(data.financials?.monthly_revenue || 0).toLocaleString()}`}
                    accent={false}
                  />
                </div>

                {/* Detailed Asset Allocation Breakdown Card */}
                {data.financials.capital_breakdown && Object.keys(data.financials.capital_breakdown).length > 0 && (
                  <Card3DTilt intensity={1.5} glareOpacity={0.05}>
                    <div
                      className="p-6 rounded-3xl border shadow-xs backdrop-blur-md"
                      style={{
                        backgroundColor: 'var(--surface-0)',
                        borderColor: 'var(--border)',
                      }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="text-xs font-bold uppercase tracking-wider text-[var(--text-primary)]">
                          Estimated Asset Allocation & Infrastructure Costs
                        </div>
                        <span className="text-[11px] font-mono text-[var(--text-muted)]">
                          {Object.keys(data.financials.capital_breakdown).length} Components
                        </span>
                      </div>

                      <div className="space-y-3.5">
                        {Object.entries(data.financials.capital_breakdown).map(([item, cost]) => {
                          const pct = Math.min(100, Math.round((cost / data.financials.total_project_cost) * 100)) || 0;
                          return (
                            <div key={item} className="space-y-1.5">
                              <div className="flex justify-between text-xs font-semibold">
                                <span style={{ color: 'var(--text-primary)' }}>{item}</span>
                                <span className="font-mono font-bold" style={{ color: 'var(--accent-text)' }}>
                                  ₹{cost.toLocaleString()} <span className="text-[10px] text-[var(--text-muted)]">({pct}%)</span>
                                </span>
                              </div>
                              <div className="w-full h-2 rounded-full bg-[var(--surface-2)] overflow-hidden">
                                <div
                                  className="h-full rounded-full bg-[var(--accent)] transition-all duration-500"
                                  style={{ width: `${pct}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </Card3DTilt>
                )}

                {/* Scheme Cards */}
                <Stagger stagger={0.1} className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  {data.matchedSchemes?.map((scheme: Scheme, i: number) => (
                    <Card3DTilt key={i} intensity={1.5} glareOpacity={0.05}>
                      <div
                        className="h-full p-6 rounded-3xl border backdrop-blur-md relative overflow-hidden flex flex-col justify-between"
                        style={{
                          backgroundColor: 'var(--surface-0)',
                          borderColor: 'var(--border)',
                          boxShadow: 'var(--shadow-sm)',
                        }}
                      >
                        <div>
                          <div className="flex justify-between items-start gap-2 mb-4">
                            <h4 className="text-base font-bold leading-snug">
                              {scheme.name}
                            </h4>
                            <Badge variant="secondary" className="text-[10px] shrink-0 font-bold uppercase">
                              {scheme.ministry}
                            </Badge>
                          </div>

                          <div
                            className="grid grid-cols-2 gap-3 p-3.5 rounded-2xl border mb-4"
                            style={{ backgroundColor: 'var(--surface-1)', borderColor: 'var(--border)' }}
                          >
                            <div>
                              <div className="text-[10px] font-bold uppercase tracking-widest mb-0.5" style={{ color: 'var(--text-muted)' }}>
                                Subsidy
                              </div>
                              <div className="font-black text-lg font-mono" style={{ color: 'var(--success)' }}>
                                {scheme.benefit.subsidyPercent}%
                              </div>
                            </div>
                            <div>
                              <div className="text-[10px] font-bold uppercase tracking-widest mb-0.5" style={{ color: 'var(--text-muted)' }}>
                                Max Loan
                              </div>
                              <div className="font-black text-lg font-mono" style={{ color: 'var(--text-primary)' }}>
                                ₹{scheme.benefit.loanAmount.toLocaleString()}
                              </div>
                            </div>
                          </div>
                        </div>

                        <a
                          href={scheme.sourceUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider transition-all duration-[var(--duration-base)] hover:gap-2 text-[var(--accent-text)] pt-2"
                        >
                          <span>Official Guidelines</span>
                          <ExternalLink size={14} />
                        </a>
                      </div>
                    </Card3DTilt>
                  ))}
                </Stagger>
              </div>
            </Reveal>
          </div>
        </div>

        {/* ── FOOTER ── */}
        <Reveal className="mt-16 pt-8 border-t" style={{ borderColor: 'var(--border)' }}>
          <footer className="flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-mono text-[var(--text-muted)]">
            <div className="uppercase tracking-widest">
              Generated via GramNirnay.ai Decision Support System
            </div>
            <div className="flex gap-6 font-bold uppercase">
              <span>Source: {data.marketAnalysis.source}</span>
              <span>Confidence: {data.marketAnalysis.confidence}</span>
            </div>
          </footer>
        </Reveal>
      </div>
    </div>
  );
}
