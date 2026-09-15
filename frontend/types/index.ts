export interface Location {
  district: string;
  state: string;
  lat?: number;
  lng?: number;
}

export interface Place {
  provider_id: string;
  name: string;
  formatted_address: string;
  lat: number;
  lng: number;
}

export interface LocationCandidate {
  provider_id: string;
  label: string;
  hierarchy: {
    state: string;
    district: string;
    village: string;
  };
  lat: number;
  lng: number;
  confidence: number;
}

export interface LocationIdentity {
  provider_id: string;
  name: string;
  district: string;
  state: string;
  country: string;
  pincode?: string;
  coordinates: { lat: number; lng: number };
  source: string;
  currency: {
    code: string;
    symbol: string;
    locale: string;
  };
}

export interface QuestionOption {
  label: string;
  value: string;
  desc?: string;
}

export interface DynamicQuestion {
  id: string;
  question: string;
  type: 'single_select' | 'multi_select' | 'text' | 'number';
  allow_custom?: boolean;
  options?: QuestionOption[];
  placeholder?: string;
  iconName?: 'idea' | 'capital' | 'target' | 'experience' | 'district' | 'state' | 'chart' | 'shield' | 'sparkles' | 'zap' | 'scheme' | 'trending' | 'cart';
  variant?: 'blue' | 'emerald' | 'amber' | 'indigo' | 'cyan' | 'purple' | 'rose';
}

export interface QuestionnaireResponse {
  category: string;
  title: string;
  description: string;
  iconName?: 'idea' | 'capital' | 'target' | 'experience' | 'district' | 'state' | 'chart' | 'shield' | 'sparkles' | 'zap' | 'scheme' | 'trending' | 'cart';
  variant?: 'blue' | 'emerald' | 'amber' | 'indigo' | 'cyan' | 'purple' | 'rose';
  questions: DynamicQuestion[];
}

export interface UserProfile {
  location: Location;
  businessIdea: string;
  availableCapital?: number;
  experience: number;
  targetInvestment?: number;
  answers?: Record<string, any>;
}

export interface Financials {
  // Investment
  total_project_cost: number;
  user_capital: number | null;
  verified_subsidy: number | null;
  financing_required: number;
  min_viable_capital?: number;

  // Revenue
  monthly_revenue: number | null;
  annual_revenue: number | null;

  // Expenses
  monthly_cogs: number | null;
  monthly_expenses: number | null;
  monthly_emi: number | null;

  // Totals
  monthly_net_cash_flow: number | null;
  annual_net_cash_flow: number | null;

  // Metrics
  roi_percent: number | null;
  break_even_months: number | null;
  is_viable: boolean;

  // Detailed Breakdown
  income_breakdown: Record<string, number | null>;
  expenditure_breakdown: Record<string, number | null>;

  assumptions: Record<string, string>;
  provenance: {
    source: string;
    confidence: string;
  };
}

export interface MarketAnalysis {
  demand: number | null;
  competition: number | null;
  accessibility: number | null;
  seasonality: number | null;
  source: string;
  confidence: string;
  reasoning?: string;
}

export interface Scheme {
  schemeId: string;
  name: string;
  ministry: string;
  benefit: {
    subsidyPercent: number;
    loanAmount: number;
  };
  sourceUrl: string;
  eligibility: {
    minCapital: number;
    maxCapital: number;
    categories: string[];
  };
  match_reason: string;
}

export interface ScenarioResult {
  setup_cost: number;
  user_contribution: number;
  subsidy: number;
  financing_gap: number;
  loan_amount: number;
  interest_rate: number;
  tenure_years: number;
  monthly_emi: number;
  monthly_revenue: number;
  monthly_expenses: number;
  monthly_net_cash_flow: number;
  annual_net_cash_flow: number;
  roi_percent: number;
  break_even_months: number | null;
  cumulative_cash_flow_12m: number;
}

export interface AnalysisResult {
  status: 'SUCCESS' | 'PARTIAL' | 'FAILED';
  is_demo?: boolean;
  viabilityScore: number;
  recommendation: string;
  headline?: string;
  category?: string;
  location: LocationIdentity;
  marketAnalysis: MarketAnalysis;
  financials: Financials;
  scenarios?: Record<string, ScenarioResult>;
  interpreter_reasoning?: string;
  modifications: string[];
  matchedSchemes: Scheme[];
  business_blueprint?: {
    flow: Array<{step: string, desc: string}>;
    inputs: string[];
    outputs: string[];
  };
  startup_roadmap?: Array<{week: number, tasks: string[]}>;
  regulatory_requirements?: Array<{doc: string, status: string, source: string}>;
  risk_matrix?: Array<{risk: string, severity: string, probability: string, mitigation: string}>;
  provenance: {
    generated_at: string;
    model_version: string;
  };
}

export interface VoiceTranscription {
  text: string;
  normalized_text: string;
  raw_text: string;
  confidence: number;
}

export interface AuthResponse {
  user: {
    id: string;
    name: string;
    email: string;
    avatar: string;
    provider: string;
  };
  token: string;
}

export interface AnalysisHistoryItem {
  id: string;
  businessIdea: string;
  district: string;
  state: string;
  date: string;
  score: number;
  recommendation: string;
  projectCost: number;
  data: AnalysisResult;
}



