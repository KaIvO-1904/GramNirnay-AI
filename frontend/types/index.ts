export interface Location {
  district: string;
  state: string;
  lat?: number;
  lng?: number;
}

export interface QuestionOption {
  label: string;
  value: string;
  desc?: string;
}

export interface DynamicQuestion {
  id: string;
  question: string;
  type: 'select' | 'text' | 'number';
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

export interface AnalysisResult {
  is_demo?: boolean;
  viabilityScore: number;
  recommendation: string;
  headline?: string;
  category?: string;
  marketAnalysis: MarketAnalysis;
  financials: Financials;
  interpreter_reasoning?: string;
  modifications: string[];
  matchedSchemes: Scheme[];
}

