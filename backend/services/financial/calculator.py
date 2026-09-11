from ..base_service import BaseService
from ...financial_engine import FinancialEngine
from ...core.schemas.domain import FinancialMetrics, FinancialBenchmarks
from typing import Dict, Any

class FinancialService(BaseService[FinancialMetrics]):
    """
    Authoritative service for financial calculations.
    Wraps the legacy FinancialEngine to maintain deterministic results.
    """

    def __init__(self):
        self.engine = FinancialEngine()

    def execute(self, params: FinancialBenchmarks) -> FinancialMetrics:
        """
        Compute full financial model from benchmarks.
        """
        try:
            # Convert Pydantic model to dict for the legacy engine
            params_dict = params.model_dump(by_alias=True)
            result_dict = self.engine.compute_full_model(params_dict)

            # Map legacy dict to new FinancialMetrics schema
            return FinancialMetrics(
                total_project_cost=result_dict["total_project_cost"],
                financing_required=result_dict["financing_required"],
                min_viable_capital=params.min_viable_capital or (result_dict["total_project_cost"] * 0.6),
                monthly_revenue=params.monthly_revenue,
                monthly_expenses=params.monthly_expenses,
                monthly_emi=result_dict["monthly_emi"],
                monthly_net_profit=result_dict["monthly_net_profit"],
                annual_net_profit=result_dict["annual_net_profit"],
                roi_percent=result_dict["roi_percent"],
                break_even_months=result_dict["break_even_months"],
                is_viable=result_dict["is_viable"],
                user_capital=params.user_capital,
                capital_breakdown=params.capital_breakdown
            )
        except Exception as e:
            self.handle_error(e, "Financial calculation failed")
