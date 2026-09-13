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
  calculateCapitalEfficiency,
  calculateSurvivalThreshold
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
  DollarSign, Activity, LayoutDashboard, MapPin,
  ClipboardList, FileText, AlertCircle, Lightbulb, ChevronRight
} from 'lucide-react';

/* ─────────────────────────────────────────
   UI Components
───────────────────────────────────────── */

function MetricCard({ label, value, unit = '', trend, variant = 'default' }: { label: string, value: number | string, unit?: string, trend?: string, variant?: 'default' | 'success' | 'danger' }) {
  const colors = {
    default: 'var(--text-primary)',
    success: 'var(--success)',
    danger: 'var(--danger)',
  };
  return (
    <div className="p-4 rounded-2xl border bg-var(--surface-0) transition-all hover:shadow-sm" style={{ borderColor: 'var(--border)' }}>
      <div className="text-[10px] font-bold uppercase tracking-widest mb-1 opacity-50">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className="text-2xl font-black font-mono" style={{ color: colors[variant] }}>{typeof value === 'number' ? value.toLocaleString() : value}</span>
        <span className="text-xs font-bold opacity-50">{unit}</span>
      </div>
      {trend && <div className="text-[10px] mt-1 flex items-center gap-1 opacity-70"><TrendingUp size={10} /> {trend}</div>}
    </div>
  );
}

