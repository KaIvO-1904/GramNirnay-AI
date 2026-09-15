import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.rag_engine import RAGEngine
from backend.ontology.models import FinancialParams, BusinessProfile
from pydantic import BaseModel

def test_rag_with_pydantic():
    print("Testing RAG with Pydantic models...")
    engine = RAGEngine()
    
    profile = BusinessProfile(
        business_idea="Poultry Farm",
        category="poultry",
        available_capital=100000,
        location="Mysore, Karnataka",
        experience_years=2
    )
    
    params = FinancialParams(
        setup_cost=500000,
        monthly_revenue=50000,
        monthly_expenses=30000,
        user_capital=100000
    )
    
    try:
        results = engine.get_best_schemes(profile, params)
        print(f"Success! Matched {len(results)} schemes.")
    except Exception as e:
        print(f"Failed: {e}")
        raise e

def test_rag_with_dicts():
    print("Testing RAG with dictionaries...")
    engine = RAGEngine()
    
    profile = {
        "business_idea": "Poultry Farm",
        "available_capital": 100000,
    }
    
    params = {
        "setup_cost": 500000,
    }
    
    try:
        results = engine.get_best_schemes(profile, params)
        print(f"Success! Matched {len(results)} schemes.")
    except Exception as e:
        print(f"Failed: {e}")
        raise e

if __name__ == "__main__":
    try:
        test_rag_with_pydantic()
        test_rag_with_dicts()
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
