'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  TrendingUp, Activity, Scale, Wallet, DollarSign, Rocket, LayoutDashboard, Zap, ClipboardList, ChevronRight, ExternalLink, AlertTriangle, FileText, Gavel
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { Badge } from '@/components/ui/badge';
import { AnalysisResult } from '@/types';
import { useLanguage } from '@/lib/LanguageContext';
import { t } from '@/lib/i18n';
import { Reveal } from '@/components/motion';

function formatValue(val: number | string | null): string {
  if (val === null || val === undefined) return 'N/A';
  if (typeof val === 'string') return val;
  if (val === 0) return '0';
  const absVal = Math.abs(val);
  if (absVal >= 10000000) return (val / 10000000).toFixed(2) + ' Cr';
  if (absVal >= 100000) return (val / 100000).toFixed(2) + ' L';
  if (absVal >= 1000) return (val / 1000).toFixed(1) + ' K';
  return val.toLocaleString();
}

function KpiWidget({ label, value, unit = '', trend, variant = 'default', icon: Icon }: { label: string, value: number | string | null, unit?: string, trend?: string, variant?: 'default' | 'success' | 'danger', icon: any }) {
  const colors = {
    default: 'var(--text-primary, #000)',
    success: 'var(--success, #16a34a)',
    danger: 'var(--danger, #dc2626)',
  };
  return (
    <div className="p-5 rounded-3xl border bg-white transition-all hover:shadow-md group min-w-0" style={{ borderColor: 'var(--border, #e2e8f0)' }}>
      <div className="flex items-center justify-between mb-3">
        <div className="p-2 rounded-xl bg-slate-100 group-hover:bg-blue-50 transition-colors">
          <Icon size={16} style={{ color: 'var(--accent, #3b82f6)' }} />
        </div>
        {trend && <div className="text-[10px] font-bold flex items-center gap-1 text-green-600 truncate"><TrendingUp size={10} /> {trend}</div>}
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
        <div className="p-6 rounded-3xl border bg-slate-50 border-dashed flex flex-col gap-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase opacity-50"><Zap size={14} className="text-blue-600"/> Resource Inputs</div>
          <div className="flex flex-wrap gap-2">
            {blueprint.inputs.map(i => <Badge key={i} variant="secondary" className="text-[10px] px-2 py-0.5 rounded-lg">{i}</Badge>)}
          </div>
        </div>
        <div className="p-6 rounded-3xl border bg-slate-50 border-dashed flex flex-col gap-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase opacity-50"><Activity size={14} className="text-blue-600"/> Core Process</div>
          <div className="text-sm opacity-80 leading-relaxed">A deterministic operational cycle consisting of {blueprint.flow.length} synchronized stages.</div>
        </div>
        <div className="p-6 rounded-3xl border bg-slate-50 border-dashed flex flex-col gap-4">
          <div className="flex items-center gap-2 text-xs font-black uppercase opacity-50"><Rocket size={14} className="text-blue-600"/> Value Outputs</div>
          <div className="flex flex-wrap gap-2">
            {blueprint.outputs.map(o => <Badge key={o} variant="secondary" className="text-[10px] px-2 py-0.5 rounded-lg">{o}</Badge>)}
          </div>
        </div>
      </div>
      <div className="relative pl-10 space-y-6">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-600 via-slate-200 to-blue-600" />
        {blueprint.flow.map((step, i) => (
          <div key={i} className="relative group">
            <div className="absolute -left-7 top-1 w-6 h-6 rounded-full bg-white border-2 border-blue-600 flex items-center justify-center z-10 group-hover:scale-110 transition-transform">
              <span className="text-[10px] font-black text-blue-600">{i+1}</span>
            </div>
            <div className="p-4 rounded-2xl border bg-white group-hover:shadow-lg transition-all hover:border-blue-300">
              <div className="text-xs font-black text-blue-600 uppercase mb-1 tracking-widest">{step.step}</div>
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
        <div key={i} className="p-6 rounded-3xl border bg-white hover:shadow-lg transition-all group">
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-black uppercase tracking-tighter px-2 py-1 rounded-lg bg-blue-600 text-white">Week {week.week}</div>
            <div className="opacity-0 group-hover:opacity-100 transition-opacity"><ChevronRight size={16} className="text-blue-600"/></div>
          </div>
          <ul className="space-y-3">
            {week.tasks.map((task, j) => (
              <li key={j} className="text-xs flex items-start gap-3 opacity-80">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1 shrink-0" />
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
        <div key={i} className="flex items-center justify-between p-4 rounded-2xl border bg-slate-50 hover:bg-white transition-all">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-white border">
              <FileText size={14} className="text-blue-600" />
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
        <thead className="text-[10px] font-black uppercase opacity-50">
          <tr>
            <th className="pb-3 pl-4">Risk Factor</th>
            <th className="pb-3">Severity</th>
            <th className="pb-3">Probability</th>
            <th className="pb-3 pr-4">Mitigation Strategy</th>
          </tr>
        </thead>
        <tbody>
          {risks.map((r, i) => (
            <tr key={i} className="group bg-white hover:bg-slate-50 transition-colors">
              <td className="py-4 pl-4 rounded-l-2xl font-bold border-l-4 border-transparent group-hover:border-blue-600">{r.risk}</td>
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

  useEffect(() => {
    const stored = localStorage.getItem('analysis_result');
    const demo = localStorage.getItem('demo_data');
    const source = stored || demo;
    if (source) {
      try {
        const parsed: AnalysisResult = JSON.parse(source);
        setData(parsed);
      } catch (e) {
        console.error('Parsing error', e);
      }
    }
  }, [router]);

  const currencySymbol = data?.location?.currency?.symbol || '₹';
  const currentScenario = data?.scenarios ? (data.scenarios[activePreset] || data.scenarios['base']) : null;
  const annualProfit = currentScenario?.annual_net_cash_flow ?? null;
  const breakEven = currentScenario?.break_even_months ?? null;
  const roi = currentScenario?.roi_percent ?? null;

  const chartData = Array.from({ length: 12 }, (_, i) => ({
    month: `Mo ${i + 1}`,
    cash: Math.round((currentScenario?.monthly_net_cash_flow ?? 0) * (i + 1)),
  }));

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100 text-slate-900">
        <div className="text-center">
          <p className="text-xl font-bold">Waiting for data...</p>
          <p className="text-sm opacity-60">Please complete the analysis first.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 p-10">
      <h1 className="text-3xl font-black uppercase mb-10">{t(lang, 'report.title')}</h1>

      <Reveal>
        <div className="p-10 rounded-[40px] border bg-white shadow-xl relative overflow-hidden mb-10">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-4 flex flex-col items-center text-center">
              <div className="relative w-40 h-40 flex items-center justify-center mb-6">
                <svg width="160" height="160" className="rotate-[-90deg]">
                  <circle cx="80" cy="80" r="70" fill="none" stroke="#e2e8f0" strokeWidth="16" />
                  <motion.circle
                    cx="80" cy="80" r="70" fill="none" stroke="var(--accent, #3b82f6)" strokeWidth="16" strokeLinecap="round"
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
              <div className="text-2xl font-black leading-tight">{data.recommendation}</div>
            </div>
            <div className="lg:col-span-8 space-y-6">
              <div className="p-6 rounded-3xl bg-slate-50 border border-slate-200 relative">
                <div className="absolute -top-3 left-6 px-3 py-1 rounded-full bg-blue-600 text-white text-[10px] font-black uppercase">Analyst Reasoning</div>
                <p className="text-base opacity-80 leading-relaxed italic">
                  "{data.interpreter_reasoning}"
                </p>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <KpiWidget label="Total Capital" value={currentScenario?.setup_cost ?? data?.financials?.total_project_cost} unit={currencySymbol} icon={Wallet} />
                <KpiWidget label="Annual Net" value={annualProfit} unit={currencySymbol} variant="success" icon={TrendingUp} />
                <KpiWidget label="Break-even" value={breakEven} unit="Mo" variant="danger" icon={Activity} />
                <KpiWidget label="Projected ROI" value={roi} unit="%" variant="success" icon={Scale} />
              </div>
            </div>
          </div>
        </div>
      </Reveal>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-16">
        <div className="lg:col-span-7">
          <Reveal>
            <div className="p-8 rounded-[40px] border bg-white shadow-sm">
              <div className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-blue-50"><Rocket size={20} style={{ color: '#3b82f6' }} /></div>
                  <h2 className="text-xl font-black tracking-tight uppercase">Strategy Simulator</h2>
                </div>
                <div className="flex p-1 rounded-2xl bg-slate-100 border border-slate-200">
                  {(['conservative', 'base', 'optimistic'] as const).map(p => (
                    <button key={p} onClick={() => setActivePreset(p)} className={`px-4 py-1.5 text-[10px] font-bold uppercase rounded-xl transition-all ${activePreset === p ? 'bg-blue-600 text-white shadow-sm' : 'opacity-50 hover:opacity-100'}`}>
                      {p}
                    </button>
                  ))}
                </div>
              </div>
              <div className="h-64 w-full rounded-3xl border bg-slate-50 p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                    <XAxis dataKey="month" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} tickFormatter={(v) => `${currencySymbol}${v / 1000}k`} />
                    <Tooltip />
                    <Area type="monotone" dataKey="cash" stroke="#3b82f6" strokeWidth={3} fillOpacity={0.3} fill="#3b82f6" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Reveal>
        </div>
        <div className="lg:col-span-5 space-y-6">
          <Reveal>
            <div className="p-8 rounded-[40px] border bg-white shadow-sm h-full">
              <div className="flex items-center gap-3 mb-8">
                <div className="p-2 rounded-xl bg-slate-100"><LayoutDashboard size={20} style={{ color: '#3b82f6' }} /></div>
                <h2 className="text-xl font-black tracking-tight uppercase">Financial Breakdown</h2>
              </div>
              <div className="space-y-6">
                <div className="p-6 rounded-3xl bg-slate-50 border border-slate-200">
                  <div className="text-xs font-black uppercase opacity-50 mb-4 flex items-center gap-2">
                    <DollarSign size={14} className="text-green-600"/> Monthly Income
                  </div>
                  <div className="space-y-2">
                    {Object.entries(data.financials?.income_breakdown || {}).map(([key, val]: [string, any]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="opacity-60">{key}</span>
                        <span className="font-mono font-bold">{currencySymbol}{formatValue(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="p-6 rounded-3xl bg-slate-50 border border-slate-200">
                  <div className="text-xs font-black uppercase opacity-50 mb-4 flex items-center gap-2">
                    <Activity size={14} className="text-red-600"/> Monthly Expenditure
                  </div>
                  <div className="space-y-2">
                    {Object.entries(data.financials?.expenditure_breakdown || {}).map(([key, val]: [string, any]) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="opacity-60">{key}</span>
                        <span className="font-mono font-bold">{currencySymbol}{formatValue(val)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </div>

      <div className="mb-16">
        <Reveal>
          <div className="p-10 rounded-[40px] border bg-white shadow-sm">
            <div className="flex items-center gap-3 mb-12">
              <div className="p-2 rounded-xl bg-blue-50"><Zap size={20} style={{ color: '#3b82f6' }} /></div>
              <h2 className="text-2xl font-black tracking-tight uppercase">The Operational Blueprint</h2>
            </div>
            <OperationalFlow blueprint={data.business_blueprint} />
          </div>
        </Reveal>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
        <Reveal>
          <div className="p-10 rounded-[40px] border bg-white shadow-sm">
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2 rounded-xl bg-blue-50"><ClipboardList size={20} style={{ color: '#3b82f6' }} /></div>
              <h2 className="text-xl font-black tracking-tight uppercase">30-Day Launch Roadmap</h2>
            </div>
            <StartupTimeline roadmap={data.startup_roadmap} />
          </div>
        </Reveal>
        <Reveal>
          <div className="p-10 rounded-[40px] border bg-white shadow-sm">
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2 rounded-xl bg-blue-50"><Gavel size={20} style={{ color: '#3b82f6' }} /></div>
              <h2 className="text-xl font-black tracking-tight uppercase">Compliance & Licensing</h2>
            </div>
            <ComplianceGrid requirements={data.regulatory_requirements} />
          </div>
        </Reveal>
      </div>

      <div className="mb-16">
        <Reveal>
          <div className="p-10 rounded-[40px] border bg-white shadow-sm">
            <div className="flex items-center gap-3 mb-12">
              <div className="p-2 rounded-xl bg-blue-50"><Wallet size={20} style={{ color: '#3b82f6' }} /></div>
              <h2 className="text-2xl font-black tracking-tight uppercase">Strategic Funding Strategy</h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
              <div className="lg:col-span-1 space-y-6">
                <div className="p-6 rounded-3xl border bg-slate-50 shadow-sm">
                  <div className="text-xs font-black uppercase opacity-50 mb-4">Funding Mix</div>
                  <div className="h-6 w-full rounded-full overflow-hidden flex mb-6 bg-slate-200">
                    <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: '33%' }} title="Own Capital" />
                    <div className="h-full bg-emerald-500 transition-all duration-500" style={{ width: '33%' }} title="Govt Subsidy" />
                    <div className="h-full bg-amber-500 transition-all duration-500" style={{ width: '34%' }} title="External Loan" />
                  </div>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between opacity-80"><span>Own Contribution</span><span className="font-mono">{currencySymbol}{formatValue(data.financials?.user_capital)}</span></div>
                    <div className="flex justify-between text-emerald-500 font-bold"><span>Est. Subsidy</span><span className="font-mono">{currencySymbol}{formatValue(data.financials?.verified_subsidy)}</span></div>
                    <div className="flex justify-between border-t pt-2 font-black"><span>Financing Gap</span><span className="font-mono">{currencySymbol}{formatValue(data.financials?.financing_required)}</span></div>
                  </div>
                </div>
              </div>
              <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                {data.matchedSchemes?.map((scheme, i) => (
                  <div key={i} className="p-6 rounded-3xl border bg-slate-50 hover:border-blue-300 transition-all group">
                    <div className="flex justify-between items-start mb-4">
                      <h4 className="text-sm font-black">{scheme.name}</h4>
                      <Badge variant="secondary" className="text-[9px]">{scheme.ministry}</Badge>
                    </div>
                    <div className="text-xs opacity-80 mb-4 leading-relaxed">
                      Benefit: <span className="font-bold text-blue-600">{scheme.benefit.subsidyPercent}% subsidy</span> /
                      <span className="font-bold text-blue-600"> {currencySymbol}{formatValue(scheme.benefit.loanAmount)} max loan</span>
                    </div>
                    <a href={scheme.sourceUrl} target="_blank" className="text-[10px] font-black text-blue-600 flex items-center gap-1 group-hover:underline">
                      Official Portal <ExternalLink size={10} />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </Reveal>
      </div>

      <div className="mb-16">
        <Reveal>
          <div className="p-10 rounded-[40px] border bg-white shadow-sm">
            <div className="flex items-center gap-3 mb-12">
              <div className="p-2 rounded-xl bg-blue-50"><AlertTriangle size={20} style={{ color: '#3b82f6' }} /></div>
              <h2 className="text-2xl font-black tracking-tight uppercase">Risk Analysis & Mitigation</h2>
            </div>
            <RiskAnalysis risks={data.risk_matrix} />
          </div>
        </Reveal>
      </div>
    </div>
  );
}
