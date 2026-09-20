'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { getDemoScenario } from '@/lib/api';
import { FadeIn, Reveal, Stagger, HoverLift, MagneticButton } from '@/components/motion';
import Hero3DScene from '@/components/3d/Hero3DScene';
import Card3DTilt from '@/components/3d/Card3DTilt';
import ThreeDIcon from '@/components/3d/ThreeDIcons';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DEFAULT_CURRENCY_SYMBOL } from '@/lib/utils';
import {
  ArrowRight,
  Sparkles,
  MapPin,
  Calculator,
  ShieldCheck,
  FileText,
  TrendingUp,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Layers,
  Zap,
  Globe2,
  HelpCircle,
  Cpu,
  CheckCircle,
} from 'lucide-react';
import VoiceInput from '@/components/ui/VoiceInput';

export default function LandingPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [demoActiveTab, setDemoActiveTab] = useState<'dairy' | 'poultry' | 'retail'>('dairy');
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  const startNormalFlow = () => router.push('/profile');

  const loadDemo = async (scenarioId: string) => {
    setIsLoading(true);
    try {
      const data = await getDemoScenario(scenarioId);
      localStorage.setItem('demo_data', JSON.stringify(data));
      router.push('/report');
    } catch {
      alert('Failed to load demo scenario. Is the backend running?');
    } finally {
      setIsLoading(false);
    }
  };

  const demoScenarios = {
    dairy: {
      title: 'Dairy Farming Venture (10 Gir Cows)',
      location: 'Ramanagara, Karnataka',
      score: 84,
      verdict: 'Proceed with Modification',
      investment: `${DEFAULT_CURRENCY_SYMBOL}5,50,000`,
      subsidy: '25% (NABARD)',
      roi: '24.8%',
      breakeven: '18 Months',
    },
    poultry: {
      title: 'Commercial Broiler Poultry Unit',
      location: 'Namakkal, Tamil Nadu',
      score: 91,
      verdict: 'Proceed',
      investment: `${DEFAULT_CURRENCY_SYMBOL}8,20,000`,
      subsidy: '35% (PMEGP)',
      roi: '31.4%',
      breakeven: '14 Months',
    },
    retail: {
      title: 'Agro-Inputs & Bio-Fertilizer Store',
      location: 'Bareilly, Uttar Pradesh',
      score: 72,
      verdict: 'Proceed with Modification',
      investment: `${DEFAULT_CURRENCY_SYMBOL}3,00,000`,
      subsidy: '15% (MUDRA)',
      roi: '18.2%',
      breakeven: '22 Months',
    },
  };

  const coreFeatures = [
    {
      iconName: 'district' as const,
      variant: 'cyan' as const,
      title: 'Hyper-Local Geospatial Engine',
      desc: 'Deep regional proxies calibrated for 700+ Indian districts — assessing real footfall, road connectivity, and cluster density.',
      highlight: 'Geospatial Proxies',
    },
    {
      iconName: 'chart' as const,
      variant: 'blue' as const,
      title: 'Deterministic Math & ROI Logic',
      desc: 'Strictly zero hallucinated calculations. Project cost, cash flows, EMI, and payback horizons are computed with pure deterministic financial code.',
      highlight: '100% Auditable Code',
    },
    {
      iconName: 'scheme' as const,
      variant: 'emerald' as const,
      title: 'Verified Scheme Matching RAG',
      desc: 'Semantic retrieval across official NABARD, PMEGP, MUDRA, and state credit schemes with verifiable official source citations.',
      highlight: 'Source-Backed Citations',
    },
    {
      iconName: 'shield' as const,
      variant: 'purple' as const,
      title: 'Explainable Viability Scoring',
      desc: 'Understand exactly WHY a business succeeds or fails with structured risk parameters, market saturation tests, and actionable modifications.',
      highlight: 'Actionable Advice',
    },
  ];

  const steps = [
    {
      step: '01',
      title: 'Describe Your Venture',
      desc: 'Enter your business idea, seed capital, target investment, and location in your preferred language.',
      iconName: 'idea' as const,
      variant: 'blue' as const,
    },
    {
      step: '02',
      title: 'Contextual & Geospatial Synthesis',
      desc: 'Our data engine analyzes local demographic demand, competition saturation, and operational costs.',
      iconName: 'district' as const,
      variant: 'cyan' as const,
    },
    {
      step: '03',
      title: 'Deterministic Financial Modeling',
      desc: 'Simulate break-even months, debt burden, and profit margins under conservative, base, and optimistic scenarios.',
      iconName: 'capital' as const,
      variant: 'emerald' as const,
    },
    {
      step: '04',
      title: 'Scheme Financing & Strategic Report',
      desc: 'Receive an instant report with subsidy matches, loan structures, and concrete recommendations.',
      iconName: 'scheme' as const,
      variant: 'amber' as const,
    },
  ];

  const faqs = [
    {
      q: 'How does GramNirnay.ai calculate business viability without guessing?',
      a: 'We separate deterministic calculations from probabilistic AI. Financial numbers (cost, EMI, payback, ROI) are computed via strict Python financial algorithms. The AI engine is only used for qualitative reasoning and extracting structured business parameters.',
    },
    {
      q: 'Which government schemes are indexed in the platform?',
      a: 'We index major national and state-level subsidy schemes including PMEGP (Prime Minister Employment Generation Programme), NABARD Dairy Entrepreneurship Scheme, PM Mudra Yojana, AIF (Agriculture Infrastructure Fund), and state MSME subsidies.',
    },
    {
      q: 'Can rural entrepreneurs use GramNirnay in Hindi or other regional languages?',
      a: 'Yes. GramNirnay has full multilingual support (English, Hindi, and expanding regional languages) with seamless bilingual report summaries.',
    },
    {
      q: 'What makes hyper-local intelligence different from generic business plans?',
      a: 'Generic plans assume national averages. GramNirnay ingests district-level geospatial density, mandi proximity, power reliability, raw material availability, and existing competitor density to reflect realistic rural market conditions.',
    },
  ];

  return (
    <div
      className="relative min-h-screen overflow-hidden"
      style={{ backgroundColor: 'var(--surface-0)', color: 'var(--text-primary)' }}
    >
      {/* ── Background Subtle Grid & Rich Ambient Mesh Gradients ── */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden="true">
        <div
          className="absolute inset-0 opacity-[0.25]"
          style={{
            backgroundImage: 'url(/media/grid-pattern.svg)',
            backgroundSize: '320px 320px',
            backgroundRepeat: 'repeat',
            color: 'var(--text-muted)',
          }}
        />
        {/* Top-Right Vibrant Indigo-Cyan Aurora */}
        <div
          className="absolute top-[-15%] right-[-5%] w-[900px] h-[800px] rounded-full blur-[120px] opacity-45"
          style={{
            background: 'radial-gradient(circle, color-mix(in srgb, #3b82f6 28%, transparent) 0%, color-mix(in srgb, #06b6d4 15%, transparent) 45%, transparent 70%)',
          }}
        />
        {/* Center Accent Glow */}
        <div
          className="absolute top-[35%] left-[20%] w-[700px] h-[600px] rounded-full blur-[140px] opacity-25"
          style={{
            background: 'radial-gradient(circle, color-mix(in srgb, #6366f1 22%, transparent) 0%, transparent 65%)',
          }}
        />
        {/* Bottom-Left Emerald Glow */}
        <div
          className="absolute bottom-[-10%] left-[-5%] w-[750px] h-[750px] rounded-full blur-[120px] opacity-30"
          style={{
            background: 'radial-gradient(circle, color-mix(in srgb, #10b981 18%, transparent) 0%, transparent 70%)',
          }}
        />
      </div>

      {/* ────────────────────────────────────────────────────────
          HERO SECTION — 2-COLUMN BALANCED LAYOUT (NO OVERLAP)
      ──────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-16 min-h-[88vh] flex items-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center w-full">
          
          {/* Left Column: Headlines & CTAs */}
          <div className="lg:col-span-7 space-y-8 text-left">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            >
              {/* Brand Title with Gradient AI */}
              <h1 className="text-5xl sm:text-6xl md:text-7xl xl:text-8xl font-black tracking-tighter leading-none mb-6">
                GramNirnay<span className="ai-gradient-text font-black">.ai</span>
              </h1>

              {/* Subtitle & Value Proposition */}
              <p className="text-xl sm:text-2xl font-bold tracking-tight text-[var(--text-primary)] mb-4">
                Hyper-Local Business Intelligence for Rural Micro-Entrepreneurs.
              </p>
              
              <p className="text-base sm:text-lg font-medium text-[var(--text-secondary)] leading-relaxed max-w-2xl">
                Validate real business viability &amp; unlock verified government credit subsidies before investing your hard-earned capital.
              </p>
            </motion.div>

            {/* CTAs */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 pt-2"
            >
              <MagneticButton
                onClick={startNormalFlow}
                className="px-8 py-4 text-base font-bold rounded-full text-white shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center gap-3 cursor-pointer"
                style={{ backgroundColor: 'var(--accent)' }}
                strength={0.15}
              >
                <span>Start Business Analysis</span>
                <ArrowRight size={18} />
              </MagneticButton>

              <motion.button
                onClick={() => loadDemo('2')}
                disabled={isLoading}
                className="px-7 py-4 text-base font-semibold rounded-full border transition-all duration-[var(--duration-base)] disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer shadow-xs"
                style={{
                  backgroundColor: 'var(--surface-0)',
                  borderColor: 'var(--border-strong)',
                  color: 'var(--text-primary)',
                }}
                whileHover={{
                  backgroundColor: 'var(--surface-2)',
                  y: -2,
                  boxShadow: 'var(--shadow-sm)',
                }}
                whileTap={{ scale: 0.98 }}
              >
                <AnimatePresence mode="wait">
                  {isLoading ? (
                    <motion.span
                      key="loading"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center gap-2"
                    >
                      <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                      </svg>
                      Simulating…
                    </motion.span>
                  ) : (
                    <motion.span key="idle" className="flex items-center gap-2">
                      <Sparkles size={16} className="text-[var(--accent)]" />
                      Explore Live Demo
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            </motion.div>

            {/* Quick Stats Strip */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35, duration: 0.6 }}
              className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-[var(--border)]"
            >
              {[
                { val: '750+', label: 'Districts Mapped' },
                { val: '100%', label: 'Deterministic Math' },
                { val: `${DEFAULT_CURRENCY_SYMBOL}50Cr+`, label: 'Subsidies Indexed' },
                { val: '< 2.5s', label: 'Report Speed' },
              ].map((m, i) => (
                <div key={i} className="text-left">
                  <div className="text-2xl font-black font-mono text-[var(--accent)]">{m.val}</div>
                  <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)] mt-0.5">{m.label}</div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Right Column: Natural Floating 3D Interactive Scene (No Card Box) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.15, duration: 0.8 }}
            className="lg:col-span-5 relative flex items-center justify-center min-h-[480px] w-full"
          >
            {/* Ambient Radial Gradient Aura behind 3D Scene */}
            <div
              className="absolute inset-0 rounded-full blur-3xl opacity-60 pointer-events-none"
              style={{
                background: 'radial-gradient(circle at center, color-mix(in srgb, var(--accent) 25%, transparent) 0%, color-mix(in srgb, #6366f1 18%, transparent) 50%, transparent 75%)',
              }}
            />

            {/* Seamless 3D Canvas */}
            <div className="relative w-full h-[480px] flex items-center justify-center">
              <Hero3DScene className="w-full h-full" />
            </div>
          </motion.div>

        </div>
      </section>

      {/* ────────────────────────────────────────────────────────
          VOICE-FIRST ANALYSIS QUICK START
      ──────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-20 border-t border-[var(--border)]">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <Reveal>
              <span className="text-xs font-bold uppercase tracking-widest text-[var(--accent)] mb-2 block">
                Inclusive Interface
              </span>
              <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4">
                Speak Your Vision <span className="ai-gradient-text">Directly</span>
              </h2>
              <p className="text-base text-[var(--text-secondary)] leading-relaxed">
                No typing required. Describe your business idea in your local dialect, and our intelligence pipeline will handle the translation and analysis.
              </p>
            </Reveal>
            <div className="flex items-center gap-4 text-sm font-medium text-[var(--text-muted)]">
              <div className="flex items-center gap-1.5">
                <CheckCircle size={14} className="text-[var(--success)]" /> Support for Regional Dialects
              </div>
              <div className="flex items-center gap-1.5">
                <CheckCircle size={14} className="text-[var(--success)]" /> Instant Transcription
              </div>
            </div>
          </div>
          <div className="flex justify-center">
            <VoiceInput />
          </div>
        </div>
      </section>

      {/* ────────────────────────────────────────────────────────
          INTERACTIVE LIVE DEMO PREVIEW SECTION
      ──────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-20 border-t border-[var(--border)]">
        <Reveal>
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--accent)] mb-2 block">
              Real-Time Simulation
            </span>
            <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4">
              See How GramNirnay Analyzes A Venture
            </h2>
            <p className="text-base text-[var(--text-secondary)]">
              Select a real rural micro-enterprise scenario below to see the instant viability assessment and scheme match.
            </p>
          </div>
        </Reveal>

        {/* Tab Controls */}
        <div className="flex justify-center mb-8">
          <div className="flex p-1.5 rounded-2xl border bg-[var(--surface-1)] border-[var(--border)] gap-1 shadow-xs">
            {(['dairy', 'poultry', 'retail'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setDemoActiveTab(tab)}
                className={`relative px-5 py-2 text-xs sm:text-sm font-bold uppercase tracking-wider rounded-xl transition-all duration-300 capitalize cursor-pointer ${
                  demoActiveTab === tab
                    ? 'text-white shadow-sm'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
                style={{
                  backgroundColor: demoActiveTab === tab ? 'var(--accent)' : 'transparent',
                }}
              >
                {tab} Venture
              </button>
            ))}
          </div>
        </div>

        {/* 3D Tilted Interactive Card Showcase (Gentle Tilt) */}
        <Card3DTilt intensity={3} glareOpacity={0.08}>
          <div
            className="rounded-3xl border p-6 sm:p-10 backdrop-blur-xl relative overflow-hidden shadow-xl"
            style={{
              backgroundColor: 'var(--surface-0)',
              borderColor: 'var(--border)',
            }}
          >
            {/* Top Accent line */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-emerald-500" />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
              {/* Left Details */}
              <div className="lg:col-span-7 space-y-6">
                <div className="flex items-center gap-3">
                  <Badge variant="outline" className="text-xs font-semibold px-3 py-1 bg-[var(--accent-subtle)] text-[var(--accent)] border-[var(--accent)]/30">
                    Live Case Study
                  </Badge>
                  <span className="text-xs font-medium text-[var(--text-muted)] flex items-center gap-1">
                    <MapPin size={12} /> {demoScenarios[demoActiveTab].location}
                  </span>
                </div>

                <h3 className="text-2xl sm:text-3xl font-black tracking-tight text-[var(--text-primary)]">
                  {demoScenarios[demoActiveTab].title}
                </h3>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3.5 rounded-2xl bg-[var(--surface-1)] border border-[var(--border)]">
                    <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Project Cost</div>
                    <div className="text-lg font-black text-[var(--text-primary)] font-mono">{demoScenarios[demoActiveTab].investment}</div>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-[var(--surface-1)] border border-[var(--border)]">
                    <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Top Subsidy</div>
                    <div className="text-lg font-black text-[var(--success)] font-mono">{demoScenarios[demoActiveTab].subsidy}</div>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-[var(--surface-1)] border border-[var(--border)]">
                    <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Annual ROI</div>
                    <div className="text-lg font-black text-[var(--accent)] font-mono">{demoScenarios[demoActiveTab].roi}</div>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-[var(--surface-1)] border border-[var(--border)]">
                    <div className="text-[10px] font-bold uppercase text-[var(--text-muted)]">Break-Even</div>
                    <div className="text-lg font-black text-[var(--text-primary)] font-mono">{demoScenarios[demoActiveTab].breakeven}</div>
                  </div>
                </div>

                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  Financial calculations account for state electricity tariffs, raw feed logistics, local mandi price indices, and eligible credit subsidies under Government of India schemes.
                </p>

                <div className="pt-2 flex flex-wrap gap-4">
                  <Button
                    variant="primary"
                    onClick={() => loadDemo('2')}
                    className="gap-2 rounded-2xl px-6 h-11 cursor-pointer"
                  >
                    Open Full Report Analysis <ArrowRight size={16} />
                  </Button>
                </div>
              </div>

              {/* Right Viability Gauge Badge */}
              <div className="lg:col-span-5 flex flex-col items-center justify-center p-6 rounded-3xl bg-[var(--surface-1)] border border-[var(--border)] text-center">
                <div className="text-[11px] font-bold uppercase tracking-widest text-[var(--text-muted)] mb-3">
                  Computed Viability Score
                </div>

                <div className="relative w-36 h-36 flex items-center justify-center my-2">
                  <svg width="140" height="140" className="rotate-[-90deg]">
                    <circle cx="70" cy="70" r="55" fill="none" stroke="var(--surface-3)" strokeWidth="10" />
                    <circle
                      cx="70" cy="70" r="55"
                      fill="none"
                      stroke={demoScenarios[demoActiveTab].score > 80 ? 'var(--success)' : 'var(--warning)'}
                      strokeWidth="10"
                      strokeLinecap="round"
                      strokeDasharray={2 * Math.PI * 55}
                      strokeDashoffset={2 * Math.PI * 55 * (1 - demoScenarios[demoActiveTab].score / 100)}
                      className="transition-all duration-700 ease-out"
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-4xl font-black font-mono">{demoScenarios[demoActiveTab].score}</span>
                    <span className="text-xs text-[var(--text-muted)] font-bold">/100</span>
                  </div>
                </div>

                <Badge
                  variant={demoScenarios[demoActiveTab].score > 80 ? 'success' : 'warning'}
                  className="mt-3 px-4 py-1 text-xs font-bold uppercase tracking-wider"
                >
                  {demoScenarios[demoActiveTab].verdict}
                </Badge>

                <span className="text-xs text-[var(--text-muted)] mt-4">
                  Verified with 14 Hyper-Local Indicators
                </span>
              </div>
            </div>
          </div>
        </Card3DTilt>
      </section>

      {/* ────────────────────────────────────────────────────────
          CORE 3D ARCHITECTURAL FEATURES GRID
      ──────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-20">
        <Reveal>
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--accent)] mb-2 block">
              Architectural Rigor
            </span>
            <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4">
              Built On Deterministic Science, Not AI Guesses
            </h2>
            <p className="text-base text-[var(--text-secondary)]">
              GramNirnay strictly decouples quantitative arithmetic from qualitative reasoning to deliver trustworthy decisions.
            </p>
          </div>
        </Reveal>

        <Stagger stagger={0.1} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {coreFeatures.map((feat, i) => (
            <Card3DTilt key={i} intensity={3}>
              <div
                className="h-full p-8 rounded-3xl border backdrop-blur-md relative overflow-hidden transition-all group flex flex-col justify-between shadow-xs"
                style={{
                  backgroundColor: 'var(--surface-0)',
                  borderColor: 'var(--border)',
                }}
              >
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <ThreeDIcon name={feat.iconName} variant={feat.variant} size="lg" />
                    <Badge variant="secondary" className="text-[10px] font-bold uppercase tracking-wider">
                      {feat.highlight}
                    </Badge>
                  </div>

                  <h3 className="text-xl font-bold tracking-tight mb-3 text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors">
                    {feat.title}
                  </h3>

                  <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                    {feat.desc}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-[var(--border)] flex items-center justify-between text-xs font-semibold text-[var(--text-muted)] group-hover:text-[var(--accent)] transition-colors">
                  <span>Explore Architecture</span>
                  <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Card3DTilt>
          ))}
        </Stagger>
      </section>

      {/* ────────────────────────────────────────────────────────
          "HOW IT WORKS" 4-STEP JOURNEY
      ──────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-20 border-t border-[var(--border)]">
        <Reveal>
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--accent)] mb-2 block">
              Simple 4-Step Process
            </span>
            <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4">
              From Idea to Bankable Project Report
            </h2>
            <p className="text-base text-[var(--text-secondary)]">
              A guided experience engineered for clarity, speed, and real financial readiness.
            </p>
          </div>
        </Reveal>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((s, idx) => (
            <Reveal key={s.step} delay={idx * 0.08}>
              <div
                className="p-7 rounded-3xl border bg-[var(--surface-0)] border-[var(--border)] shadow-xs hover:shadow-sm transition-all h-full flex flex-col justify-between relative group"
              >
                <div>
                  <div className="flex items-center justify-between mb-5">
                    <ThreeDIcon name={s.iconName} variant={s.variant} size="md" />
                    <span className="text-2xl font-black font-mono text-[var(--text-muted)] opacity-60">
                      {s.step}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold tracking-tight mb-2 text-[var(--text-primary)]">
                    {s.title}
                  </h3>

                  <p className="text-xs sm:text-sm text-[var(--text-secondary)] leading-relaxed">
                    {s.desc}
                  </p>
                </div>

                <div className="mt-6 flex items-center gap-1.5 text-xs font-bold text-[var(--accent)]">
                  <CheckCircle2 size={14} /> Ready in Step {idx + 1}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ────────────────────────────────────────────────────────
          FREQUENTLY ASKED QUESTIONS
      ──────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 py-20 border-t border-[var(--border)]">
        <Reveal>
          <div className="text-center mb-14">
            <span className="text-xs font-bold uppercase tracking-widest text-[var(--accent)] mb-2 block">
              Transparency &amp; Trust
            </span>
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight mb-3">
              Frequently Asked Questions
            </h2>
            <p className="text-sm text-[var(--text-secondary)]">
              Everything you need to know about our data models and methodology.
            </p>
          </div>
        </Reveal>

        <div className="space-y-4">
          {faqs.map((faq, i) => {
            const isOpen = activeFaq === i;
            return (
              <Reveal key={i} delay={i * 0.04}>
                <div
                  onClick={() => setActiveFaq(isOpen ? null : i)}
                  className="rounded-2xl border p-6 bg-[var(--surface-0)] border-[var(--border)] shadow-xs hover:border-[var(--border-strong)] transition-all cursor-pointer"
                >
                  <div className="flex items-center justify-between gap-4">
                    <h3 className="text-base font-bold text-[var(--text-primary)] flex items-center gap-3">
                      <HelpCircle size={18} className="text-[var(--accent)] shrink-0" />
                      {faq.q}
                    </h3>
                    <ChevronRight
                      size={18}
                      className={`text-[var(--text-muted)] transition-transform duration-300 shrink-0 ${
                        isOpen ? 'rotate-90 text-[var(--accent)]' : ''
                      }`}
                    />
                  </div>
                  <AnimatePresence>
                    {isOpen && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.25 }}
                        className="overflow-hidden"
                      >
                        <p className="mt-4 text-sm text-[var(--text-secondary)] leading-relaxed border-t border-[var(--border)] pt-4">
                          {faq.a}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </Reveal>
            );
          })}
        </div>
      </section>

      {/* ────────────────────────────────────────────────────────
          FINAL HIGH-IMPACT 3D CTA BANNER
      ──────────────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-20">
        <Card3DTilt intensity={2}>
          <div
            className="rounded-3xl border p-8 sm:p-14 text-center relative overflow-hidden shadow-xl backdrop-blur-xl"
            style={{
              backgroundColor: 'var(--surface-0)',
              borderColor: 'var(--border)',
            }}
          >
            {/* Ambient inner glow */}
            <div
              className="absolute inset-0 pointer-events-none opacity-40"
              style={{
                background: 'radial-gradient(circle at center, color-mix(in srgb, var(--accent) 20%, transparent) 0%, transparent 70%)',
              }}
            />

            <div className="relative z-10 max-w-2xl mx-auto">
              <ThreeDIcon name="sparkles" variant="indigo" size="xl" className="mx-auto mb-6" />

              <h2 className="text-3xl sm:text-5xl font-black tracking-tight mb-4 text-[var(--text-primary)]">
                Ready to Launch Your Micro-Enterprise?
              </h2>

              <p className="text-base text-[var(--text-secondary)] mb-8 leading-relaxed">
                Analyze local market viability, simulate live financial outcomes, and discover matching credit subsidies in under 3 minutes.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={startNormalFlow}
                  className="w-full sm:w-auto px-10 h-13 text-base font-bold rounded-full gap-2 shadow-xl hover:shadow-2xl cursor-pointer"
                >
                  Start Your Analysis Now <ArrowRight size={18} />
                </Button>
              </div>
            </div>
          </div>
        </Card3DTilt>
      </section>

      {/* ────────────────────────────────────────────────────────
          FOOTER
      ──────────────────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-[var(--border)] py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-6 text-xs text-[var(--text-muted)] font-medium">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 rounded-md bg-[var(--accent)] text-white text-xs font-black flex items-center justify-center">
              G
            </div>
            <span className="font-bold text-[var(--text-primary)]">GramNirnay<span className="ai-gradient-text">.ai</span></span>
            <span>— Rural Decision Intelligence</span>
          </div>

          <div className="flex items-center gap-6 font-mono text-[11px] uppercase tracking-wider">
            <span>Deterministic Math</span>
            <span>•</span>
            <span>pgvector RAG</span>
            <span>•</span>
            <span>Open Data Proxies</span>
          </div>

          <div>
            © 2026 GramNirnay.ai. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
