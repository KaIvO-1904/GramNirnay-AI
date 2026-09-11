# Demo Guide - GramNirnay.ai MVP

## 1. Setup Instructions

### Backend
1. `cd backend`
2. `pip install -r requirements.txt`
3. `python main.py` (runs on `http://localhost:8000`)

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev` (runs on `http://localhost:3000`)

## 2. The "Killer Demo" Workflow

To showcase the system to judges, follow this path:

### Step 1: Landing Page
- Open `http://localhost:3000`.
- Click **"Try Demo Scenario"**.

### Step 2: The Magic (Internal Flow)
- The frontend calls `/api/demo/dairy_ramanagara`.
- The backend:
    1. Loads the **Ramanagara Dairy** profile.
    2. Runs the **Deterministic Financial Engine** $\rightarrow$ calculates a real ROI and Break-even based on actual dairy economics.
    3. Runs the **RAG Engine** $\rightarrow$ filters and ranks government schemes (e.g., MUDRA, PMEGP) based on the $\text{₹}6$ lakh funding gap.
    4. Synthesizes the final report.

### Step 3: The Report (User View)
The judge sees:
- **Business Viability Score**: (e.g., 78/100).
- **The Verdict**: "Proceed with Modification".
- **The "Why"**: Clear reasons why the business works in Ramanagara.
- **The Financials**: A clear ROI and EMI table.
- **The modification**: "Start with 10-12 cows instead of 15 to lower risk."
- **Matched Schemes**: Evidence-backed scheme suggestions.

## 3. Key Talking Points for Judges

- **"Business Viability Before Financing"**: We don't just find loans; we tell the entrepreneur if the business is a good idea first.
- **Deterministic Math**: "All our financial calculations are done in code, not by an LLM, ensuring 100% accuracy."
- **Hyper-Local Focus**: "We use district-level proxies to move beyond generic national advice."
- **Explainable AI**: "Every recommendation is backed by data and answers the 'Why'."
