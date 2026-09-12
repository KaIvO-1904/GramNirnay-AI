import json
from typing import Dict, Any, Optional
from openai import OpenAI
import os
try:
    from .config import settings
    from .logger import logger
    from .demo_data import DEMO_DATASETS
except (ImportError, ValueError):
    from config import settings
    from logger import logger
    from demo_data import DEMO_DATASETS

class BusinessInterpreter:
    """
    Intelligent interpreter that computes required capital, projected revenue,
    and operational cost breakdowns based on business idea and personalized answers.
    """

    def __init__(self):
        # Use Groq if available, otherwise OpenAI
        api_key = settings.groq_api_key or settings.openai_api_key
        base_url = "https://api.groq.com/openai/v1" if settings.groq_api_key else settings.openai_base_url
        self.model = settings.llm_model

        if not api_key:
            logger.warning("OPENAI_API_KEY not found. Using domain-calibrated deterministic algorithms.")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    def interpret(self, idea: str, available_capital: float = 0.0) -> Dict[str, Any]:
        """
        Legacy fallback method when only text idea and optional capital are provided.
        """
        return self.interpret_from_answers(
            idea=idea,
            location={"district": "Rural District", "state": "India"},
            experience_years=1,
            answers={}
        )

    def interpret_from_answers(
        self,
        idea: str,
        location: Dict[str, Any],
        experience_years: int,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main calculation engine that derives required capital and expected revenue
        without asking the user for capital.
        """
        idea_lower = idea.lower()
        district = location.get("district", "Rural District")
        state = location.get("state", "India")

        # --- DEMO MODE OVERRIDE ---
        if settings.demo_mode:
            category_key = self._get_category_key(idea_lower)
            if category_key in DEMO_DATASETS:
                demo_financials = DEMO_DATASETS[category_key]["financials"].copy()
                demo_financials["is_demo"] = True
                return demo_financials
        # --------------------------

        # 1. Poultry Venture Analysis
        if any(w in idea_lower for w in ["poultry", "chicken", "broiler", "layer", "hen", "egg", "kadaknath"]):
            result = self._calculate_poultry_financials(answers, district, state)
            result["is_demo"] = False
            return result

        # 2. Apparel & Cloth Store Analysis
        if any(w in idea_lower for w in ["cloth", "garment", "apparel", "saree", "textile", "tailor", "dress", "boutique"]):
            result = self._calculate_cloth_store_financials(answers, district, state)
            result["is_demo"] = False
            return result

        # 3. Dairy Farm Analysis
        if any(w in idea_lower for w in ["dairy", "cow", "buffalo", "milk", "cattle", "ghee", "paneer"]):
            result = self._calculate_dairy_financials(answers, district, state)
            result["is_demo"] = False
            return result

        # 4. Grocery & Kirana Analysis
        if any(w in idea_lower for w in ["kirana", "grocery", "provision", "supermarket", "fmcg"]):
            result = self._calculate_kirana_financials(answers, district, state)
            result["is_demo"] = False
            return result

        # 5. Agro-Inputs & Fertilizer Analysis
        if any(w in idea_lower for w in ["fertilizer", "seed", "pesticide", "agro", "input"]):
            result = self._calculate_agro_inputs_financials(answers, district, state)
            result["is_demo"] = False
            return result

        # 6. Goat & Livestock Husbandry
        if any(w in idea_lower for w in ["goat", "sheep", "bakri", "mutton"]):
            result = self._calculate_goat_financials(answers, district, state)
            result["is_demo"] = False
            return result

        # 7. AI LLM Dynamic Interpretation for unique ventures
        if self.client:
            result = self._interpret_with_llm(idea, location, experience_years, answers)
            result["is_demo"] = False
            return result

        # Fallback generic rural enterprise model
        result = self._calculate_generic_financials(idea, answers, district, state)
        result["is_demo"] = False
        return result

    def _get_category_key(self, idea_lower: str) -> str:
        if any(w in idea_lower for w in ["poultry", "chicken", "broiler", "layer", "hen", "egg", "bird", "kadaknath"]):
            return "poultry"
        if any(w in idea_lower for w in ["cloth", "garment", "apparel", "saree", "textile", "tailor", "dress", "fashion", "boutique"]):
            return "cloth"
        if any(w in idea_lower for w in ["dairy", "cow", "buffalo", "milk", "cattle", "ghee", "paneer"]):
            return "dairy"
        if any(w in idea_lower for w in ["kirana", "grocery", "provision", "supermarket", "ration", "fmcg"]):
            return "kirana"
        if any(w in idea_lower for w in ["fertilizer", "seed", "pesticide", "agro", "input", "agriculture shop"]):
            return "agro_inputs"
        if any(w in idea_lower for w in ["goat", "sheep", "bakri", "mutton", "lamb"]):
            return "goat"
        return "general"

    def _calculate_poultry_financials(self, answers: Dict[str, Any], district: str, state: str) -> Dict[str, Any]:
        poultry_type = answers.get("poultry_type", "broiler")
        try:
            flock_size = int(answers.get("flock_size", "2500"))
        except (ValueError, TypeError):
            flock_size = 2500
            
        need_shed = answers.get("shed_status", "need_shed") != "shed_ready"
        is_contract = answers.get("contract_farming", "independent") == "contract"

        # Benchmark calculations per bird capacity
        shed_cost = (flock_size * 160) if need_shed else 30000
        equipment_cost = flock_size * 35
        # Working capital for 1 cycle (feed, DOC chicks, medicines)
        working_capital = flock_size * (65 if is_contract else 140)
        
        setup_cost = round(shed_cost + equipment_cost + working_capital)
        
        if is_contract:
            # Guaranteed growing charges ~Rs. 12-16 per kg live weight
            monthly_revenue = round((flock_size * 2.2 * 14.5 * 6) / 12) # 6 batches/year
            monthly_expenses = round(monthly_revenue * 0.35) # Electricity, labor, litter
        else:
            # Independent mandi sales ~Rs. 95-115/kg live weight
            monthly_revenue = round((flock_size * 2.1 * 105 * 5.5) / 12)
            monthly_expenses = round(monthly_revenue * 0.72) # Feed is 68% of total cost

        return {
            "setup_cost": setup_cost,
            "min_viable_capital": round(setup_cost * 0.6),
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "interest_rate": 9.5,
            "tenure_years": 5,
            "category": "poultry",
            "capital_breakdown": {
                "Shed & Civil Infrastructure": shed_cost,
                "Feeders, Drinkers & Heating Equipment": equipment_cost,
                "First Batch Livestock & Feed Working Capital": working_capital
            },
            "reasoning": f"Based on {flock_size} bird {poultry_type} unit in {district}, {state}. High regional protein consumption supports steady 45-day cycle cashflow.",
            "modifications": [
                "Install automated nipple drinking systems to reduce mortality below 3.5%.",
                "Phase first batch with 50% capacity during shed acclimatization.",
                "Apply for 25-35% capital subsidy under National Livestock Mission (NLM) / PMEGP."
            ]
        }

    def _calculate_cloth_store_financials(self, answers: Dict[str, Any], district: str, state: str) -> Dict[str, Any]:
        apparel_cat = answers.get("apparel_category", "readymade")
        shop_size = answers.get("shop_size", "medium")
        shop_loc = answers.get("shop_location", "main_market")

        size_mult = {"small": 0.6, "medium": 1.0, "large": 1.8}.get(shop_size, 1.0)
        
        interior_furnishing = round(120000 * size_mult) # Racks, lighting, display mannequins, trial room
        initial_inventory = round(380000 * size_mult) # Season-opening stock
        security_advance = round(60000 if shop_loc == "main_market" else 30000)

        setup_cost = interior_furnishing + initial_inventory + security_advance
        
        # Monthly sales projection: Average ticket size x daily transactions
        daily_sales = 6500 * size_mult * (1.25 if shop_loc == "main_market" else 1.0)
        monthly_revenue = round(daily_sales * 30)
        # Gross margin is 32-38% in retail apparel
        cogs = round(monthly_revenue * 0.65)
        operating_costs = round(18000 * size_mult + (22000 if shop_loc == "main_market" else 12000)) # Rent + helper + electricity
        monthly_expenses = cogs + operating_costs

        return {
            "setup_cost": setup_cost,
            "min_viable_capital": round(setup_cost * 0.65),
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "interest_rate": 10.0,
            "tenure_years": 5,
            "category": "retail_cloth",
            "capital_breakdown": {
                "Curated Opening Garment Inventory": initial_inventory,
                "Interior Display Racks & LED Illumination": interior_furnishing,
                "Shop Security Deposit & Advance": security_advance
            },
            "reasoning": f"Calculated for a {shop_size} {apparel_cat} retail store in {district}, {state}. High wedding and festival seasonal multipliers enhance annual returns.",
            "modifications": [
                "Stock fast-moving kids wear and ethnic festive lines to achieve 4x annual inventory turnover.",
                "Procure direct from manufacturing clusters (Surat/Tirupur) to increase gross margin by 8-12%.",
                "Avail MUDRA Shishu/Kishore loan up to Rs. 5 Lakhs with collateral-free guarantee."
            ]
        }

    def _calculate_dairy_financials(self, answers: Dict[str, Any], district: str, state: str) -> Dict[str, Any]:
        try:
            cattle_count = int(answers.get("cattle_count", "10"))
        except (ValueError, TypeError):
            cattle_count = 10
        breed = answers.get("breed_preference", "crossbred")
        has_own_fodder = answers.get("fodder_availability", "own_fodder") == "own_fodder"

        cost_per_animal = 70000 if breed == "indigenous_a2" else 62000 if breed == "crossbred" else 82000
        livestock_cost = cattle_count * cost_per_animal
        shed_cost = cattle_count * 22000
        equipment_cost = 45000 if cattle_count < 10 else 95000
        
        setup_cost = livestock_cost + shed_cost + equipment_cost
        
        liters_per_day_per_animal = 11 if breed == "indigenous_a2" else 15 if breed == "crossbred" else 13
        price_per_liter = 48 if breed == "indigenous_a2" else 38 if breed == "crossbred" else 52
        
        daily_yield = cattle_count * liters_per_day_per_animal * 0.85
        monthly_revenue = round(daily_yield * price_per_liter * 30)
        
        feed_cost_per_animal_day = 130 if has_own_fodder else 210
        monthly_feed = round(cattle_count * feed_cost_per_animal_day * 30)
        veterinary_labor = round(cattle_count * 1200 + 12000)
        monthly_expenses = monthly_feed + veterinary_labor

        return {
            "setup_cost": setup_cost,
            "min_viable_capital": round(setup_cost * 0.55),
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "interest_rate": 8.5,
            "tenure_years": 5,
            "category": "dairy",
            "capital_breakdown": {
                f"Purchase of {cattle_count} High-Yield {breed.replace('_', ' ').title()} Cattle": livestock_cost,
                "Ventilated Cattle Shed & Concrete Flooring": shed_cost,
                "Milking Machine, Chaff Cutter & Can Units": equipment_cost
            },
            "reasoning": f"Calibrated for {cattle_count} animals in {district}, {state}. Direct cooperative procurement guarantees daily unhindered cash flow.",
            "modifications": [
                "Cultivate green fodder (Co-4/Super Napier) on 1 acre land to reduce feeding expense by 38%.",
                "Avail NABARD Dairy Entrepreneurship Development Scheme (25-33.33% back-ended capital subsidy).",
                "Incorporate silage bags to maintain milk yield consistency throughout peak summer months."
            ]
        }

    def _calculate_kirana_financials(self, answers: Dict[str, Any], district: str, state: str) -> Dict[str, Any]:
        store_format = answers.get("store_format", "general_store")
        with_fridge = answers.get("refrigeration", "with_refrigeration") == "with_refrigeration"
        
        inventory = 300000 if store_format == "general_store" else 550000
        equipment = (65000 if with_fridge else 20000) + 75000
        setup_cost = inventory + equipment + 40000
        
        daily_sales = 8000 if store_format == "general_store" else 15000
        monthly_revenue = round(daily_sales * 30)
        cogs = round(monthly_revenue * 0.82)
        monthly_expenses = cogs + 22000

        return {
            "setup_cost": setup_cost,
            "min_viable_capital": round(setup_cost * 0.6),
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "interest_rate": 10.0,
            "tenure_years": 5,
            "category": "retail_kirana",
            "capital_breakdown": {
                "FMCG & Provision Opening Inventory": inventory,
                "Shelving, Storage Bins & POS System": equipment,
                "Shop Advance & Initial Operations": 40000
            },
            "reasoning": f"Calculated for grocery enterprise in {district}, {state} with high recurring household consumption.",
            "modifications": [
                "Bundle high-margin organic/regional grains alongside standard FMCG products to expand gross margin.",
                "Integrate digital UPI QR billing and home delivery within 3km village radius."
            ]
        }

    def _calculate_agro_inputs_financials(self, answers: Dict[str, Any], district: str, state: str) -> Dict[str, Any]:
        inventory = 450000
        godown = 120000
        licensing_store = 50000
        setup_cost = inventory + godown + licensing_store
        
        monthly_revenue = 320000
        cogs = round(monthly_revenue * 0.84)
        monthly_expenses = cogs + 24000

        return {
            "setup_cost": setup_cost,
            "min_viable_capital": round(setup_cost * 0.7),
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "interest_rate": 9.0,
            "tenure_years": 5,
            "category": "agro_retail",
            "capital_breakdown": {
                "Fertilizer, Seed & Chemical Stock": inventory,
                "Storage Godown & Display Space": godown,
                "Retail Dealership Licensing & Security": licensing_store
            },
            "reasoning": f"Optimized for seasonal agricultural cycles in {district}, {state}.",
            "modifications": [
                "Maintain tie-ups with district fertilizer distributors for credit terms of 21-30 days.",
                "Apply under Agriculture Infrastructure Fund (AIF) for 3% interest subvention."
            ]
        }

    def _calculate_goat_financials(self, answers: Dict[str, Any], district: str, state: str) -> Dict[str, Any]:
        herd = answers.get("herd_size", "20_2")
        animals = 22 if herd == "20_2" else 11 if herd == "10_1" else 55
        
        animal_cost = animals * 7500
        shed_cost = animals * 3500
        feed_health = animals * 1800
        setup_cost = animal_cost + shed_cost + feed_health
        
        monthly_revenue = round((animals * 1.6 * 8500) / 12)
        monthly_expenses = round(monthly_revenue * 0.38)

        return {
            "setup_cost": setup_cost,
            "min_viable_capital": round(setup_cost * 0.6),
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "interest_rate": 9.0,
            "tenure_years": 5,
            "category": "goat_farming",
            "capital_breakdown": {
                f"Breeding Herd ({animals} Goats/Bucks)": animal_cost,
                "Slatted-Floor Elevated Shed": shed_cost,
                "Vaccination, Feed & Mineral Blocks": feed_health
            },
            "reasoning": f"Calculated for commercial goat husbandry in {district}, {state} with high demand for live weight mutton.",
            "modifications": [
                "Avail 33% subsidy under National Livestock Mission (NLM) small ruminant scheme.",
                "Adopt stall-fed intensive management to accelerate kid growth to 25kg in 6 months."
            ]
        }

    def _interpret_with_llm(self, idea: str, location: Dict[str, Any], experience: int, answers: Dict[str, Any]) -> Dict[str, Any]:
        district = location.get("district", "Rural District")
        state = location.get("state", "India")
        answers_str = json.dumps(answers)

        prompt = (
            f"You are an Expert Rural Financial Architect for India. The entrepreneur wants to establish: '{idea}' in {district}, {state}.\n"
            f"Experience: {experience} years. Operational survey answers: {answers_str}.\n\n"
            f"Calculate benchmarked, realistic, profitable financial requirements for this business. DO NOT assume they already have capital.\n"
            f"Provide the exact capital needed to achieve healthy profitability, expected monthly sales, and operating expenses.\n\n"
            f"Return ONLY a JSON object with:\n"
            f"- setup_cost: (Total recommended investment in INR to build and equip the venture)\n"
            f"- min_viable_capital: (Minimum bare-bones capital to launch)\n"
            f"- monthly_revenue: (Realistic projected monthly sales in INR)\n"
            f"- monthly_expenses: (All recurring monthly costs: raw material, labor, electricity, rent in INR)\n"
            f"- interest_rate: (Typical rural loan interest, e.g. 9.0 to 11.5)\n"
            f"- tenure_years: (Standard loan tenure, usually 5)\n"
            f"- category: (Business classification string)\n"
            f"- capital_breakdown: (Object with 3-4 major asset items and their INR cost)\n"
            f"- reasoning: (Clear explanation of the revenue and capital benchmark in that district)\n"
            f"- modifications: (Array of 3 concrete strategic recommendations to increase profit margin)"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"LLM Interpretation failed: {e}. Falling back to default model.")
            return self._calculate_generic_financials(idea, answers, district, state)

    def _calculate_generic_financials(self, idea: str, answers: Dict[str, Any], district: str, state: str) -> Dict[str, Any]:
        setup_cost = 450000
        monthly_revenue = 110000
        monthly_expenses = 72000

        return {
            "setup_cost": setup_cost,
            "min_viable_capital": 250000,
            "monthly_revenue": monthly_revenue,
            "monthly_expenses": monthly_expenses,
            "interest_rate": 9.5,
            "tenure_years": 5,
            "category": "micro_enterprise",
            "capital_breakdown": {
                "Machinery & Essential Equipment": 180000,
                "Workshop / Retail Workspace Setup": 120000,
                "Opening Raw Materials & Operational Buffer": 150000
            },
            "reasoning": f"Derived for {idea} in {district}, {state} based on rural SME benchmarks.",
            "modifications": [
                "Apply for PMEGP credit-linked capital subsidy up to 35% in rural areas.",
                "Structure procurement to maintain positive cashflow from Month 2."
            ]
        }

