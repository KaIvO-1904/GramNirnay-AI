'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useApp, FontSize, AnalysisHistoryItem } from '@/lib/AppContext';
import { useLanguage } from '@/lib/LanguageContext';
import { useTheme } from '@/lib/ThemeContext';
import { FadeIn, Reveal, Stagger } from '@/components/motion';
import Card3DTilt from '@/components/3d/Card3DTilt';
import ThreeDIcon from '@/components/3d/ThreeDIcons';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Image from 'next/image';
import {
  User,
  History,
  Sliders,
  Shield,
  LogOut,
  Sparkles,
  ArrowRight,
  Trash2,
  Download,
  Eye,
  Type,
  SunMoon,
  Volume2,
  CheckCircle2,
  MapPin,
  Calendar,
  Layers,
  TrendingUp,
  Award,
  DollarSign,
  PlusCircle,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  LogIn,
  Search,
} from 'lucide-react';

export default function AccountPage() {
  const router = useRouter();
  const { lang, setLang } = useLanguage();
  const { theme, toggleTheme } = useTheme();
  const {
    user,
    signInWithGoogle,
    signOut,
    fontSize,
    setFontSize,
    highContrast,
    setHighContrast,
    reducedMotion,
    setReducedMotion,
    history,
    deleteHistoryItem,
    clearHistory,
  } = useApp();

  const [activeTab, setActiveTab] = useState<'history' | 'settings' | 'data'>('history');
  const [audioAssistance, setAudioAssistance] = useState(false);
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleGoogleSignIn = async () => {
    setIsSigningIn(true);
    try {
      await signInWithGoogle();
    } finally {
      setIsSigningIn(false);
    }
  };

  const handleOpenReport = (item: AnalysisHistoryItem) => {
    if (item.data) {
      localStorage.setItem('analysis_result', JSON.stringify(item.data));
    } else {
      localStorage.setItem(
        'demo_data',
        JSON.stringify({
          viabilityScore: item.score,
          recommendation: item.recommendation,
          marketAnalysis: {
            demand: 82,
            competition: 45,
            accessibility: 78,
            seasonality: 20,
            source: 'Regional Agri-Census & Mandi Indices',
            confidence: 'High (0.89)',
          },
          financials: {
            total_project_cost: item.projectCost,
            financing_required: Math.round(item.projectCost * 0.7),
            monthly_revenue: Math.round(item.projectCost * 0.18),
            monthly_expenses: Math.round(item.projectCost * 0.08),
            monthly_emi: Math.round(item.projectCost * 0.02),
            monthly_net_profit: Math.round(item.projectCost * 0.08),
            annual_net_profit: Math.round(item.projectCost * 0.96),
            roi_percent: 24.5,
            break_even_months: 16,
            is_viable: true,
          },
          interpreter_reasoning: `Analysis based on regional demand and supply channels in ${item.district}, ${item.state}.`,
          modifications: [
            'Optimize procurement cycles to minimize initial capital drag.',
            'Connect with local cluster cooperatives for bulk discount on inputs.',
          ],
          matchedSchemes: [
            {
              schemeId: 'nabard-rural',
              name: 'NABARD Rural Micro-Enterprise Development Scheme',
              ministry: 'Ministry of Agriculture & Rural Development',
              benefit: { subsidyPercent: 25, loanAmount: item.projectCost * 0.75 },
              sourceUrl: 'https://www.nabard.org',
              eligibility: { minCapital: 50000, maxCapital: 2500000, categories: ['General', 'OBC', 'SC/ST'] },
            },
          ],
        })
      );
    }
    router.push('/report');
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(history, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `gramnirnay_analysis_history_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const filteredHistory = history.filter(
    (item) =>
      item.businessIdea.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.district.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.state.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalEvaluations = history.length;
  const avgViability = totalEvaluations > 0 ? Math.round(history.reduce((a, b) => a + b.score, 0) / totalEvaluations) : 0;
  const totalCapital = history.reduce((a, b) => a + (b.projectCost || 0), 0);

  return (
    <div
      className="min-h-screen pt-24 pb-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden"
      style={{ backgroundColor: 'var(--surface-0)', color: 'var(--text-primary)' }}
    >
      {/* ── Ambient Background Mesh Gradients (Matching Landing Page) ── */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden="true">
        <div
          className="absolute inset-0 opacity-[0.22]"
          style={{
            backgroundImage: 'url(/media/grid-pattern.svg)',
            backgroundSize: '320px 320px',
            backgroundRepeat: 'repeat',
            color: 'var(--text-muted)',
          }}
        />
        <div
          className="absolute top-[-10%] right-[-5%] w-[800px] h-[750px] rounded-full blur-[130px] opacity-35"
          style={{
            background: 'radial-gradient(circle, color-mix(in srgb, #3b82f6 24%, transparent) 0%, color-mix(in srgb, #06b6d4 15%, transparent) 50%, transparent 70%)',
          }}
        />
        <div
          className="absolute bottom-[-10%] left-[-5%] w-[750px] h-[750px] rounded-full blur-[140px] opacity-30"
          style={{
            background: 'radial-gradient(circle, color-mix(in srgb, #6366f1 20%, transparent) 0%, transparent 65%)',
          }}
        />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto space-y-8">
        
        {/* ─────────────────────────────────────────
            USER PROFILE & GOOGLE AUTHENTICATION HERO
        ───────────────────────────────────────── */}
        <FadeIn duration={0.6}>
          <div
            className="rounded-3xl border p-7 sm:p-9 relative overflow-hidden backdrop-blur-2xl shadow-xl transition-all"
            style={{
              backgroundColor: 'var(--surface-1)',
              borderColor: 'var(--border)',
            }}
          >
            {/* Top Multi-Color Aurora Strip */}
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400" />

            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8 relative z-10">
              
              {/* Profile Identity */}
              {user ? (
                /* Authenticated User Profile derived from Google */
                <div className="flex items-center gap-5">
                  <div className="relative w-20 h-20 rounded-3xl overflow-hidden border-2 border-blue-400/50 shadow-lg shrink-0 bg-[var(--surface-2)]">
                    <Image
                      src={user.avatar}
                      alt={user.name}
                      fill
                      unoptimized
                      className="object-cover"
                    />
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2.5 mb-1">
                      <h2 className="text-2xl sm:text-3xl font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                        {user.name}
                      </h2>
                      <Badge variant="success" className="text-[10px] font-bold px-2.5 py-0.5 shadow-xs">
                        <CheckCircle2 size={12} className="mr-1" /> Google Verified
                      </Badge>
                    </div>
                    <p className="text-sm font-medium text-[var(--text-secondary)]">{user.email}</p>
                    <div className="flex items-center gap-2 mt-2 text-xs font-semibold text-[var(--accent)]">
                      <Sparkles size={13} />
                      <span>Authenticated Google Account</span>
                    </div>
                  </div>
                </div>
              ) : (
                /* Guest State (No Hardcoded Names) */
                <div className="flex items-center gap-5">
                  <ThreeDIcon name="building" size="xl" variant="indigo" />
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h2 className="text-2xl sm:text-3xl font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                        Guest Session
                      </h2>
                      <Badge variant="secondary" className="text-[10px] font-bold">
                        Local Storage Active
                      </Badge>
                    </div>
                    <p className="text-sm text-[var(--text-secondary)] max-w-lg leading-relaxed">
                      Sign in with your Google account to automatically sync reports across devices, unlock government subsidy matching, and export certified dossiers.
                    </p>
                  </div>
                </div>
              )}

              {/* Action: Google Sign-In Prompt or Sign Out */}
              <div className="shrink-0 w-full sm:w-auto">
                {user ? (
                  <Button
                    variant="outline"
                    onClick={signOut}
                    className="w-full sm:w-auto gap-2 rounded-2xl text-xs font-bold hover:text-red-500 hover:border-red-500/50 px-5 h-11 cursor-pointer"
                  >
                    <LogOut size={15} />
                    Sign Out Account
                  </Button>
                ) : (
                  <button
                    onClick={handleGoogleSignIn}
                    disabled={isSigningIn}
                    className="w-full sm:w-auto flex items-center justify-center gap-3 px-8 py-3.5 rounded-2xl font-bold text-sm shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] cursor-pointer bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 text-zinc-900 dark:text-zinc-50"
                  >
                    {/* Official Google SVG Logo */}
                    <svg width="19" height="19" viewBox="0 0 24 24">
                      <path
                        fill="#4285F4"
                        d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17Z"
                      />
                      <path
                        fill="#34A853"
                        d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.36 24 12 24Z"
                      />
                      <path
                        fill="#FBBC05"
                        d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15Z"
                      />
                      <path
                        fill="#EA4335"
                        d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.36 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98Z"
                      />
                    </svg>
                    <span>{isSigningIn ? 'Connecting to Google…' : 'Sign in with Google'}</span>
                  </button>
                )}
              </div>
            </div>

            {/* Quick Metrics Bar on Profile Header */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-6 mt-6 border-t border-[var(--border)]">
              <div className="p-4 rounded-2xl bg-[var(--surface-0)] border border-[var(--border)]">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1.5 mb-1">
                  <History size={13} className="text-[var(--accent)]" /> Total Analyses
                </div>
                <div className="text-2xl font-black font-mono" style={{ color: 'var(--text-primary)' }}>
                  {totalEvaluations}
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-[var(--surface-0)] border border-[var(--border)]">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1.5 mb-1">
                  <TrendingUp size={13} className="text-[var(--success)]" /> Average Score
                </div>
                <div className="text-2xl font-black font-mono text-[var(--success)]">
                  {avgViability > 0 ? `${avgViability}/100` : '—'}
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-[var(--surface-0)] border border-[var(--border)] col-span-2 sm:col-span-1">
                <div className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] flex items-center gap-1.5 mb-1">
                  <DollarSign size={13} className="text-[var(--accent)]" /> Capital Modeled
                </div>
                <div className="text-2xl font-black font-mono" style={{ color: 'var(--text-primary)' }}>
                  {totalCapital > 0 ? `₹${(totalCapital / 100000).toFixed(1)} Lakhs` : '₹0'}
                </div>
              </div>
            </div>
          </div>
        </FadeIn>

        {/* ─────────────────────────────────────────
            NAVIGATION TABS
        ───────────────────────────────────────── */}
        <div className="flex border-b border-[var(--border)] gap-2 pb-1 overflow-x-auto">
          {[
            { id: 'history', label: 'Analysis History', icon: History, count: history.length },
            { id: 'settings', label: 'Accessibility & Display', icon: Sliders },
            { id: 'data', label: 'Data Security & Export', icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`relative flex items-center gap-2.5 px-6 py-3 text-sm font-bold transition-all border-b-2 cursor-pointer shrink-0 ${
                  isActive
                    ? 'border-[var(--accent)] text-[var(--accent)]'
                    : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-[var(--surface-2)] text-[var(--text-muted)] font-mono font-bold">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* ─────────────────────────────────────────
            TAB 1: ANALYSIS HISTORY
        ───────────────────────────────────────── */}
        {activeTab === 'history' && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h3 className="text-xl font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                  Saved Enterprise Evaluations
                </h3>
                <p className="text-xs text-[var(--text-muted)] mt-0.5">
                  Reload previously generated deterministic viability models.
                </p>
              </div>

              {history.length > 0 && (
                <div className="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-end">
                  <div className="relative w-full sm:w-64">
                    <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
                    <input
                      type="text"
                      placeholder="Search evaluations…"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-9 pr-4 py-2 rounded-xl text-xs bg-[var(--surface-1)] border border-[var(--border)] focus:border-[var(--accent)] focus:outline-none"
                    />
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExportJSON}
                    className="text-xs gap-1.5 rounded-xl font-bold shrink-0 cursor-pointer"
                  >
                    <Download size={14} /> Export JSON
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearHistory}
                    className="text-xs text-red-500 hover:text-red-600 gap-1.5 font-bold shrink-0 cursor-pointer"
                  >
                    <Trash2 size={14} /> Clear
                  </Button>
                </div>
              )}
            </div>

            {filteredHistory.length > 0 ? (
              <div className="grid grid-cols-1 gap-4">
                {filteredHistory.map((item) => (
                  <div
                    key={item.id}
                    className="p-6 rounded-3xl border bg-[var(--surface-1)] border-[var(--border)] shadow-xs hover:shadow-md hover:border-[var(--border-strong)] transition-all flex flex-col md:flex-row justify-between items-start md:items-center gap-5 group"
                  >
                    <div className="space-y-2.5">
                      <div className="flex flex-wrap items-center gap-3">
                        <span className="text-lg font-black group-hover:text-[var(--accent)] transition-colors" style={{ color: 'var(--text-primary)' }}>
                          {item.businessIdea}
                        </span>
                        <Badge
                          variant={item.score > 80 ? 'success' : item.score > 60 ? 'warning' : 'danger'}
                          className="text-xs font-bold px-3 py-0.5 font-mono shadow-xs"
                        >
                          {item.score}/100 Viability
                        </Badge>
                      </div>

                      <div className="flex flex-wrap items-center gap-4 text-xs text-[var(--text-muted)] font-medium">
                        <span className="flex items-center gap-1.5 font-semibold text-[var(--text-secondary)]">
                          <MapPin size={13} className="text-[var(--accent)]" /> {item.district}, {item.state}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <Calendar size={13} /> {item.date}
                        </span>
                        <span className="font-mono font-bold px-2.5 py-0.5 rounded-lg bg-[var(--surface-0)] border border-[var(--border)] text-[var(--text-primary)]">
                          ₹{item.projectCost?.toLocaleString()} Project Cost
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 w-full md:w-auto justify-end pt-2 md:pt-0 border-t md:border-t-0 border-[var(--border)]">
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleOpenReport(item)}
                        className="gap-2 rounded-xl px-5 h-10 font-bold shadow-md cursor-pointer"
                      >
                        <Eye size={15} /> Open Report
                      </Button>
                      <button
                        onClick={() => deleteHistoryItem(item.id)}
                        className="p-2.5 rounded-xl hover:bg-red-500/10 text-[var(--text-muted)] hover:text-red-500 transition-colors cursor-pointer"
                        title="Delete from history"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-20 border rounded-3xl bg-[var(--surface-1)] border-[var(--border)]">
                <ThreeDIcon name="chart" size="xl" variant="blue" className="mx-auto mb-4" />
                <h4 className="text-xl font-bold mb-2">No Evaluations Saved Yet</h4>
                <p className="text-sm text-[var(--text-secondary)] max-w-sm mx-auto mb-6">
                  Complete a business questionnaire to automatically generate and save your viability analysis report here.
                </p>
                <Button variant="primary" onClick={() => router.push('/profile')} className="rounded-2xl px-7 cursor-pointer">
                  Start New Analysis
                </Button>
              </div>
            )}
          </motion.div>
        )}

        {/* ─────────────────────────────────────────
            TAB 2: ACCESSIBILITY & DISPLAY SETTINGS
        ───────────────────────────────────────── */}
        {activeTab === 'settings' && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            {/* Font Size Scaling */}
            <div className="p-7 rounded-3xl border bg-[var(--surface-1)] border-[var(--border)] shadow-xs">
              <div className="flex items-start gap-4 mb-6">
                <ThreeDIcon name="layers" size="md" variant="indigo" />
                <div>
                  <h3 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
                    Display Font Size Scaling
                  </h3>
                  <p className="text-xs text-[var(--text-secondary)] mt-0.5">
                    Adjust text size across all reports and questionnaires for optimal readability.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  { id: 'normal', label: 'Normal (100%)', desc: 'Standard 16px base size' },
                  { id: 'large', label: 'Large (112%)', desc: 'Enhanced 18px base size' },
                  { id: 'xlarge', label: 'Extra Large (125%)', desc: 'Maximum 20px base size' },
                ].map((opt) => (
                  <button
                    key={opt.id}
                    onClick={() => setFontSize(opt.id as FontSize)}
                    className={`p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                      fontSize === opt.id
                        ? 'border-[var(--accent)] bg-[var(--accent-subtle)] shadow-sm'
                        : 'border-[var(--border)] bg-[var(--surface-0)] hover:border-[var(--border-strong)]'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-sm" style={{ color: 'var(--text-primary)' }}>
                        {opt.label}
                      </span>
                      {fontSize === opt.id && <CheckCircle2 size={16} className="text-[var(--accent)]" />}
                    </div>
                    <p className="text-xs text-[var(--text-muted)]">{opt.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* High Contrast & Reduced Motion */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* High Contrast Toggle */}
              <div className="p-7 rounded-3xl border bg-[var(--surface-1)] border-[var(--border)] shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <ThreeDIcon name="zap" size="sm" variant="amber" />
                    <h4 className="text-base font-bold" style={{ color: 'var(--text-primary)' }}>
                      High Contrast Palette
                    </h4>
                  </div>
                  <p className="text-xs text-[var(--text-secondary)] mb-6">
                    Maximizes border sharpness and deepens contrast for low-vision environments.
                  </p>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
                  <span className="text-xs font-bold text-[var(--text-primary)]">
                    {highContrast ? 'Enabled' : 'Disabled'}
                  </span>
                  <button
                    onClick={() => setHighContrast(!highContrast)}
                    className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${
                      highContrast ? 'bg-[var(--accent)]' : 'bg-[var(--surface-3)]'
                    }`}
                  >
                    <div
                      className={`w-5 h-5 rounded-full bg-white transition-transform ${
                        highContrast ? 'translate-x-6' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Reduced Motion Toggle */}
              <div className="p-7 rounded-3xl border bg-[var(--surface-1)] border-[var(--border)] shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-3">
                    <ThreeDIcon name="shield" size="sm" variant="purple" />
                    <h4 className="text-base font-bold" style={{ color: 'var(--text-primary)' }}>
                      Reduced Motion
                    </h4>
                  </div>
                  <p className="text-xs text-[var(--text-secondary)] mb-6">
                    Minimizes large scale 3D rotations, transitions, and parallax canvas drift.
                  </p>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
                  <span className="text-xs font-bold text-[var(--text-primary)]">
                    {reducedMotion ? 'Enabled' : 'Disabled'}
                  </span>
                  <button
                    onClick={() => setReducedMotion(!reducedMotion)}
                    className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${
                      reducedMotion ? 'bg-[var(--accent)]' : 'bg-[var(--surface-3)]'
                    }`}
                  >
                    <div
                      className={`w-5 h-5 rounded-full bg-white transition-transform ${
                        reducedMotion ? 'translate-x-6' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Language Preference & Audio Assistance */}
            <div className="p-7 rounded-3xl border bg-[var(--surface-1)] border-[var(--border)] shadow-xs">
              <h3 className="text-base font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                Language &amp; Audio Advisory
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl bg-[var(--surface-0)] border border-[var(--border)] flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold">Default System Language</div>
                    <div className="text-xs text-[var(--text-muted)]">Currently set to {lang.toUpperCase()}</div>
                  </div>
                  <div className="flex gap-1.5">
                    <Button
                      variant={lang === 'en' ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setLang('en')}
                      className="text-xs font-bold rounded-xl"
                    >
                      English
                    </Button>
                    <Button
                      variant={lang === 'hi' ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setLang('hi')}
                      className="text-xs font-bold rounded-xl"
                    >
                      हिंदी (Hindi)
                    </Button>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-[var(--surface-0)] border border-[var(--border)] flex items-center justify-between">
                  <div>
                    <div className="text-sm font-bold flex items-center gap-1.5">
                      <Volume2 size={16} className="text-[var(--accent)]" /> Audio Readout
                    </div>
                    <div className="text-xs text-[var(--text-muted)]">Read summary advisory aloud</div>
                  </div>
                  <button
                    onClick={() => setAudioAssistance(!audioAssistance)}
                    className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${
                      audioAssistance ? 'bg-[var(--accent)]' : 'bg-[var(--surface-3)]'
                    }`}
                  >
                    <div
                      className={`w-5 h-5 rounded-full bg-white transition-transform ${
                        audioAssistance ? 'translate-x-6' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* ─────────────────────────────────────────
            TAB 3: DATA & PRIVACY
        ───────────────────────────────────────── */}
        {activeTab === 'data' && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="p-8 rounded-3xl border bg-[var(--surface-1)] border-[var(--border)] shadow-xs space-y-6"
          >
            <div>
              <h3 className="text-xl font-black" style={{ color: 'var(--text-primary)' }}>
                Data Storage &amp; Encryption
              </h3>
              <p className="text-xs text-[var(--text-secondary)] mt-1">
                Your enterprise plans and capital calculations are processed in a zero-retention execution pipeline.
              </p>
            </div>

            <div className="space-y-3 text-sm text-[var(--text-secondary)] leading-relaxed">
              <div className="flex items-start gap-3">
                <CheckCircle2 size={16} className="text-emerald-500 shrink-0 mt-0.5" />
                <span>All deterministic calculations are executed on encrypted edge worker nodes.</span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 size={16} className="text-emerald-500 shrink-0 mt-0.5" />
                <span>Local analysis history is stored securely on your device and synchronized to your account only when authenticated.</span>
              </div>
            </div>

            <div className="pt-4 border-t border-[var(--border)] flex flex-wrap gap-4">
              <Button variant="outline" onClick={handleExportJSON} className="gap-2 rounded-xl text-xs font-bold cursor-pointer">
                <Download size={14} /> Download Entire History (.json)
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
