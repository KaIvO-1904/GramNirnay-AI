from typing import List, Dict, Any, Optional
import json
import os
try:
    from .config import settings
    from .logger import logger
except (ImportError, ValueError):
    from config import settings
    from logger import logger

# Pre-calibrated high-accuracy question banks for major rural enterprises
CURATED_QUESTION_BANKS = {
    "poultry": {
        "title": "Poultry Venture Configuration",
        "description": "Specify your flock size, breed, housing, and distribution for precise capital & profit modeling.",
        "iconName": "idea",
        "variant": "blue",
        "questions": [
            {
                "id": "poultry_type",
                "question": "What type of poultry unit are you planning?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Broiler (Fast 45-day Meat Cycle)", "value": "broiler", "desc": "High turnover, steady mandi & retail chicken demand"},
                    {"label": "Layer (Egg Production Unit)", "value": "layer", "desc": "Daily recurring cash flow from table egg sales"},
                    {"label": "Desi / Kadaknath (Free-Range Native)", "value": "desi_kadaknath", "desc": "Premium pricing (Rs. 400-600/bird), lower disease risk"},
                    {"label": "Hatchery & Day-Old Chicks (DOC)", "value": "hatchery", "desc": "Incubator supply to local backyard poultry farmers"}
                ]
            },
            {
                "id": "flock_size",
                "question": "What is your target flock capacity per batch?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "1,000 Birds (Starter Commercial)", "value": "1000", "desc": "Manageable initial capital, family labor friendly"},
                    {"label": "2,500 - 3,000 Birds (Optimal Commercial)", "value": "2500", "desc": "Best unit economics & prime NABARD/PMEGP subsidy eligibility"},
                    {"label": "5,000+ Birds (Large Scale Automated)", "value": "5000", "desc": "High volume margins with automated nipple drinkers & feeders"}
                ]
            },
            {
                "id": "shed_status",
                "question": "What is the status of your shed & civil infrastructure?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Own land, need new shed construction", "value": "need_shed", "desc": "Requires civil investment in truss, floor & wire mesh"},
                    {"label": "Existing shed ready to use", "value": "shed_ready", "desc": "Minimal setup capital, instant operational launch"},
                    {"label": "Planning to lease / rent poultry shed", "value": "leased_shed", "desc": "Lower upfront capital with monthly rental expense"}
                ]
            },
            {
                "id": "contract_farming",
                "question": "Will you operate independently or via contract integration?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Independent Farming (Higher Profit, Market Risk)", "value": "independent", "desc": "Purchase feed & DOC directly, capture full open mandi profits"},
                    {"label": "Company Contract / Buy-back (Guaranteed Growing Charges)", "value": "contract", "desc": "Company supplies chicks & feed; guaranteed Rs. 12-16/kg payout"}
                ]
            },
            {
                "id": "feed_strategy",
                "question": "How will you manage feed and water infrastructure?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Commercial Branded Pelleted Feed", "value": "commercial_feed", "desc": "Optimal FCR (1.55-1.65), predictable weight gain"},
                    {"label": "On-Farm Feed Mixing Unit (Maize + Soya + Pre-mix)", "value": "self_mixing", "desc": "Reduces feed cost by 12-18% for larger scale flocks"},
                    {"label": "Borewell with Water Filtration & Nipple Drinkers", "value": "borewell_auto", "desc": "Automated clean water reduces flock mortality below 3%"}
                ]
            }
        ]
    },
    "cloth": {
        "title": "Apparel & Textile Store Setup",
        "description": "Configure your inventory mix, retail floor space, and sourcing channels for accurate financial forecasting.",
        "iconName": "cart",
        "variant": "emerald",
        "questions": [
            {
                "id": "apparel_category",
                "question": "What primary clothing lines will you stock?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Sarees, Lehengas & Ethnic Festive Wear", "value": "ethnic", "desc": "High gross profit margins (30-45%), wedding peak demand"},
                    {"label": "Readymade Garments & Kids/Youth Wear", "value": "readymade", "desc": "Fastest inventory turnover (4-6 turns/year)"},
                    {"label": "Daily Cottons & School/Work Uniforms", "value": "daily_uniforms", "desc": "Recession-proof steady weekly recurring sales"},
                    {"label": "Unstitched Fabrics, Suiting & Shirting", "value": "textiles", "desc": "Long shelf-life, minimal dead-stock risk"}
                ]
            },
            {
                "id": "shop_location",
                "question": "Where will your retail store be located?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Main Taluka Bazaar / High Footfall Market", "value": "main_market", "desc": "Highest daily walk-in traffic, higher rental advance"},
                    {"label": "Gram Panchayat Center / Village Junction", "value": "village_center", "desc": "Affordable rent, loyal neighborhood customer base"},
                    {"label": "Near Bus Stand / Highway Commercial Hub", "value": "transit_hub", "desc": "High commuter visibility and weekend shopping footfall"}
                ]
            },
            {
                "id": "shop_size",
                "question": "What estimated retail floor area are you planning?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "150 - 250 sq.ft (Compact Boutique)", "value": "small", "desc": "Optimal for single entrepreneur with curated stock"},
                    {"label": "350 - 600 sq.ft (Full Family Store)", "value": "medium", "desc": "Multiple sections (Men, Women, Kids) + fitting room"},
                    {"label": "800+ sq.ft (Multi-Tier Showroom)", "value": "large", "desc": "High inventory depth with display mannequins & seating"}
                ]
            },
            {
                "id": "sourcing_channel",
                "question": "Where will you source your wholesale inventory?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Direct from manufacturing clusters (Surat / Delhi / Tirupur)", "value": "direct_hubs", "desc": "Lowest cost price, extra 8-14% profit margin"},
                    {"label": "Regional District Wholesale Distributor", "value": "district_wholesaler", "desc": "Frequent small batch restocking with local credit terms"},
                    {"label": "Direct Weavers & Handloom Cooperatives", "value": "local_artisans", "desc": "Exclusive artisan designs with authentic regional appeal"}
                ]
            },
            {
                "id": "fitout_level",
                "question": "What level of interior furnishing & lighting do you plan?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Modern LED Lighting, Acrylic Racks & Glass Display", "value": "premium_fitout", "desc": "Boosts perceived garment value and premium pricing"},
                    {"label": "Standard Wooden / Metal Shelving with Trial Mirror", "value": "standard_fitout", "desc": "Cost-effective, clean presentation"},
                    {"label": "Basic Counter & Wall Hangings", "value": "basic_fitout", "desc": "Lowest setup capital requirement"}
                ]
            }
        ]
    },
    "dairy": {
        "title": "Dairy Farm Configuration",
        "description": "Define cattle count, breed genetics, and milk marketing channels for yield modeling.",
        "iconName": "trending",
        "variant": "amber",
        "questions": [
            {
                "id": "cattle_count",
                "question": "How many milch animals are you starting with?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "4 - 5 Animals (Starter Unit)", "value": "4", "desc": "Family-run, low risk, 45-60 liters/day output"},
                    {"label": "10 - 15 Animals (Semi-Commercial)", "value": "10", "desc": "Optimal unit economics, prime 25-33% NABARD subsidy"},
                    {"label": "20+ Animals (Commercial Dairy)", "value": "20", "desc": "Supports automated milking, chilling vat & dung biogas"}
                ]
            },
            {
                "id": "breed_preference",
                "question": "Which cattle breed do you plan to acquire?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Crossbred High-Yield Cows (HF / Jersey)", "value": "crossbred", "desc": "High volume (16-24 L/day per cow), fast cashflow"},
                    {"label": "Indigenous A2 Cows (Gir / Sahiwal / Tharparkar)", "value": "indigenous_a2", "desc": "Premium milk pricing (Rs. 50-70/L), disease hardy"},
                    {"label": "Murrah / Mehsana Buffaloes", "value": "buffalo", "desc": "High fat content (7-8%), top cooperative FAT rate payout"}
                ]
            },
            {
                "id": "fodder_availability",
                "question": "What is your green fodder cultivation setup?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Own agricultural land with borewell/canal irrigation", "value": "own_fodder", "desc": "Cuts daily feeding cost by 38%, maximizes net profit"},
                    {"label": "Partial land with supplemental dry silage & feed bags", "value": "mixed_fodder", "desc": "Balanced cost with year-round yield consistency"},
                    {"label": "No agricultural land, 100% market feed purchase", "value": "purchase_fodder", "desc": "Higher operational expense per animal"}
                ]
            },
            {
                "id": "sales_channel",
                "question": "How will you market the produced milk?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Dairy Cooperative Union (Amul / KMF / Mother Dairy)", "value": "cooperative", "desc": "Guaranteed daily off-take with 10-day direct bank payout"},
                    {"label": "Direct Retail Bottling to Town Households & Hotels", "value": "direct_retail", "desc": "Earn 25-35% higher price per liter directly"},
                    {"label": "On-Farm Value Addition (Ghee, Paneer, Curd, Butter)", "value": "value_added", "desc": "Doubles gross profit margin from milk volume"}
                ]
            },
            {
                "id": "mechanization",
                "question": "What farm machinery will you incorporate?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Automatic Bucket Milking Machine & Chaff Cutter", "value": "milking_machine", "desc": "Reduces labor time from 3 hours to 35 minutes"},
                    {"label": "Chaff Cutter + Manual Milking", "value": "chaff_only", "desc": "Standard rural setup with lower equipment expense"},
                    {"label": "Bulk Milk Chiller (BMC) & Biogas Generator", "value": "bmc_biogas", "desc": "Zero milk spoilage & free cooking gas/manure"}
                ]
            }
        ]
    },
    "kirana": {
        "title": "Grocery & FMCG Retail Store",
        "description": "Structure your retail format, refrigeration, inventory turnover, and daily customer reach.",
        "iconName": "cart",
        "variant": "cyan",
        "questions": [
            {
                "id": "store_format",
                "question": "What format of grocery store are you setting up?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "General Provisions & Daily FMCG Store", "value": "general_store", "desc": "Standard counter format with pulses, spices, soaps & staples"},
                    {"label": "Self-Service Mini Supermarket with POS Barcode", "value": "supermarket", "desc": "Modern walk-in shopping with higher average basket size"},
                    {"label": "Wholesale Grain, Spices & Edible Oil Depot", "value": "wholesale_depot", "desc": "Supplies village kirana shops and wedding bulk orders"}
                ]
            },
            {
                "id": "refrigeration",
                "question": "Will you install commercial refrigeration & cooling units?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Yes, Commercial Deep Freezers & Beverage Coolers", "value": "with_refrigeration", "desc": "Capture lucrative dairy, ice-cream, cold beverage & frozen margins"},
                    {"label": "Dry Packaged Goods & Grains Only", "value": "dry_only", "desc": "Lower electricity bill and equipment investment"}
                ]
            },
            {
                "id": "inventory_sourcing",
                "question": "How will you source your daily FMCG inventory?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Direct FMCG Company Distributors on Weekly Credit", "value": "fmcg_distributors", "desc": "Best dealer discounts & promotional schemes"},
                    {"label": "District Wholesale Mandi Cash Purchases", "value": "mandi_wholesale", "desc": "Lowest bulk rates for rice, wheat, oils & spices"},
                    {"label": "B2B E-Commerce Apps (Udaan / JioMart Partner)", "value": "b2b_apps", "desc": "Doorstep delivery with digital invoices"}
                ]
            },
            {
                "id": "digital_payments",
                "question": "What payment & delivery services will you offer?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "UPI QR Soundbox + Free Home Delivery within 3km", "value": "digital_delivery", "desc": "Attracts 30% higher sales volume from nearby households"},
                    {"label": "Counter Walk-in Cash & UPI Only", "value": "counter_only", "desc": "Simple low-overhead operations"}
                ]
            }
        ]
    },
    "agro_inputs": {
        "title": "Agro-Inputs & Farm Solutions Center",
        "description": "Configure fertilizer, seed, and pesticide dealership parameters.",
        "iconName": "sparkles",
        "variant": "indigo",
        "questions": [
            {
                "id": "input_mix",
                "question": "What agricultural inputs will you distribute?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Certified Hybrid Seeds, Fertilizers & Crop Protection", "value": "standard_inputs", "desc": "High seasonal turnover (Urea, DAP, NPK, Hybrid Paddy/Cotton)"},
                    {"label": "Organic Fertilizers, Bio-Pesticides & Micronutrients", "value": "organic_inputs", "desc": "Rapidly growing demand with 22-28% gross margins"},
                    {"label": "Drip Irrigation, Sprayers & Farm Implements", "value": "farm_equipment", "desc": "High-ticket items with government subsidy integration"}
                ]
            },
            {
                "id": "storage_facility",
                "question": "What is your warehouse / godown storage capacity?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Licensed Dry Godown (500+ Bag Capacity)", "value": "godown_ready", "desc": "Essential for bulk seasonal fertilizer storage"},
                    {"label": "Renting Godown Space Near Mandi", "value": "rented_godown", "desc": "Flexible capacity without heavy civil capital"},
                    {"label": "Shop Backroom Storage (100-200 Bags)", "value": "shop_storage", "desc": "Lower setup cost for seed & specialty inputs"}
                ]
            },
            {
                "id": "credit_cycle",
                "question": "How will you manage farmer seasonal credit cycles?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Strict Cash & 15-day Credit against Mandi slips", "value": "low_credit", "desc": "Protects cash flow, eliminates bad debts"},
                    {"label": "Seasonal Harvest-Linked Credit (60-90 Days)", "value": "harvest_credit", "desc": "Higher total sales volume; requires Rs. 2-3 Lakh working capital buffer"}
                ]
            }
        ]
    },
    "goat": {
        "title": "Goat & Sheep Husbandry",
        "description": "Define flock size, housing structure, and breeding cycles.",
        "iconName": "trending",
        "variant": "purple",
        "questions": [
            {
                "id": "herd_size",
                "question": "What breeding herd size are you starting with?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "10 Does + 1 Buck (Starter Family Unit)", "value": "10_1", "desc": "Low initial risk, manageable in backyard setup"},
                    {"label": "20 Does + 2 Bucks (Optimal Unit for Subsidy)", "value": "20_2", "desc": "Prime tier for 33% National Livestock Mission (NLM) grant"},
                    {"label": "50+ Herd Unit (Commercial Goat Farm)", "value": "50_plus", "desc": "High annual offspring turnover with dedicated shed"}
                ]
            },
            {
                "id": "housing_type",
                "question": "What rearing & housing method will you adopt?",
                "type": "select",
                "allow_custom": False,
                "options": [
                    {"label": "Elevated Wooden Slatted Floor (Stall-Fed Zero Grazing)", "value": "stall_fed", "desc": "Clean hygiene, cuts disease by 70%, rapid weight gain to 30kg"},
                    {"label": "Semi-Intensive (Day Grazing + Night Concentrate Feed)", "value": "semi_intensive", "desc": "Balanced feed cost with healthy animal exercise"},
                    {"label": "Open Range Pasture Grazing", "value": "open_grazing", "desc": "Lowest infrastructure cost"}
                ]
            },
            {
                "id": "breed_choice",
                "question": "Which goat breed will you raise?",
                "type": "select",
                "allow_custom": True,
                "options": [
                    {"label": "Sirohi / Barbari / Jamnapari (Fast Weight Gain)", "value": "meat_breeds", "desc": "Reaches 25-30kg in 7 months, top festival price"},
                    {"label": "Black Bengal (High Fecundity / 2-3 Kids per delivery)", "value": "black_bengal", "desc": "Fastest herd multiplication rate"},
                    {"label": "Hardy Local Native Breed", "value": "local_breed", "desc": "Zero acclimatization risk, lowest mortality"}
                ]
            }
        ]
    }
}

