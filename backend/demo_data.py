from typing import Dict, Any, List

# Realistic but clearly synthetic datasets for SIH demonstration
# These are used when settings.demo_mode = True

DEMO_DATASETS = {
    "poultry": {
        "metadata": {
            "location": {
                "district": "Mayurbhanj",
                "state": "Odisha",
                "coordinates": {"lat": 22.11, "lng": 86.35},
                "characteristics": "High humidity, strong local demand for native chicken"
            },
            "context": "Simulated environment for Poultry (Country Chicken) business journey."
        },
        "intelligence": {
            "competition": [
                {"name": "Local Poultry Farm A", "distance": "2.5km", "market_share": "15%", "strength": "Low price"},
                {"name": "Rural Egg Distributor", "distance": "5.0km", "market_share": "10%", "strength": "Established network"},
                {"name": "Backyard Small-scale Farmers", "distance": "Various", "market_share": "40%", "strength": "Trust/Local relations"}
            ],
            "suppliers": [
                {"name": "Bhubaneswar Hatchery Hub", "product": "DOC Chicks", "cost": "Rs. 45/bird", "lead_time": "3 days"},
                {"name": "Regional Feed Mill", "product": "Pre-mix Feed", "cost": "Rs. 38/kg", "lead_time": "2 days"},
                {"name": "Govt Vet Services", "product": "Vaccines", "cost": "Subsidized", "lead_time": "Immediate"}
            ],
            "raw_materials": [
                {"item": "Day-Old Chicks (DOC)", "cost": "Rs. 45", "unit": "per bird"},
                {"item": "Poultry Feed", "cost": "Rs. 38", "unit": "per kg"},
                {"item": "Bedding (Husks)", "cost": "Rs. 5", "unit": "per kg"}
            ],
            "transportation": [
                {"mode": "Tractor-Trolley", "cost": "Rs. 500", "unit": "per trip", "detail": "Local transport to mandi"},
                {"mode": "Small Commercial Vehicle", "cost": "Rs. 1200", "unit": "per trip", "detail": "Transport to city hub"}
            ],
            "local_demand": {
                "market_size": "High",
                "growth_rate": "12% YoY",
                "consumer_preference": "Preference for 'Country Chicken' (Desi) over Broiler for taste and health.",
                "peak_seasons": "Wedding season (Nov-Feb), Local festivals"
            },
            "business_costs": {
                "shed_construction": 120000,
                "equipment": 45000,
                "labor_monthly": 8000,
                "electricity_monthly": 1200
            }
        },
        "financials": {
            "setup_cost": 210000,
            "min_viable_capital": 126000,
            "monthly_revenue": 45000,
            "monthly_expenses": 28000,
            "interest_rate": 9.0,
            "tenure_years": 5,
            "category": "poultry",
            "capital_breakdown": {
                "Shed & Civil Infrastructure": 120000,
                "Feeding & Watering Equipment": 45000,
                "Initial Flock & Feed Buffer": 45000
            },
            "reasoning": "Deterministic Demo: Based on Mayurbhanj district benchmarks for Country Chicken. High premium pricing for native birds offsets higher growth time.",
            "modifications": [
                "Demo: Integrate automated ventilation to reduce summer mortality by 5%.",
                "Demo: Establish direct tie-ups with hotel chains in Bhubaneswar for 20% higher margins.",
                "Demo: Apply for NLM subsidy to recover 33% of capital cost."
            ]
        }
    },
    "dairy": {
        "metadata": {
            "location": {
                "district": "Anand",
                "state": "Gujarat",
                "coordinates": {"lat": 22.82, "lng": 72.91},
                "characteristics": "Hub of dairy cooperatives, high-yield breed availability"
            },
            "context": "Simulated environment for Dairy (Indigenous A2) business journey."
        },
        "intelligence": {
            "competition": [
                {"name": "Amul Collection Center", "distance": "1km", "market_share": "60%", "strength": "Guaranteed buy-back"},
                {"name": "Private Dairy Farm X", "distance": "4km", "market_share": "10%", "strength": "Premium A2 branding"},
                {"name": "Local Milkmen", "distance": "Various", "market_share": "20%", "strength": "Doorstep delivery"}
            ],
            "suppliers": [
                {"name": "Certified Gir Cow Breeders", "product": "A2 Cows", "cost": "Rs. 75,000", "lead_time": "15 days"},
                {"name": "Cooperative Feed Store", "product": "Balanced Fodder", "cost": "Rs. 22/kg", "lead_time": "1 day"},
                {"name": "Veterinary Clinic", "product": "Health Checkups", "cost": "Rs. 500/visit", "lead_time": "Immediate"}
            ],
            "raw_materials": [
                {"item": "High-Yield A2 Cattle", "cost": "Rs. 75,000", "unit": "per animal"},
                {"item": "Concentrate Feed", "cost": "Rs. 22", "unit": "per kg"},
                {"item": "Mineral Mixture", "cost": "Rs. 60", "unit": "per kg"}
            ],
            "transportation": [
                {"mode": "Milk Cans/Trolley", "cost": "Rs. 300", "unit": "per trip", "detail": "Collection center transport"},
                {"mode": "Chilled Tanker", "cost": "Rs. 2000", "unit": "per trip", "detail": "Bulk transport to processing plant"}
            ],
            "local_demand": {
                "market_size": "Very High",
                "growth_rate": "8% YoY",
                "consumer_preference": "Increasing shift towards A2 milk for digestive health.",
                "peak_seasons": "Year-round steady demand"
            },
            "business_costs": {
                "shed_construction": 150000,
                "milking_equipment": 60000,
                "labor_monthly": 10000,
                "electricity_monthly": 2000
            }
        },
        "financials": {
            "setup_cost": 420000,
            "min_viable_capital": 231000,
            "monthly_revenue": 65000,
            "monthly_expenses": 32000,
            "interest_rate": 8.5,
            "tenure_years": 5,
            "category": "dairy",
            "capital_breakdown": {
                "A2 Cattle Purchase": 250000,
                "Ventilated Shed": 120000,
                "Milking & Chilling Equipment": 50000
            },
            "reasoning": "Deterministic Demo: Based on Anand district benchmarks for A2 Dairy. Strong cooperative support reduces market risk.",
            "modifications": [
                "Demo: Adopt silage making to reduce dry-season fodder costs by 20%.",
                "Demo: Register as an Organic Certified farm to increase price by 15%.",
                "Demo: Utilize NABARD Dairy Entrepreneurship Scheme for 33% subsidy."
            ]
        }
    },
    "kirana": {
        "metadata": {
            "location": {
                "district": "Kurnool",
                "state": "Andhra Pradesh",
                "coordinates": {"lat": 15.82, "lng": 78.03},
                "characteristics": "Rural trade center, high frequency of small ticket purchases"
            },
            "context": "Simulated environment for Small Rural Retail (Kirana) business journey."
        },
        "intelligence": {
            "competition": [
                {"name": "Village General Store", "distance": "0.5km", "market_share": "30%", "strength": "Established relations"},
                {"name": "Town Mini-Mart", "distance": "3km", "market_share": "20%", "strength": "Better variety"},
                {"name": "Mobile Grocery Van", "distance": "Various", "market_share": "15%", "strength": "Convenience"}
            ],
            "suppliers": [
                {"name": "District Wholesale Mandi", "product": "Grains & Staples", "cost": "Wholesale", "lead_time": "2 days"},
                {"name": "HUL/ITC Distributor", "product": "FMCG Goods", "cost": "Dealer Price", "lead_time": "1 day"},
                {"name": "Local Flour Mill", "product": "Atta/Besan", "cost": "Local Rate", "lead_time": "Immediate"}
            ],
            "raw_materials": [
                {"item": "FMCG Opening Stock", "cost": "Rs. 2,00,000", "unit": "Lumpsum"},
                {"item": "Bulk Grains", "cost": "Rs. 1,00,000", "unit": "Lumpsum"},
                {"item": "Shelving/Counters", "cost": "Rs. 50,000", "unit": "Lumpsum"}
            ],
            "transportation": [
                {"mode": "Auto-Rickshaw", "cost": "Rs. 200", "unit": "per trip", "detail": "Mandi to store transport"},
                {"mode": "Two-Wheeler", "cost": "Rs. 50", "unit": "per trip", "detail": "Home delivery service"}
            ],
            "local_demand": {
                "market_size": "Medium",
                "growth_rate": "5% YoY",
                "consumer_preference": "High demand for branded FMCG and local staples.",
                "peak_seasons": "Harvest season (higher spending power)"
            },
            "business_costs": {
                "shop_advance": 40000,
                "initial_inventory": 300000,
                "furniture": 60000,
                "electricity_monthly": 1000
            }
        },
        "financials": {
            "setup_cost": 400000,
            "min_viable_capital": 240000,
            "monthly_revenue": 120000,
            "monthly_expenses": 95000,
            "interest_rate": 10.0,
            "tenure_years": 5,
            "category": "retail_kirana",
            "capital_breakdown": {
                "Initial FMCG Inventory": 300000,
                "Furniture & Shelving": 60000,
                "Shop Advance & Legal": 40000
            },
            "reasoning": "Deterministic Demo: Based on Kurnool rural trade benchmarks. High turnover of daily essentials ensures steady cash flow.",
            "modifications": [
                "Demo: Introduce a 'Subscription' model for monthly staples to lock in customers.",
                "Demo: Partner with a digital payment provider for a 'Cashback' lure.",
                "Demo: Avail MUDRA Shishu loan for initial inventory funding."
            ]
        }
    }
}
