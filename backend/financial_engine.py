import math
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ScenarioResult:
    setup_cost: float
    user_contribution: float
    subsidy: float
    financing_gap: float
    loan_amount: float
    interest_rate: float
    tenure_years: int
    monthly_emi: float
    monthly_revenue: float
    monthly_expenses: float
    monthly_net_cash_flow: float
    annual_net_cash_flow: float
    roi_percent: float
    break_even_months: Optional[float]
    cumulative_cash_flow_12m: float

class FinancialEngine:
    """
    Deterministic engine for rural business financial calculations.
    No LLM calls allowed in this class.
    """

    def __init__(self):
        pass

    @staticmethod
    def calculate_emi(principal: float, annual_rate: float, tenure_years: int) -> float:
        """
        Calculates the Monthly Equated Installment (EMI).
        Formula: [P x R x (1+R)^N] / [(1+R)^N - 1]
        """
        if principal <= 0 or annual_rate <= 0 or tenure_years <= 0:
            return 0.0

        monthly_rate = (annual_rate / 100) / 12
        num_payments = tenure_years * 12

        try:
            emi = (principal * monthly_rate * math.pow(1 + monthly_rate, num_payments)) / \
                  (math.pow(1 + monthly_rate, num_payments) - 1)
            return round(emi, 2)
        except ZeroDivisionError:
            return 0.0

    @staticmethod
    def calculate_break_even(setup_cost: float, monthly_revenue: float, monthly_fixed_cost: float) -> Optional[float]:
        """
        Calculates break-even period in months.
        """
        contribution_margin = monthly_revenue - monthly_fixed_cost
        if contribution_margin <= 0:
            return None
        return round(setup_cost / contribution_margin, 2)

    @staticmethod
    def calculate_roi(annual_net_profit: float, total_investment: float) -> float:
        """
        Calculates Return on Investment as a percentage.
        """
        if total_investment <= 0:
            return 0.0
        return round((annual_net_profit / total_investment) * 100, 2)

    @staticmethod
    def project_financing_gap(total_cost: float, user_capital: float) -> float:
        """
        Determines the amount of financing required.
        """
        gap = total_cost - user_capital
        return max(0.0, round(gap, 2))

    def compute_full_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs a full financial projection based on business parameters.
        """
        setup_cost = params.get('setup_cost', 0.0)
        user_capital = params.get('user_capital', 0.0)
        monthly_revenue = params.get('monthly_revenue', 0.0)
        monthly_expenses = params.get('monthly_expenses', 0.0)
        interest_rate = params.get('interest_rate', 0.0)
        tenure = params.get('tenure_years', 5)

        # Ensure expenses are not zero if revenue exists (Business Logic)
        if monthly_revenue > 0 and monthly_expenses <= 0:
            # Fallback to a benchmark expenditure if not provided (e.g., 60-80% of revenue for retail/agro)
            # In a real system, this would come from an ontology based on the category.
            monthly_expenses = monthly_revenue * 0.7

        financing_req = self.project_financing_gap(setup_cost, user_capital)
        emi = self.calculate_emi(financing_req, interest_rate, tenure)

        monthly_net_profit = monthly_revenue - monthly_expenses - emi
        annual_net_profit = monthly_net_profit * 12

        roi = self.calculate_roi(annual_net_profit, setup_cost)
        break_even = self.calculate_break_even(setup_cost, monthly_revenue, monthly_expenses + emi)

        capital_breakdown = params.get('capital_breakdown')
        if not capital_breakdown:
            capital_breakdown = {
                "Owner Contribution": user_capital,
                "External Financing": financing_req
            }

        return {
            "total_project_cost": setup_cost,
            "monthly_revenue": monthly_revenue,
            "annual_revenue": monthly_revenue * 12,
            "monthly_expenses": monthly_expenses,
            "annual_expenses": monthly_expenses * 12,
            "financing_required": financing_req,
            "monthly_emi": emi,
            "monthly_net_profit": round(monthly_net_profit, 2),
            "annual_net_profit": round(annual_net_profit, 2),
            "roi_percent": roi,
            "break_even_months": break_even,
            "is_viable": monthly_net_profit > 0 and break_even < 60,
            "user_capital": user_capital,
            "min_viable_capital": setup_cost * 0.2,
            "capital_breakdown": capital_breakdown,
            "expenditure_breakdown": {
                "Operating Expenses": monthly_expenses,
                "Debt Service (EMI)": emi,
                "Total": monthly_expenses + emi
            },
            "income_breakdown": {
                "Direct Sales": monthly_revenue,
                "Total": monthly_revenue
            },
            "assumptions": {
                "revenue": "Based on regional benchmarks for the selected category.",
                "expenses": "Estimated at 70% of revenue if not provided." if monthly_expenses == 0 else "User provided values."
            }
        }

    def calculate_scenarios(self, params: Dict[str, Any]) -> Dict[str, ScenarioResult]:
        """
        Deterministic Scenario Engine.
        Computes a set of standardized financial scenarios.
        """
        base_setup = params.get('setup_cost', 0.0)
        base_rev = params.get('monthly_revenue', 0.0)
        base_exp = params.get('monthly_expenses', 0.0)
        base_cap = params.get('user_capital', 0.0)
        base_rate = params.get('interest_rate', 9.5)
        base_tenure = params.get('tenure_years', 5)

        scenarios = {}

        # Scenario configurations: (setup_mult, rev_mult, exp_mult, subsidy_pct, rate_adj, tenure_adj)
        configs = {
            "conservative": (1.1, 0.7, 1.2, 0.0, 1.0, 0),
            "base": (1.0, 1.0, 1.0, 0.0, 0.0, 0),
            "optimistic": (0.9, 1.3, 0.9, 0.0, -0.5, 0),
            "lean": (0.7, 0.8, 0.8, 0.0, 0.0, 0),
            "subsidy": (1.0, 1.0, 1.0, 0.25, -1.0, 0),
            "aggressive": (1.2, 1.5, 1.3, 0.0, 0.0, 0),
        }

        for name, (s_m, r_m, e_m, sub_p, rate_a, ten_a) in configs.items():
            s_cost = base_setup * s_m
            m_rev = base_rev * r_m
            m_exp = base_exp * e_m
            subsidy = s_cost * sub_p

            # Contribution includes the subsidy in this model
            total_contribution = base_cap + subsidy
            gap = self.project_financing_gap(s_cost, total_contribution)

            rate = base_rate + rate_a
            tenure = base_tenure + ten_a
            emi = self.calculate_emi(gap, rate, tenure)

            m_net = m_rev - m_exp - emi
            a_net = m_net * 12
            roi = self.calculate_roi(a_net, s_cost)
            be = self.calculate_break_even(s_cost, m_rev, m_exp + emi)

            # 12m Cumulative: (Monthly Net * 12) - SetupCost + Contribution
            cum_12 = (m_net * 12) - s_cost + total_contribution

            scenarios[name] = ScenarioResult(
                setup_cost=round(s_cost, 2),
                user_contribution=round(base_cap, 2),
                subsidy=round(subsidy, 2),
                financing_gap=round(gap, 2),
                loan_amount=round(gap, 2),
                interest_rate=round(rate, 2),
                tenure_years=tenure,
                monthly_emi=emi,
                monthly_revenue=round(m_rev, 2),
                monthly_expenses=round(m_exp, 2),
                monthly_net_cash_flow=round(m_net, 2),
                annual_net_cash_flow=round(a_net, 2),
                roi_percent=roi,
                break_even_months=be,
                cumulative_cash_flow_12m=round(cum_12, 2)
            )

        return scenarios