function BusinessBlueprint({ blueprint }: { blueprint: AnalysisResult['business_blueprint'] }) {
  if (!blueprint) return null;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-2xl border bg-var(--surface-1) border-dashed">
          <div className="text-xs font-bold uppercase mb-2 opacity-50 flex items-center gap-2"><Zap size={12}/> Inputs</div>
          <div className="flex flex-wrap gap-2">
            {blueprint.inputs.map(i => <Badge key={i} variant="secondary" className="text-[10px]">{i}</Badge>)}
          </div>
        </div>
        <div className="p-4 rounded-2xl border bg-var(--surface-1) border-dashed">
          <div className="text-xs font-bold uppercase mb-2 opacity-50 flex items-center gap-2"><Activity size={12}/> Operations</div>
          <div className="text-xs opacity-80">Deterministic workflow based on {blueprint.flow.length} key steps.</div>
        </div>
        <div className="p-4 rounded-2xl border bg-var(--surface-1) border-dashed">
          <div className="text-xs font-bold uppercase mb-2 opacity-50 flex items-center gap-2"><Rocket size={12}/> Outputs</div>
          <div className="flex flex-wrap gap-2">
            {blueprint.outputs.map(o => <Badge key={o} variant="secondary" className="text-[10px]">{o}</Badge>)}
          </div>
        </div>
      </div>
      <div className="relative pl-8 space-y-4">
        <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-var(--border)" />
        {blueprint.flow.map((step, i) => (
          <div key={i} className="relative">
            <div className="absolute -left-6 top-1 w-4 h-4 rounded-full bg-var(--accent) border-4 border-var(--surface-0)" />
            <div className="p-3 rounded-xl border bg-var(--surface-0) hover:shadow-sm transition-all">
              <div className="text-xs font-bold text-var(--accent) uppercase mb-1">{step.step}</div>
              <div className="text-sm opacity-80">{step.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ActionPlan({ roadmap }: { roadmap: AnalysisResult['startup_roadmap'] }) {
  if (!roadmap) return null;
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {roadmap.map((week, i) => (
        <div key={i} className="p-4 rounded-2xl border bg-var(--surface-0)">
          <div className="flex items-center justify-between mb-3">
            <div className="text-xs font-black uppercase tracking-tighter p-1 px-2 rounded bg-var(--accent) text-white">Week {week.week}</div>
          </div>
          <ul className="space-y-2">
            {week.tasks.map((task, j) => (
              <li key={j} className="text-xs flex items-start gap-2 opacity-80">
                <ChevronRight size={12} className="mt-0.5 shrink-0 text-var(--accent)" />
                {task}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

function RiskMatrix({ risks }: { risks: AnalysisResult['risk_matrix'] }) {
  if (!risks) return null;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs">
        <thead>
          <tr className="text-[10px] font-bold uppercase opacity-50 border-b border-var(--border)">
            <th className="pb-2">Risk</th>
            <th className="pb-2">Severity</th>
            <th className="pb-2">Prob.</th>
            <th className="pb-2">Mitigation</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-var(--border)">
          {risks.map((r, i) => (
            <tr key={i} className="group hover:bg-var(--surface-1)">
              <td className="py-3 font-bold">{r.risk}</td>
              <td className="py-3">
                <Badge variant={r.severity === 'High' ? 'danger' : r.severity === 'Medium' ? 'warning' : 'secondary'} className="text-[9px]">{r.severity}</Badge>
              </td>
              <td className="py-3 opacity-70">{r.probability}</td>
              <td className="py-3 opacity-80 italic">{r.mitigation}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ReportPage() {
  const { lang } = useLanguage();
  const router = useRouter();
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [activePreset, setActivePreset] = useState<'conservative' | 'base' | 'optimistic'>('base');
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

  if (!data) return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--surface-1)', color: 'var(--text-primary)' }}>
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-full border-3 border-t-[var(--accent)] animate-spin" style={{ borderColor: 'var(--border)', borderTopColor: 'var(--accent)' }} />
        <p className="text-sm font-medium opacity-60">Analyzing venture viability...</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--surface-1)', color: 'var(--text-primary)' }}>
      <div className="pointer-events-none fixed inset-0 opacity-20" style={{ backgroundImage: 'url(/media/grid-pattern.svg)', backgroundSize: '280px 280px', backgroundRepeat: 'repeat' }} />
      <div className="relative z-10 max-w-[1400px] mx-auto px-4 sm:px-6 md:px-10 pt-24 pb-20">

        <div className="flex justify-between items-center mb-10">
          <div className="flex items-center gap-3">
            <ThreeDIcon name="chart" size="sm" variant="blue" />
            <h1 className="text-xl font-black tracking-tight uppercase">{t(lang, 'report.title')}</h1>
          </div>
          <Button variant="outline" onClick={() => router.push('/')} className="gap-2 rounded-2xl">
            <ArrowLeft size={16} /> New Analysis
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* LEFT COLUMN: EXECUTIVE SUMMARY & CORE METRICS */}
          <div className="lg:col-span-4 space-y-6">
            <Reveal>
              <div className="p-8 rounded-3xl border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-2 mb-4">
                  <Target size={20} style={{ color: 'var(--accent)' }} />
                  <h2 className="text-lg font-black tracking-tight uppercase">Executive Summary</h2>
                </div>
                <div className="flex items-center gap-6 mb-6">
                  <div className="relative w-24 h-24 flex items-center justify-center">
                    <svg width="96" height="96" className="rotate-[-90deg]">
                      <circle cx="48" cy="48" r="40" fill="none" stroke="var(--surface-3)" strokeWidth="10" />
                      <motion.circle
                        cx="48" cy="48" r="40" fill="none" stroke="var(--accent)" strokeWidth="10" strokeLinecap="round"
                        strokeDasharray={2 * Math.PI * 40}
                        initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
                        animate={{ strokeDashoffset: (2 * Math.PI * 40) * (1 - data.viabilityScore / 100) }}
                        transition={{ duration: 1.5 }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-black">{data.viabilityScore}</span>
                      <span className="text-[8px] font-bold uppercase opacity-50">Score</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <Badge variant="secondary" className="text-[10px] mb-1">{data.category}</Badge>
                    <div className="text-lg font-black leading-tight">{data.recommendation}</div>
                  </div>
                </div>
                <p className="text-sm opacity-70 leading-relaxed italic mb-6">
                  "{data.interpreter_reasoning}"
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <MetricCard label="Investment" value={effectiveSandbox.setupCost} unit="₹" />
                  <MetricCard label="Annual Profit" value={annualProfit} unit="₹" variant="success" />
                  <MetricCard label="Break-even" value={breakEven} unit="Mo" variant="warning" />
                  <MetricCard label="Projected ROI" value={roi} unit="%" variant="success" />
                </div>
              </div>
            </Reveal>
          </div>

          {/* CENTER COLUMN: THE STRATEGIC BLUEPRINT */}
          <div className="lg:col-span-8 space-y-8">
            <Reveal delay={0.1}>
              <div className="p-8 rounded-3xl border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center justify-between mb-8">
                  <div className="flex items-center gap-2">
                    <Lightbulb size={20} style={{ color: 'var(--accent)' }} />
                    <h2 className="text-xl font-black tracking-tight uppercase">Business Model Blueprint</h2>
                  </div>
                  <div className="flex p-1 rounded-xl bg-var(--surface-1) border border-var(--border)">
                    {(['conservative', 'base', 'optimistic'] as const).map(p => (
                      <button key={p} onClick={() => setActivePreset(p)} className={`px-3 py-1 text-[10px] font-bold uppercase rounded-lg transition-all ${activePreset === p ? 'bg-var(--accent) text-white' : 'opacity-50'}`}>
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
                <BusinessBlueprint blueprint={data.business_blueprint} />
              </div>
            </Reveal>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <Reveal delay={0.2}>
                <div className="p-8 rounded-3xl border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
                  <div className="flex items-center gap-2 mb-6">
                    <ClipboardList size={20} style={{ color: 'var(--accent)' }} />
                    <h3 className="text-lg font-black uppercase">The 30-Day Roadmap</h3>
                  </div>
                  <ActionPlan roadmap={data.startup_roadmap} />
                </div>
              </Reveal>

              <Reveal delay={0.3}>
                <div className="p-8 rounded-3xl border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
                  <div className="flex items-center gap-2 mb-6">
                    <FileText size={20} style={{ color: 'var(--accent)' }} />
                    <h3 className="text-lg font-black uppercase">Compliance & Docs</h3>
                  </div>
                  <div className="space-y-3">
                    {data.regulatory_requirements?.map((req, i) => (
                      <div key={i} className="flex items-center justify-between p-3 rounded-xl border bg-var(--surface-1)">
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-1.5 rounded-full bg-var(--accent)" />
                          <span className="text-xs font-medium">{req.doc}</span>
                        </div>
                        <Badge variant="outline" className="text-[9px] opacity-60">{req.status}</Badge>
                      </div>
                    )) || <p className="text-xs opacity-50 italic">No specific documents listed.</p>}
                  </div>
                </div>
              </Reveal>
            </div>

            <Reveal delay={0.4}>
              <div className="p-8 rounded-3xl border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-2 mb-6">
                  <AlertCircle size={20} style={{ color: 'var(--danger)' }} />
                  <h3 className="text-lg font-black uppercase">Risk Assessment</h3>
                </div>
                <RiskMatrix risks={data.risk_matrix} />
              </div>
            </Reveal>

            <Reveal delay={0.5}>
              <div className="p-8 rounded-3xl border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-2 mb-6">
                  <ShieldCheck size={20} style={{ color: 'var(--success)' }} />
                  <h3 className="text-lg font-black uppercase">Government Support</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {data.matchedSchemes.map((scheme, i) => (
                    <div key={i} className="p-4 rounded-2xl border bg-var(--surface-1) hover:border-var(--accent) transition-all">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-xs font-bold">{scheme.name}</h4>
                        <Badge variant="secondary" className="text-[9px]">{scheme.ministry}</Badge>
                      </div>
                      <div className="text-[11px] opacity-80 mb-3">{scheme.benefit.subsidyPercent}% subsidy / ₹{scheme.benefit.loanAmount.toLocaleString()} loan</div>
                      <a href={scheme.sourceUrl} target="_blank" className="text-[10px] font-bold text-var(--accent) flex items-center gap-1 hover:underline">
                        Official Portal <ExternalLink size={10} />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            </Reveal>
          </div>
        </div>
      </div>
    </div>
  );
}
