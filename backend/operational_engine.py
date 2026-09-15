from typing import List, Dict, Any, Optional
from .ontology.models import BusinessCategory

class OperationalEngine:
    """
    Deterministic engine for generating business blueprints, roadmaps,
    regulatory requirements, and risk matrices based on business category.
    No LLM calls allowed in this class.
    """

    def __init__(self):
        # Templates mapped by BusinessCategory
        self.templates = {
            BusinessCategory.AGRICULTURE: {
                "blueprint": {
                    "flow": [
                        {"step": "Land Acquisition/Lease", "desc": "Secure fertile land with appropriate soil quality and water access."},
                        {"step": "Crop Selection", "desc": "Select high-yield, market-demand crops based on regional soil and climate analysis."},
                        {"step": "Infrastructure Setup", "desc": "Install irrigation systems, fencing, and storage facilities."},
                        {"step": "Sowing & Cultivation", "desc": "Implement scientific planting schedules and nutrient management."},
                        {"step": "Harvest & Post-Harvest", "desc": "Efficient harvesting and primary processing to reduce wastage."},
                        {"step": "Market Distribution", "desc": "Connect with Mandis, wholesalers, or direct-to-consumer channels."}
                    ],
                    "inputs": ["Seeds", "Fertilizers", "Water", "Agricultural Labor", "Farm Equipment"],
                    "outputs": ["Raw Produce", "Processed Crops", "Organic Compost"]
                },
                "roadmap": [
                    {"week": 1, "tasks": ["Soil testing and land survey", "Secure land lease/ownership", "Finalize crop selection"]},
                    {"week": 2, "tasks": ["Procure seeds and fertilizers", "Set up basic water irrigation", "Hire seasonal labor"]},
                    {"week": 3, "tasks": ["Land preparation (plowing/tilling)", "Install fencing", "Set up storage shed"]},
                    {"week": 4, "tasks": ["Sowing/Planting phase", "Implement fertilization schedule", "Set up pest monitoring"]},
                ],
                "requirements": [
                    {"doc": "Land Records/Title Deed", "status": "Required", "source": "Local Revenue Office"},
                    {"doc": "Agricultural License", "status": "Recommended", "source": "Dept. of Agriculture"},
                    {"doc": "Water Usage Permit", "status": "Conditional", "source": "Water Resources Board"},
                ],
                "risks": [
                    {"risk": "Climate Volatility", "severity": "High", "probability": "Medium", "mitigation": "Crop insurance and diversified planting."},
                    {"risk": "Pest Infestation", "severity": "Medium", "probability": "High", "mitigation": "Integrated Pest Management (IPM) and organic bio-controls."},
                    {"risk": "Market Price Fluctuations", "severity": "Medium", "probability": "High", "mitigation": "Contract farming and value-addition processing."}
                ]
            },
            BusinessCategory.DAIRY: {
                "blueprint": {
                    "flow": [
                        {"step": "Livestock Procurement", "desc": "Acquire high-yield cattle breeds with verified health certificates."},
                        {"step": "Shed Construction", "desc": "Build hygienic, ventilated shelters with proper waste management."},
                        {"step": "Feeding & Health Management", "desc": "Implement balanced nutrition and regular veterinary check-ups."},
                        {"step": "Milking Operations", "desc": "Setup hygienic milking process (manual or automated)."},
                        {"step": "Cold Chain Integration", "desc": "Install chilling units to maintain milk quality."},
                        {"step": "Distribution Network", "desc": "Establish supply contracts with dairies or local retail outlets."}
                    ],
                    "inputs": ["Cattle", "Fodder", "Veterinary Care", "Milking Equipment", "Cooling Units"],
                    "outputs": ["Raw Milk", "Curd/Paneer (Value added)", "Organic Manure"]
                },
                "roadmap": [
                    {"week": 1, "tasks": ["Identify cattle breed and source", "Finalize shed design and location", "Apply for livestock loans"]},
                    {"week": 2, "tasks": ["Construct cattle shed and feeding troughs", "Procure milking equipment", "Set up waste disposal"]},
                    {"week": 3, "tasks": ["Purchase and transport cattle", "Initial health screenings", "Setup fodder storage"]},
                    {"week": 4, "tasks": ["Start milking cycle", "Establish daily collection schedule", "Contract with local dairy cooperative"]},
                ],
                "requirements": [
                    {"doc": "Livestock Registration", "status": "Required", "source": "Animal Husbandry Dept"},
                    {"doc": "Health/Veterinary Certificates", "status": "Required", "source": "Govt Veterinarian"},
                    {"doc": "Trade License", "status": "Required", "source": "Local Municipality"},
                ],
                "risks": [
                    {"risk": "Disease Outbreak", "severity": "High", "probability": "Medium", "mitigation": "Strict vaccination schedules and biosecurity protocols."},
                    {"risk": "Fodder Shortage", "severity": "Medium", "probability": "Medium", "mitigation": "Hydroponic fodder setup and silage storage."},
                    {"risk": "Cold Chain Failure", "severity": "High", "probability": "Low", "mitigation": "Backup power/generators for chilling units."}
                ]
            },
            BusinessCategory.POULTRY: {
                "blueprint": {
                    "flow": [
                        {"step": "Housing Setup", "desc": "Construct temperature-controlled poultry sheds with proper ventilation."},
                        {"step": "Chick Procurement", "desc": "Source high-quality day-old chicks from certified hatcheries."},
                        {"step": "Brooding & Feeding", "desc": "Implement age-specific feeding and temperature management."},
                        {"step": "Vaccination Cycle", "desc": "Strict adherence to poultry vaccination schedules."},
                        {"step": "Processing & Packaging", "desc": "Hygienic slaughter and packaging (for meat) or egg collection."},
                        {"step": "Retail/Wholesale Linkage", "desc": "Connect with hotels, restaurants, and local markets."}
                    ],
                    "inputs": ["Chicks", "Poultry Feed", "Vaccines", "Brooders", "Packaging Materials"],
                    "outputs": ["Eggs", "Poultry Meat", "Poultry Manure"]
                },
                "roadmap": [
                    {"week": 1, "tasks": ["Finalize shed layout and ventilation", "Secure poultry license", "Source feed suppliers"]},
                    {"week": 2, "tasks": ["Complete shed construction", "Install feeders and drinkers", "Setup brooding heaters"]},
                    {"week": 3, "tasks": ["Arrival of chicks", "Implement brooding phase", "Start initial vaccination"]},
                    {"week": 4, "tasks": ["Monitor growth and feed conversion", "Scale feeding regimen", "Plan for first harvest/egg cycle"]},
                ],
                "requirements": [
                    {"doc": "Poultry Farm License", "status": "Required", "source": "Animal Husbandry Dept"},
                    {"doc": "Environmental Clearance", "status": "Conditional", "source": "Pollution Control Board"},
                    {"doc": "Health Certificate", "status": "Required", "source": "Vet Authority"},
                ],
                "risks": [
                    {"risk": "Avian Flu/Disease", "severity": "Critical", "probability": "Low", "mitigation": "Strict biosecurity and mandatory vaccination."},
                    {"risk": "Feed Price Volatility", "severity": "Medium", "probability": "High", "mitigation": "Bulk procurement and alternative feed sources."},
                    {"risk": "High Mortality Rate", "severity": "High", "probability": "Medium", "mitigation": "Optimized brooding and ventilation."}
                ]
            },
            BusinessCategory.RETAIL_KIRANA: {
                "blueprint": {
                    "flow": [
                        {"step": "Store Location Selection", "desc": "Choose a high-footfall area with visibility and accessibility."},
                        {"step": "Interior Layout Design", "desc": "Optimize shelving and counter placement for customer flow."},
                        {"step": "Supplier Onboarding", "desc": "Establish credit and supply lines with wholesalers and distributors."},
                        {"step": "Inventory Procurement", "desc": "Source a balanced mix of FMCG, staples, and local essentials."},
                        {"step": "Billing & Inventory System", "desc": "Setup POS system for billing and stock tracking."},
                        {"step": "Grand Opening & Marketing", "desc": "Local awareness campaigns and introductory offers."}
                    ],
                    "inputs": ["Rental Space", "Shelving/Racks", "Initial Stock", "POS System", "Refrigeration"],
                    "outputs": ["Retail Sales", "Customer Loyalty", "Local Market Data"]
                },
                "roadmap": [
                    {"week": 1, "tasks": ["Finalize store lease", "Register business entity", "Apply for GST/Trade license"]},
                    {"week": 2, "tasks": ["Shop interior work (painting/shelving)", "Procure POS hardware", "Source initial inventory"]},
                    {"week": 3, "tasks": ["Stocking shelves", "Set up billing software", "Hire helper/staff"]},
                    {"week": 4, "tasks": ["Soft launch", "Collect feedback", "Full opening with local promotions"]},
                ],
                "requirements": [
                    {"doc": "Trade License", "status": "Required", "source": "Municipal Corporation"},
                    {"doc": "GST Registration", "status": "Required", "source": "Tax Department"},
                    {"doc": "Food License (FSSAI)", "status": "Required", "source": "FSSAI"},
                ],
                "risks": [
                    {"risk": "Inventory Spoilage", "severity": "Medium", "probability": "Medium", "mitigation": "FIFO (First-In-First-Out) inventory management."},
                    {"risk": "High Local Competition", "severity": "Medium", "probability": "High", "mitigation": "Value-added services (home delivery, credit)."},
                    {"risk": "Working Capital Crunch", "severity": "High", "probability": "Medium", "mitigation": "Balanced credit terms with suppliers."}
                ]
            },
            BusinessCategory.OTHER: {
                "blueprint": {
                    "flow": [
                        {"step": "Market Research", "desc": "Validate demand and analyze competitor offerings."},
                        {"step": "Resource Planning", "desc": "Identify required capital, equipment, and personnel."},
                        {"step": "Setup & Procurement", "desc": "Secure location and procure essential assets."},
                        {"step": "Operational Testing", "desc": "Run a pilot or MVP to refine the process."},
                        {"step": "Full Launch", "desc": "Commence full-scale operations and marketing."},
                        {"step": "Feedback & Optimization", "desc": "Iterate based on customer and operational data."}
                    ],
                    "inputs": ["Capital", "Equipment", "Labor", "Raw Materials", "Marketing Budget"],
                    "outputs": ["Products/Services", "Revenue", "Market Presence"]
                },
                "roadmap": [
                    {"week": 1, "tasks": ["Finalize business model", "Market validation", "Budgeting"]},
                    {"week": 2, "tasks": ["Resource procurement", "Setup infrastructure", "Legal registrations"]},
                    {"week": 3, "tasks": ["Staffing and training", "Pilot run", "Process optimization"]},
                    {"week": 4, "tasks": ["Official launch", "Marketing push", "Performance monitoring"]},
                ],
                "requirements": [
                    {"doc": "General Trade License", "status": "Required", "source": "Local Authority"},
                    {"doc": "Business Registration", "status": "Required", "source": "Registrar of Companies/Firm"},
                    {"doc": "Tax Identification Number", "status": "Required", "source": "Tax Department"},
                ],
                "risks": [
                    {"risk": "Low Market Adoption", "severity": "High", "probability": "Medium", "mitigation": "Iterative MVP and aggressive local marketing."},
                    {"risk": "Operational Inefficiency", "severity": "Medium", "probability": "Medium", "mitigation": "Standard Operating Procedures (SOPs) and training."},
                    {"risk": "Capital Shortfall", "severity": "High", "probability": "Low", "mitigation": "Maintain a 20% contingency fund."}
                ]
            }
        }

    def get_blueprint(self, category: str) -> Dict[str, Any]:
        cat_enum = self._normalize_category(category)
        return self.templates.get(cat_enum, self.templates[BusinessCategory.OTHER])["blueprint"]

    def get_roadmap(self, category: str) -> List[Dict[str, Any]]:
        cat_enum = self._normalize_category(category)
        return self.templates.get(cat_enum, self.templates[BusinessCategory.OTHER])["roadmap"]

    def get_requirements(self, category: str) -> List[Dict[str, Any]]:
        cat_enum = self._normalize_category(category)
        return self.templates.get(cat_enum, self.templates[BusinessCategory.OTHER])["requirements"]

    def get_risks(self, category: str) -> List[Dict[str, Any]]:
        cat_enum = self._normalize_category(category)
        return self.templates.get(cat_enum, self.templates[BusinessCategory.OTHER])["risks"]

    def _normalize_category(self, category: str) -> BusinessCategory:
        if isinstance(category, BusinessCategory):
            return category

        try:
            # Try to match the string to the enum value
            return BusinessCategory(category.lower())
        except ValueError:
            # Fuzzy match or default to OTHER
            cat_lower = category.lower()
            for member in BusinessCategory:
                if member.value in cat_lower or cat_lower in member.value:
                    return member
            return BusinessCategory.OTHER
