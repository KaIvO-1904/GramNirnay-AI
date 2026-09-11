import math
from typing import Dict, Any

class FinancialEngine:
    """
    Deterministic engine for rural business financial calculations.
    No LLM calls allowed in this class.
    """

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
    def calculate_break_even(setup_cost: float, monthly_revenue: float, monthly_fixed_cost: float) -> float:
        """
        Calculates break-even period in months.
        """
        contribution_margin = monthly_revenue - monthly_fixed_cost
        if contribution_margin <= 0:
            return 999.0 # Use a large number instead of float('inf') for JSON compliance
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

        financing_req = self.project_financing_gap(setup_cost, user_capital)
        emi = self.calculate_emi(financing_req, interest_rate, tenure)

        # Net monthly profit after EMI
        monthly_net_profit = monthly_revenue - monthly_expenses - emi
        annual_net_profit = monthly_net_profit * 12

        roi = self.calculate_roi(annual_net_profit, setup_cost)
        break_even = self.calculate_break_even(setup_cost, monthly_revenue, monthly_expenses + emi)

        return {
            "total_project_cost": setup_cost,
            "financing_required": financing_req,
            "monthly_emi": emi,
            "monthly_net_profit": round(monthly_net_profit, 2),
            "annual_net_profit": round(annual_net_profit, 2),
            "roi_percent": roi,
            "break_even_months": break_even,
            "is_viable": monthly_net_profit > 0 and break_even < 60 # Viable if profit > 0 and breaks even within 5 years
        }
