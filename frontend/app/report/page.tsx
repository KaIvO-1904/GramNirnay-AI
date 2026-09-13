'use client';
import React, { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import {
  calculateEMI,
  calculateBreakEven,
  calculateROI,
  calculateSubsidyBenefit,
} from '@/lib/financials';
import { useLanguage } from '@/lib/LanguageContext';
import { t } from '@/lib/i18n';
import { AnalysisResult } from '@/types';
import { Reveal } from '@/components/motion';
import Card3DTilt from '@/components/3d/Card3DTilt';
import ThreeDIcon from '@/components/3d/ThreeDIcons';
import {
  ArrowLeft, TrendingUp, AlertTriangle, ShieldCheck,
  ExternalLink, Zap, Rocket,
  DollarSign, Activity, LayoutDashboard,
  ClipboardList, FileText, Lightbulb, ChevronRight,
  Scale, Wallet, Gavel, Info
} from 'lucide-react';

/* ─────────────────────────────────────────
   Utilities
───────────────────────────────────────── */

function formatValue(val: number | string | null): string {
  if (val === null || val === undefined) return 'N/A';
  if (typeof val === 'string') return val;

  if (val === 0) return '0';

  const absVal = Math.abs(val);
  if (absVal >= 10000000) {
    return (val / 10000000).toFixed(2) + ' Cr';
  } else if (absVal >= 100000) {
    return (val / 100000).toFixed(2) + ' L';
  } else if (absVal >= 1000) {
    return (val / 1000).toFixed(1) + ' K';
  }
  return val.toLocaleString();
}

/* ─────────────────────────────────────────
   Configuration
───────────────────────────────────────── */

const sandboxSliders = [
  { key: 'setupCost', label: 'Initial Setup Cost', min: 10000, max: 1000000, step: 5000 },
  { key: 'monthlyRevenue', label: 'Est. Monthly Revenue', min: 5000, max: 500000, step: 1000 },
  { key: 'monthlyExpenses', label: 'Est. Monthly Expenses', min: 1000, max: 200000, step: 1000 },
  { key: 'loanAmount', label: 'Loan Amount', min: 0, max: 1000000, step: 10000 },
];

/* ─────────────────────────────────────────
   High-Fidelity UI Components
───────────────────────────────────────── */

function KpiWidget({ label, value, unit = '', trend, variant = 'default', icon: Icon }: { label: string, value: number | string | null, unit?: string, trend?: string, variant?: 'default' | 'success' | 'danger', icon: any }) {
  const colors = {
    default: 'var(--text-primary)',
    success: 'var(--success)',
    danger: 'var(--danger)',
  };
  return (
    <div className="p-5 rounded-3xl border bg-var(--surface-0) transition-all hover:shadow-md group min-w-0" style={{ borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="p-2 rounded-xl bg-var(--surface-1) group-hover:bg-var(--accent)/10 transition-colors">
          <Icon size={16} style={{ color: 'var(--accent)' }} />
        </div>
        {trend && <div className="text-[10px] font-bold flex items-center gap-1 text-var(--success) truncate"><TrendingUp size={10} /> {trend}</div>}
      </div>
      <div className="text-xs font-bold uppercase tracking-widest mb-1 opacity-50 truncate">{label}</div>
      <div className="flex items-baseline gap-1 overflow-hidden">
        <span className="text-2xl md:text-3xl font-black font-mono truncate" style={{ color: colors[variant] }}>
          {typeof value === 'number' ? formatValue(value) : (value ?? 'N/A')}
        </span>
        <span className="text-sm font-bold opacity-50 shrink-0">{unit}</span>
      </div>
    </div>
  );
}

function OperationalFlow({ blueprint }: { blueprint: AnalysisResult['business_blueprint'] }) {
  if (!blueprint) return null;
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-3xl border bg-var(--surface-1)/50 border-dashed flex flex-col gap-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase opacity-50"><Zap size={14} className="text-var(--accent)"/> Resource Inputs</div>
          <div className="flex flex-wrap gap-2">
            {blueprint.inputs.map(i => <Badge key={i} variant="secondary" className="text-[10px] px-2 py-0.5 rounded-lg">{i}</Badge>)}
          </div>
        </div>
        <div className="p-6 rounded-3xl border bg-var(--surface-1)/50 border-dashed flex flex-col gap-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase opacity-50"><Activity size={14} className="text-var(--accent)"/> Core Process</div>
          <div className="text-sm opacity-80 leading-relaxed">A deterministic operational cycle consisting of {blueprint.flow.length} synchronized stages.</div>
        </div>
        <div className="p-6 rounded-3xl border bg-var(--surface-1)/50 border-dashed flex flex-col gap-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase opacity-50"><Rocket size={14} className="text-var(--accent)"/> Value Outputs</div>
          <div className="flex flex-wrap gap-2">
            {blueprint.outputs.map(o => <Badge key={o} variant="secondary" className="text-[10px] px-2 py-0.5 rounded-lg">{o}</Badge>)}
          </div>
        </div>
      </div>
      <div className="relative pl-10 space-y-6">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-var(--accent) via-var(--border) to-var(--accent)" />
        {blueprint.flow.map((step, i) => (
          <div key={i} className="relative group">
            <div className="absolute -left-7 top-1 w-6 h-6 rounded-full bg-var(--surface-0) border-2 border-var(--accent) flex items-center justify-center z-10 group-hover:scale-110 transition-transform">
              <span className="text-[10px] font-black text-var(--accent)">{i+1}</span>
            </div>
            <div className="p-4 rounded-2xl border bg-var(--surface-0) group-hover:shadow-lg transition-all hover:border-var(--accent)/50">
              <div className="text-xs font-black text-var(--accent) uppercase mb-1 tracking-widest">{step.step}</div>
              <div className="text-sm opacity-80 leading-relaxed">{step.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StartupTimeline({ roadmap }: { roadmap: AnalysisResult['startup_roadmap'] }) {
  if (!roadmap) return null;
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {roadmap.map((week, i) => (
        <div key={i} className="p-6 rounded-3xl border bg-var(--surface-0) hover:shadow-lg transition-all group">
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-black uppercase tracking-tighter px-2 py-1 rounded-lg bg-var(--accent) text-white">Week {week.week}</div>
            <div className="opacity-0 group-hover:opacity-100 transition-opacity"><ChevronRight size={16} className="text-var(--accent)"/></div>
          </div>
          <ul className="space-y-3">
            {week.tasks.map((task, j) => (
              <li key={j} className="text-xs flex items-start gap-3 opacity-80">
                <div className="w-1.5 h-1.5 rounded-full bg-var(--accent) mt-1 shrink-0" />
                {task}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

function ComplianceGrid({ requirements }: { requirements: AnalysisResult['regulatory_requirements'] }) {
  if (!requirements) return null;
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {requirements.map((req, i) => (
        <div key={i} className="flex items-center justify-between p-4 rounded-2xl border bg-var(--surface-1) hover:bg-var(--surface-0) transition-all">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-var(--surface-0) border">
              <FileText size={14} className="text-var(--accent)" />
            </div>
            <div>
              <div className="text-xs font-bold">{req.doc}</div>
              <div className="text-[10px] opacity-50">{req.source}</div>
            </div>
          </div>
          <Badge variant="outline" className="text-[9px] uppercase tracking-tighter">{req.status}</Badge>
        </div>
      ))}
    </div>
  );
}

function RiskAnalysis({ risks }: { risks: AnalysisResult['risk_matrix'] }) {
  if (!risks) return null;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs border-separate border-spacing-y-2">
        <thead>
          <tr className="text-[10px] font-black uppercase opacity-50">
            <th className="pb-3 pl-4">Risk Factor</th>
            <th className="pb-3">Severity</th>
            <th className="pb-3">Probability</th>
            <th className="pb-3 pr-4">Mitigation Strategy</th>
          </tr>
        </thead>
        <tbody>
          {risks.map((r, i) => (
            <tr key={i} className="group bg-var(--surface-0) hover:bg-var(--surface-1) transition-colors">
              <td className="py-4 pl-4 rounded-l-2xl font-bold border-l-4 border-transparent group-hover:border-var(--accent)">{r.risk}</td>
              <td className="py-4">
                <Badge variant={r.severity === 'High' ? 'danger' : r.severity === 'Medium' ? 'warning' : 'secondary'} className="text-[9px]">{r.severity}</Badge>
              </td>
              <td className="py-4 opacity-70 font-mono">{r.probability}</td>
              <td className="py-4 pr-4 rounded-r-2xl opacity-80 italic leading-relaxed">{r.mitigation}</td>
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

  const chartData = Array.from({ length: 12 }, (_, i) => ({
    month: `Mo ${i + 1}`,
    cash: Math.round(monthlyNet * (i + 1)),
  }));

  const fundingMix = useMemo(() => {
    const total = data?.financials.total_project_cost || 1;
    const user = data?.financials.user_capital || 0;
    const subsidy = calculateSubsidyBenefit(data?.financials.total_project_cost || 0, data?.matchedSchemes[0]?.benefit.subsidyPercent || 0);
    const loan = data?.financials.financing_required || 0;
    return {
      userPct: (user / total) * 100,
      subsidyPct: (subsidy / total) * 100,
      loanPct: (loan / total) * 100,
    };
  }, [data]);

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

        <div className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-var(--accent) text-white shadow-lg">
              <ThreeDIcon name="chart" size="sm" variant="blue" />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight uppercase">{t(lang, 'report.title')}</h1>
              <p className="text-xs opacity-50 font-bold uppercase tracking-widest">Business Intelligence Report</p>
            </div>
          </div>
          <Button variant="outline" onClick={() => router.push('/')} className="gap-2 rounded-2xl px-6 py-6 h-auto">
            <ArrowLeft size={16} /> New Analysis
          </Button>
        </div>

        {/* SECTION 1: THE VERDICT (HERO) */}
        <div className="mb-16">
          <Reveal>
            <div className="p-10 rounded-[40px] border bg-var(--surface-0) shadow-xl relative overflow-hidden" style={{ borderColor: 'var(--border)' }}>
              <div className="absolute top-0 right-0 w-64 h-64 bg-var(--accent)/5 rounded-full blur-3xl -mr-32 -mt-32" />
              <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                <div className="lg:col-span-4 flex flex-col items-center text-center">
                  <div className="relative w-40 h-40 flex items-center justify-center mb-6">
                    <svg width="160" height="160" className="rotate-[-90deg]">
                      <circle cx="80" cy="80" r="70" fill="none" stroke="var(--surface-3)" strokeWidth="16" />
                      <motion.circle
                        cx="80" cy="80" r="70" fill="none" stroke="var(--accent)" strokeWidth="16" strokeLinecap="round"
                        strokeDasharray={2 * Math.PI * 70}
                        initial={{ strokeDashoffset: 2 * Math.PI * 70 }}
                        animate={{ strokeDashoffset: (2 * Math.PI * 70) * (1 - data.viabilityScore / 100) }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-5xl font-black font-mono">{data.viabilityScore}</span>
                      <span className="text-xs font-bold uppercase opacity-50 tracking-widest">Score</span>
                    </div>
                  </div>
                  <Badge variant="secondary" className="text-xs mb-3 px-4 py-1 rounded-full uppercase">{data.category}</Badge>
                  <div className="text-2xl font-black leading-tight mb-2">{data.recommendation}</div>
                </div>
                <div className="lg:col-span-8 space-y-6">
                  <div className="p-6 rounded-3xl bg-var(--surface-1) border border-var(--border) relative">
                    <div className="absolute -top-3 left-6 px-3 py-1 rounded-full bg-var(--accent) text-white text-[10px] font-black uppercase">Analyst Reasoning</div>
                    <p className="text-base opacity-80 leading-relaxed italic">
                      "{data.interpreter_reasoning}"
                    </p>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <KpiWidget label="Total Capital" value={effectiveSandbox.setupCost} unit="₹" icon={Wallet} />
                    <KpiWidget label="Annual Net" value={annualProfit} unit="₹" variant="success" icon={TrendingUp} />
                    <KpiWidget label="Break-even" value={breakEven} unit="Mo" variant="danger" icon={Activity} />
                    <KpiWidget label="Projected ROI" value={roi} unit="%" variant="success" icon={Scale} />
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>

        {/* SECTION 2: THE STRATEGY SIMULATOR & FINANCIALS */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-16">
          <div className="lg:col-span-7">
            <Reveal>
              <Card3DTilt intensity={1.2}>
                <div className="p-8 rounded-[40px] border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
                  <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-var(--accent)/10"><Rocket size={20} style={{ color: 'var(--accent)' }} /></div>
                      <h2 className="text-xl font-black tracking-tight uppercase">Strategy Simulator</h2>
                    </div>
                    <div className="flex p-1 rounded-2xl bg-var(--surface-1) border border-var(--border)">
                      {(['conservative', 'base', 'optimistic'] as const).map(p => (
                        <button key={p} onClick={() => setActivePreset(p)} className={`px-4 py-1.5 text-[10px] font-bold uppercase rounded-xl transition-all ${activePreset === p ? 'bg-var(--accent) text-white shadow-sm' : 'opacity-50 hover:opacity-100'}`}>
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
                    <LeverButton label="Govt Subsidy" active={levers.appliedSubsidy} onClick={() => setLevers(l => ({...l, appliedSubsidy: !l.appliedSubsidy}))} icon={DollarSign} />
                    <LeverButton label="Lean Startup" active={levers.leanMode} onClick={() => setLevers(l => ({...l, leanMode: !l.leanMode}))} icon={Zap} />
                    <LeverButton label="Aggressive Growth" active={levers.growthMode} onClick={() => setLevers(l => ({...l, growthMode: !l.growthMode}))} icon={TrendingUp} />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                    <div className="space-y-8">
                      {sandboxSliders.map((ctrl) => (
                        <div key={ctrl.key} className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="text-xs font-bold uppercase opacity-60">{ctrl.label}</span>
                            <span className="text-xs font-mono font-black text-var(--accent)">₹{Math.round(sandbox[ctrl.key as keyof typeof sandbox] || 0).toLocaleString()}</span>
                          </div>
                          <Slider
                            value={[sandbox[ctrl.key as keyof typeof sandbox] || 0]}
                            min={ctrl.min} max={ctrl.max} step={ctrl.step}
                            onValueChange={(val) => setSandbox({ ...sandbox, [ctrl.key]: val[0] })}
                          />
                        </div>
                      ))}
                    </div>
                    <div className="flex flex-col gap-6">
                      <div className="h-56 w-full rounded-3xl border bg-var(--surface-1) p-4">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={chartData}>
                            <defs>
                              <linearGradient id="colorCash" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.3}/>
                                <stop offset="95%" stopColor="var(--accent)" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                            <XAxis dataKey="month" stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="var(--text-muted)" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v / 1000}k`} />
                            <Tooltip content={<CustomTooltip />} />
                            <Area type="monotone" dataKey="cash" stroke="var(--accent)" strokeWidth={3} fillOpacity={1} fill="url(#colorCash)" />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="p-6 rounded-3xl border bg-var(--accent) text-white text-center shadow-lg">
                        <div className="text-[10px] font-bold uppercase opacity-80 mb-1">Projected Break-even</div>
                        <div className="text-4xl font-black font-mono">
                          {breakEven === null ? 'Never' : `${Math.round(breakEven)} Mo`}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card3DTilt>
            </Reveal>
          </div>

          <div className="lg:col-span-5 space-y-6">
            <Reveal>
              <div className="p-8 rounded-[40px] border bg-var(--surface-0) shadow-sm h-full" style={{ borderColor: 'var(--border)' }}>
                <div className="flex items-center gap-3 mb-8">
                  <div className="p-2 rounded-xl bg-var(--surface-1)"><LayoutDashboard size={20} style={{ color: 'var(--accent)' }} /></div>
                  <h2 className="text-xl font-black tracking-tight uppercase">Market Intelligence</h2>
                </div>
                <div className="grid grid-cols-1 gap-6">
                  <IntelWidget title="Market Demand" value={data.marketAnalysis.demand} variant="success" icon={TrendingUp} evidence={data.marketAnalysis.source} />
                  <IntelWidget title="Competition" value={data.marketAnalysis.competition} variant="danger" icon={ShieldCheck} evidence={data.marketAnalysis.source} />
                  <IntelWidget title="Infrastructure" value={data.marketAnalysis.accessibility} variant="default" icon={Rocket} evidence={data.marketAnalysis.source} />
                  <IntelWidget title="Seasonality" value={data.marketAnalysis.seasonality} variant="warning" icon={Activity} evidence={data.marketAnalysis.source} />
                </div>
                <div className="mt-10 p-6 rounded-3xl bg-var(--surface-1) border border-var(--border) italic text-sm opacity-80 leading-relaxed">
                  <div className="flex items-center gap-2 mb-2 not-italic font-bold uppercase text-[10px] opacity-50">
                    <Info size={12}/> Analyst Perspective
                  </div>
                  "{data.interpreter_reasoning}"
                </div>
              </div>
            </Reveal>
          </div>
        </div>

        {/* SECTION 3: OPERATIONAL BLUEPRINT */}
        <div className="mb-16">
          <Reveal>
            <div className="p-10 rounded-[40px] border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-3 mb-12">
                <div className="p-2 rounded-xl bg-var(--accent)/10"><Lightbulb size={20} style={{ color: 'var(--accent)' }} /></div>
                <h2 className="text-2xl font-black tracking-tight uppercase">The Operational Blueprint</h2>
              </div>
              <OperationalFlow blueprint={data.business_blueprint} />
            </div>
          </Reveal>
        </div>

        {/* SECTION 4: IMPLEMENTATION & COMPLIANCE */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          <Reveal delay={0.1}>
            <div className="p-10 rounded-[40px] border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-3 mb-8">
                <div className="p-2 rounded-xl bg-var(--accent)/10"><ClipboardList size={20} style={{ color: 'var(--accent)' }} /></div>
                <h2 className="text-xl font-black tracking-tight uppercase">30-Day Launch Roadmap</h2>
              </div>
              <StartupTimeline roadmap={data.startup_roadmap} />
            </div>
          </Reveal>
          <Reveal delay={0.2}>
            <div className="p-10 rounded-[40px] border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-3 mb-8">
                <div className="p-2 rounded-xl bg-var(--accent)/10"><Gavel size={20} style={{ color: 'var(--accent)' }} /></div>
                <h2 className="text-xl font-black tracking-tight uppercase">Compliance & Licensing</h2>
              </div>
              <ComplianceGrid requirements={data.regulatory_requirements} />
            </div>
          </Reveal>
        </div>

        {/* SECTION 5: FUNDING STRATEGY */}
        <div className="mb-16">
          <Reveal>
            <div className="p-10 rounded-[40px] border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-3 mb-12">
                <div className="p-2 rounded-xl bg-var(--accent)/10"><Wallet size={20} style={{ color: 'var(--accent)' }} /></div>
                <h2 className="text-2xl font-black tracking-tight uppercase">Strategic Funding Strategy</h2>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                <div className="lg:col-span-1 space-y-6">
                  <div className="p-6 rounded-3xl border bg-var(--surface-1) shadow-sm">
                    <div className="text-xs font-black uppercase opacity-50 mb-4">Funding Mix</div>
                    <div className="h-6 w-full rounded-full overflow-hidden flex mb-6 bg-var(--surface-2)">
                      <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${fundingMix.userPct}%` }} title="Own Capital" />
                      <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: `${fundingMix.subsidyPct}%` }} title="Govt Subsidy" />
                      <div className="h-full bg-amber-500 transition-all duration-500" style={{ width: `${fundingMix.loanPct}%` }} title="External Loan" />
                    </div>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between opacity-80"><span>Own Contribution</span><span className="font-mono">₹{data.financials.user_capital?.toLocaleString()}</span></div>
                      <div className="flex justify-between text-emerald-500 font-bold"><span>Est. Subsidy</span><span className="font-mono">₹{calculateSubsidyBenefit(data.financials.total_project_cost, data.matchedSchemes[0]?.benefit.subsidyPercent || 0).toLocaleString()}</span></div>
                      <div className="flex justify-between border-t pt-2 font-black"><span>Financing Gap</span><span className="font-mono">₹{data.financials.financing_required.toLocaleString()}</span></div>
                    </div>
                  </div>
                </div>
                <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {data.matchedSchemes.map((scheme, i) => (
                    <div key={i} className="p-6 rounded-3xl border bg-var(--surface-1) hover:border-var(--accent) transition-all group">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="text-sm font-black">{scheme.name}</h4>
                        <Badge variant="secondary" className="text-[9px]">{scheme.ministry}</Badge>
                      </div>
                      <div className="text-xs opacity-80 mb-4 leading-relaxed">
                        Benefit: <span className="font-bold text-var(--accent)">{scheme.benefit.subsidyPercent}% subsidy</span> /
                        <span className="font-bold text-var(--accent)"> ₹{scheme.benefit.loanAmount.toLocaleString()} max loan</span>
                      </div>
                      <a href={scheme.sourceUrl} target="_blank" className="text-[10px] font-black text-var(--accent) flex items-center gap-1 group-hover:underline">
                        Official Portal <ExternalLink size={10} />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Reveal>
        </div>

        {/* SECTION 6: RISK & MITIGATION */}
        <div className="mb-16">
          <Reveal>
            <div className="p-10 rounded-[40px] border bg-var(--surface-0) shadow-sm" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-3 mb-12">
                <div className="p-2 rounded-xl bg-var(--accent)/10"><AlertTriangle size={20} style={{ color: 'var(--accent)' }} /></div>
                <h2 className="text-2xl font-black tracking-tight uppercase">Risk Analysis & Mitigation</h2>
              </div>
              <RiskAnalysis risks={data.risk_matrix} />
            </div>
          </Reveal>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────
   Sub-components
───────────────────────────────────────── */

function LeverButton({ label, active, onClick, icon: Icon }: { label: string, active: boolean, onClick: () => void, icon: any }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center gap-2 p-4 rounded-2xl border transition-all font-bold text-[11px] uppercase tracking-widest ${
        active ? 'shadow-lg scale-[1.02]' : 'opacity-60 hover:opacity-100'
      }`}
      style={{
        backgroundColor: active ? 'var(--accent)' : 'var(--surface-1)',
        borderColor: active ? 'var(--accent)' : 'var(--border)',
        color: active ? 'var(--surface-0)' : 'var(--text-primary)'
      }}
    >
      <Icon size={14} />
      {label}
    </button>
  );
}

function IntelWidget({ title, value, variant, icon: Icon, evidence }: { title: string, value: number, variant: string, icon: any, evidence: string }) {
  const colors = {
    success: 'var(--success)',
    danger: 'var(--danger)',
    warning: 'var(--warning)',
    default: 'var(--accent)',
  };
  return (
    <div className="p-5 rounded-3xl border transition-all hover:shadow-md min-w-0" style={{ backgroundColor: 'var(--surface-0)', borderColor: 'var(--border)' }}>
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest opacity-50 truncate">
          <Icon size={14} className="text-var(--accent) shrink-0" />
          <span className="truncate">{title}</span>
        </div>
        <span className="text-xl md:text-2xl font-black font-mono shrink-0" style={{ color: colors[variant as keyof typeof colors] || colors.default }}>
          {value}%
        </span>
      </div>
      <div className="text-[10px] opacity-40 truncate italic">Source: {evidence}</div>
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
