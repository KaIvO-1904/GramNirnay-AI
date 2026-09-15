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

export interface LocationIdentity {
  provider_id: string;
  name: string;
  district: string;
  state: string;
  country: string;
  pincode?: string;
  coordinates: { lat: number; lng: number };
  source: string;
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
  total_project_cost: number;
  financing_required: number;
  min_viable_capital?: number;
  monthly_revenue: number;
  monthly_expenses: number;
  monthly_emi: number;
  monthly_net_profit: number;
  annual_net_profit: number;
  roi_percent: number;
  break_even_months: number;
  is_viable: boolean;
  user_capital?: number;
  capital_breakdown?: Record<string, number>;
  income_breakdown?: Record<string, number>;
  expenditure_breakdown?: Record<string, number>;
  assumptions?: Record<string, string>;
}

export interface MarketAnalysis {
  demand: number;
  competition: number;
  accessibility: number;
  seasonality: number;
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
  is_demo?: boolean;
  viabilityScore: number;
  recommendation: string;
  headline?: string;
  category?: string;
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
}

export interface VoiceTranscription {
  text: string;
  confidence: number;
}

export interface AuthResponse {
  user_id: string;
  token: string;
}



