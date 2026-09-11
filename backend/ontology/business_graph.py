from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field
from enum import Enum

class BusinessSector(str, Enum):
    LIVESTOCK = "livestock"
    SERVICES = "services"
    TRADING = "trading"
    AGRI = "agri"
    MANUFACTURING = "manufacturing"
    OTHER = "other"

class AttributeRequirement(BaseModel):
    name: str
    description: str
    allowed_values: Optional[List[str]] = None # None means free text
    is_required: bool = True

class BusinessNode(BaseModel):
    id: str
    canonical_name: str
    description: str
    parent_id: Optional[str] = None
    required_attributes: List[AttributeRequirement] = []
    incompatible_attributes: Dict[str, List[str]] = {} # attr_name -> list of forbidden values

# The Deterministic Business Graph
BUSINESS_GRAPH: Dict[str, BusinessNode] = {
    # Sectors
    "LIVESTOCK": BusinessNode(id="LIVESTOCK", canonical_name="Livestock", description="Animal husbandry and rearing"),
    "SERVICES": BusinessNode(id="SERVICES", canonical_name="Services", description="Professional and personal services"),
    "TRADING": BusinessNode(id="TRADING", canonical_name="Trading", description="Buying and selling of goods"),
    "AGRI": BusinessNode(id="AGRI", canonical_name="Agriculture", description="Crop farming and plantation"),
    "MANUFACTURING": BusinessNode(id="MANUFACTURING", canonical_name="Manufacturing", description="Small scale production"),
    "OTHER": BusinessNode(id="OTHER", canonical_name="Other", description="Miscellaneous businesses"),

    # Livestock -> Poultry
    "POULTRY": BusinessNode(
        id="POULTRY",
        canonical_name="Poultry",
        description="Birds rearing for meat or eggs",
        parent_id="LIVESTOCK"
    ),
    "BROILER": BusinessNode(
        id="BROILER",
        canonical_name="Broiler",
        description="Chicken reared for meat",
        parent_id="POULTRY",
        required_attributes=[
            AttributeRequirement(name="shed_type", description="Type of poultry shed", allowed_values=["Open", "Controlled"]),
            AttributeRequirement(name="feed_source", description="Where do you get feed?", allowed_values=["Local", "Company", "Self-made"])
        ],
        incompatible_attributes={"egg_production_target": ["High", "Industrial"]}
    ),
    "LAYER": BusinessNode(
        id="LAYER",
        canonical_name="Layer",
        description="Chicken reared for eggs",
        parent_id="POULTRY",
        required_attributes=[
            AttributeRequirement(name="egg_collection_freq", description="How often are eggs collected?", allowed_values=["Daily", "Twice-Daily"])
        ]
    ),
    "COUNTRY_CHICKEN": BusinessNode(
        id="COUNTRY_CHICKEN",
        canonical_name="Country Chicken",
        description="Indigenous/Free-range birds",
        parent_id="POULTRY",
        required_attributes=[
            AttributeRequirement(name="grazing_area", description="Area available for grazing", allowed_values=["Small", "Medium", "Large"])
        ]
    ),
    "BREEDING": BusinessNode(
        id="BREEDING",
        canonical_name="Breeding",
        description="Hatching and breeding stock",
        parent_id="POULTRY"
    ),
    "HATCHERY": BusinessNode(
        id="HATCHERY",
        canonical_name="Hatchery",
        description="Egg hatching facility",
        parent_id="POULTRY"
    ),

    # Livestock -> Dairy
    "DAIRY": BusinessNode(
        id="DAIRY",
        canonical_name="Dairy",
        description="Milk production",
        parent_id="LIVESTOCK"
    ),
    "COW_DAIRY": BusinessNode(
        id="COW_DAIRY",
        canonical_name="Cow Dairy",
        description="Cow milk farming",
        parent_id="DAIRY",
        required_attributes=[
            AttributeRequirement(name="breed", description="Breed of cow", allowed_values=["Gir", "Sahiwal", "Jersey", "HF", "Other"])
        ]
    ),
    "BUFFALO_DAIRY": BusinessNode(
        id="BUFFALO_DAIRY",
        canonical_name="Buffalo Dairy",
        description="Buffalo milk farming",
        parent_id="DAIRY"
    ),

    # Services -> Tailoring
    "TAILORING": BusinessNode(
        id="TAILORING",
        canonical_name="Tailoring",
        description="Clothing and garment making",
        parent_id="SERVICES"
    ),
    "CUSTOM_STITCH": BusinessNode(
        id="CUSTOM_STITCH",
        canonical_name="Custom Stitching",
        description="Bespoke clothing",
        parent_id="TAILORING",
        required_attributes=[
            AttributeRequirement(name="machine_type", description="Type of sewing machine", allowed_values=["Manual", "Electric", "Industrial"])
        ]
    ),

    # Trading -> Grocery
    "GROCERY": BusinessNode(
        id="GROCERY",
        canonical_name="Grocery Store",
        description="Retail food and household items",
        parent_id="TRADING"
    ),
    "KIRANA": BusinessNode(
        id="KIRANA",
        canonical_name="Kirana Store",
        description="Traditional small grocery shop",
        parent_id="GROCERY"
    ),

    # Agri -> Vegetable
    "VEGETABLE_FARM": BusinessNode(
        id="VEGETABLE_FARM",
        canonical_name="Vegetable Farming",
        description="Growing vegetables for sale",
        parent_id="AGRI"
    ),
    "ORGANIC_VEG": BusinessNode(
        id="ORGANIC_VEG",
        canonical_name="Organic Vegetables",
        description="Pesticide-free vegetable farming",
        parent_id="VEGETABLE_FARM",
        required_attributes=[
            AttributeRequirement(name="certification", description="Certification status", allowed_values=["Certified", "In-transition", "Uncertified"])
        ],
        incompatible_attributes={"fertilizer_type": ["Chemical", "Synthetic"]}
    ),

    # Mfg -> Small Mfg
    "SMALL_MFG": BusinessNode(
        id="SMALL_MFG",
        canonical_name="Small Manufacturing",
        description="Small scale production of goods",
        parent_id="MANUFACTURING"
    ),
    "AGRI_TOOLS": BusinessNode(
        id="AGRI_TOOLS",
        canonical_name="Agri-Tool Manufacturing",
        description="Making tools for farmers",
        parent_id="SMALL_MFG"
    ),
}

def get_children_of(node_id: str) -> List[str]:
    """Returns all immediate children of a node."""
    return [nid for nid, node in BUSINESS_GRAPH.items() if node.parent_id == node_id]

def get_all_descendants(node_id: str) -> Set[str]:
    """Recursively finds all descendants of a node."""
    descendants = set()
    children = [nid for nid, node in BUSINESS_GRAPH.items() if node.parent_id == node_id]
    for child in children:
        descendants.add(child)
        descendants.update(get_all_descendants(child))
    return descendants

def get_node_by_canonical_name(name: str) -> Optional[BusinessNode]:
    """Finds a node by its canonical name (case insensitive)."""
    for node in BUSINESS_GRAPH.values():
        if node.canonical_name.lower() == name.lower():
            return node
    return None
