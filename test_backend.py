"""
Direct Test script for GramNirnay.ai backend
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

def test_all():
    print("==========================================")
    print(" GRAMNIRNAY.AI BACKEND DEBUG VERIFICATION")
    print("==========================================")
    
    print("\n--- 1. Testing Root / Health Endpoint ---")
    r1 = client.get("/")
    print(f"Status: {r1.status_code}")
    print(f"Response: {r1.json()}")
    assert r1.status_code == 200, f"Expected 200, got {r1.status_code}"

    print("\n--- 2. Testing Demo Scenario: dairy_ramanagara ---")
    r2 = client.get("/api/demo/dairy_ramanagara")
    print(f"Status: {r2.status_code}")
    assert r2.status_code == 200, f"Expected 200, got {r2.status_code}"
    data2 = r2.json()
    print(f"Viability Status: {data2.get('financials', {}).get('is_viable')}")
    print(f"Project Cost: Rs. {data2.get('financials', {}).get('total_project_cost'):,}")
    print(f"ROI: {data2.get('financials', {}).get('roi_percent')}%")
    print(f"Matched Schemes: {len(data2.get('matchedSchemes', []))} schemes found")

    print("\n--- 3. Testing Viability Analysis Endpoint /api/analyze-viability ---")
    sample_profile = {
        "location": {"district": "Ramanagara", "state": "Karnataka"},
        "businessIdea": "Dairy farm with 10 cows",
        "availableCapital": 100000.0,
        "experience": 3,
        "targetInvestment": 400000.0
    }
    r3 = client.post("/api/analyze-viability", json=sample_profile)
    print(f"Status: {r3.status_code}")
    assert r3.status_code == 200, f"Expected 200, got {r3.status_code}"
    data3 = r3.json()
    print(f"Viability Score: {data3.get('viabilityScore')}/100")
    print(f"Recommendation: {data3.get('recommendation')}")
    print(f"Monthly Net Profit: Rs. {data3.get('financials', {}).get('monthly_net_profit'):,}")

    print("\n--- 4. Testing Google Auth Endpoint /api/auth/google ---")
    sample_auth = {
        "name": "Ramesh Patel",
        "email": "ramesh.patel@gmail.com",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
        "google_id": "google_test_12345"
    }
    r4 = client.post("/api/auth/google", json=sample_auth)
    print(f"Status: {r4.status_code}")
    assert r4.status_code == 200, f"Expected 200, got {r4.status_code}"
    user_data = r4.json()
    user_id = user_data["user"]["id"]
    print(f"Authenticated User: {user_data['user']['name']} ({user_id})")
    print(f"Session Token: {user_data['token']}")

    print("\n--- 5. Testing Save Analysis to User Account ---")
    save_payload = {
        "businessIdea": "Organic Hydroponics Farm",
        "district": "Pune",
        "state": "Maharashtra",
        "score": 88,
        "recommendation": "Proceed",
        "projectCost": 650000.0,
        "data": {"test": True}
    }
    r5 = client.post(f"/api/user/analyses?user_id={user_id}", json=save_payload)
    print(f"Status: {r5.status_code}")
    assert r5.status_code == 200, f"Expected 200, got {r5.status_code}"
    print(f"Saved Record ID: {r5.json().get('item', {}).get('id')}")

    print("\n--- 6. Testing Fetch Analyses for User ---")
    r6 = client.get(f"/api/user/analyses?user_id={user_id}")
    print(f"Status: {r6.status_code}")
    assert r6.status_code == 200, f"Expected 200, got {r6.status_code}"
    records = r6.json()
    print(f"Fetched {len(records)} record(s) for user {user_id}")
    print("\n--- 7. Testing Question Generation Endpoint /api/generate-questions ---")
    cloth_q = client.post("/api/generate-questions", json={
        "businessIdea": "Apparel and saree cloth shop",
        "location": {"district": "Surat", "state": "Gujarat"}
    })
    print(f"Status: {cloth_q.status_code}")
    assert cloth_q.status_code == 200, f"Expected 200, got {cloth_q.status_code}"
    q_data = cloth_q.json()
    print(f"Generated {len(q_data.get('questions', []))} questions for {q_data.get('title')}")
    for q in q_data.get('questions', []):
        print(f" - {q['question']} ({len(q.get('options', []))} options)")

    print("\n--- 8. Testing Viability Analysis from Questionnaire (No Capital Asked) ---")
    poultry_answers = {
        "location": {"district": "Coimbatore", "state": "Tamil Nadu"},
        "businessIdea": "Broiler Poultry Farm",
        "experience": 2,
        "answers": {
            "poultry_type": "broiler",
            "flock_size": "2500",
            "shed_status": "need_shed",
            "contract_farming": "contract"
        }
    }
    r8 = client.post("/api/analyze-viability", json=poultry_answers)
    print(f"Status: {r8.status_code}")
    assert r8.status_code == 200, f"Expected 200, got {r8.status_code}"
    res8 = r8.json()
    fin8 = res8.get("financials", {})
    print(f"Category: {res8.get('category')}")
    print(f"Viability Score: {res8.get('viabilityScore')}/100")
    print(f"Recommended Setup Cost: Rs. {fin8.get('total_project_cost'):,}")
    print(f"Min Viable Capital: Rs. {fin8.get('min_viable_capital'):,}")
    print(f"Projected Monthly Revenue: Rs. {fin8.get('monthly_revenue'):,}")
    print(f"Projected Monthly Expenses: Rs. {fin8.get('monthly_expenses'):,}")
    print(f"Projected Monthly Net Profit: Rs. {fin8.get('monthly_net_profit'):,}")
    print(f"Capital Breakdown: {fin8.get('capital_breakdown')}")

    print("\n==========================================")
    print(" [SUCCESS] ALL BACKEND SERVICES VERIFIED 100% OK")
    print("==========================================")

if __name__ == "__main__":
    test_all()