class QuestionGenerator:
    """
    Generates dynamic, domain-tailored questions for any rural enterprise idea.
    """

    @classmethod
    def get_category_key(cls, idea: str) -> str:
        idea_lower = idea.lower()
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

    @classmethod
    def generate_questions(cls, business_idea: str, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns tailored questions for the business idea.
        """
        category_key = cls.get_category_key(business_idea)
        district = location.get("district", "Your District")
        state = location.get("state", "Your State")

        if category_key in CURATED_QUESTION_BANKS:
            bank = CURATED_QUESTION_BANKS[category_key]
            return {
                "category": category_key,
                "title": bank["title"],
                "description": f"Tailored for {district}, {state}. {bank['description']}",
                "iconName": bank.get("iconName", "idea"),
                "variant": bank.get("variant", "blue"),
                "questions": bank["questions"]
            }

        # Fallback dynamic questions for any custom or non-standard rural business idea
        return {
            "category": "custom",
            "title": f"{business_idea.title()} Plan",
            "description": f"Customized operational parameters to calculate required capital and revenue in {district}, {state}.",
            "iconName": "target",
            "variant": "indigo",
            "questions": [
                {
                    "id": "operational_scale",
                    "question": f"What scale are you planning for this {business_idea}?",
                    "type": "select",
                    "allow_custom": True,
                    "options": [
                        {"label": "Micro / Starter Scale (Low Risk)", "value": "micro", "desc": "Operated directly by 1-2 people, minimal capital risk"},
                        {"label": "Mid-Sized Commercial Unit", "value": "medium", "desc": "Standard commercial machinery and reliable daily capacity"},
                        {"label": "High-Capacity Hub / Processing Facility", "value": "large", "desc": "Higher initial investment, high volume turnover"}
                    ]
                },
                {
                    "id": "premises_setup",
                    "question": "What is your workspace or premises requirement?",
                    "type": "select",
                    "allow_custom": True,
                    "options": [
                        {"label": "Already have owned premises / land", "value": "owned", "desc": "Zero lease burden, fast operational setup"},
                        {"label": "Need to lease / rent commercial space", "value": "rented", "desc": "Monthly rental with security deposit advance"},
                        {"label": "Need new shed / building construction", "value": "construction", "desc": "Requires civil construction capital"}
                    ]
                },
                {
                    "id": "machinery_equipment",
                    "question": "What machinery or equipment will you require?",
                    "type": "select",
                    "allow_custom": True,
                    "options": [
                        {"label": "Semi-Automatic Processing Machinery", "value": "semi_auto", "desc": "Balances throughput with manageable electricity & capital"},
                        {"label": "Basic Manual Tools & Display Fixtures", "value": "basic_tools", "desc": "Lowest upfront capital expenditure"},
                        {"label": "Fully Automated Processing Plant", "value": "full_auto", "desc": "Maximizes efficiency & consistency"}
                    ]
                },
                {
                    "id": "target_customer",
                    "question": "Who will be your primary buyers or clients?",
                    "type": "select",
                    "allow_custom": True,
                    "options": [
                        {"label": "Direct Village & Local Town Retail Consumers", "value": "retail_b2c", "desc": "Immediate cash & digital payments"},
                        {"label": "Wholesalers, Mandi Traders & Processing Mills", "value": "wholesale_b2b", "desc": "Bulk volume contracts with periodic settlements"},
                        {"label": "Government Procurement & Cooperatives", "value": "institutional", "desc": "Guaranteed price support"}
                    ]
                },
                {
                    "id": "sourcing_inputs",
                    "question": "Where will you source your raw materials & supplies?",
                    "type": "select",
                    "allow_custom": True,
                    "options": [
                        {"label": "Local District Farmers & Mandi", "value": "local_mandi", "desc": "Low transportation cost, immediate availability"},
                        {"label": "Direct Industrial Manufacturing Hubs", "value": "direct_factory", "desc": "Lowest unit purchase price"},
                        {"label": "State Cooperative Federation Supplies", "value": "coop_supply", "desc": "Standard quality with institutional rates"}
                    ]
                }
            ]
        }

