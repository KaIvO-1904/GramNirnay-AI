# MVP Detailed Proposal - GramNirnay.ai

## 1. Minimum Viable Data Model

### User Profile
```json
{
  "userId": "uuid",
  "location": { "lat": "float", "lng": "float", "district": "string", "state": "string" },
  "businessIdea": "string",
  "availableCapital": "decimal",
  "experience": "int (years)",
  "targetInvestment": "decimal"
}
```

### Business Specifications (AI Extracted)
```json
{
  "category": "string",
  "estimatedSetupCost": "decimal",
  "fixedCostsMonthly": "decimal",
  "variableCostsPerUnit": "decimal",
  "expectedRevenuePerUnit": "decimal",
  "unitsPerMonth": "int",
  "operationalRisks": ["string"]
}
```

### Scheme Record
```json
{
  "schemeId": "string",
  "name": "string",
  "ministry": "string",
  "eligibility": { "minCapital": "decimal", "maxCapital": "decimal", "categories": ["string"] },
  "benefit": { "subsidyPercent": "float", "loanAmount": "decimal", "interestRate": "float" },
  "sourceUrl": "string",
  "lastVerified": "date"
}
```

## 2. Minimum Datasets Required
For the MVP, we will use a hybrid approach:
- **Primary Scenario Data**: A curated JSON file containing detailed market proxies for one specific district (e.g., Ramanagara, KA) for Dairy/Agri businesses.
- **Scheme Dataset**: A CSV/JSON of 20-30 major rural entrepreneurship schemes (PMEGP, Mudra, etc.).
- **Demographic Data**: Open Government Data (OGD) India - District-level population and agri-output statistics.

## 3. AI/RAG Architecture
- **Embedding Model**: `text-embedding-3-small` (OpenAI) or `cohere-embed-english-v3`.
- **Vector Store**: `pgvector` on PostgreSQL.
- **Retrieval Strategy**: Hybrid search (Semantic + Keyword for scheme names).
- **Reranking**: Simple cosine similarity for MVP.
- **Prompting**: Few-shot prompting for structured JSON output to ensure the LLM doesn't hallucinate financial numbers.

## 4. API Contracts

### POST `/api/analyze-viability`
**Input**: `User Profile`
**Output**:
```json
{
  "viabilityScore": "int",
  "marketAnalysis": { "demand": "int", "competition": "int", "accessibility": "int" },
  "financials": { "roi": "float", "breakEvenMonths": "int", "emi": "decimal" },
  "recommendation": "Proceed | Proceed with Modification | Reconsider",
  "modifications": ["string"],
  "matchedSchemes": [ { "schemeId": "string", "confidence": "float" } ]
}
```

### GET `/api/schemes/{id}`
**Output**: Full `Scheme Record` + AI generated eligibility explanation.

## 5. Frontend Screen Specifications
- **Screen 1 (Onboarding)**: Multi-step form. Minimalist, high-contrast.
- **Screen 2 (Local Intel)**: Map view (using Leaflet/Google Maps) + "Opportunity Cards" (Demand, Competition, Seasonality).
- **Screen 3 (Financials)**: "Financial Health" dashboard. Comparison chart (User Capital vs. Required Capital). EMI calculator preview.
- **Screen 4 (Final Report)**: The "Verdict". Big score, Recommendation badge, Risk list, and Scheme cards with "Apply Now" links.

## 6. Financial Model & Scoring

### Financial Logic
- **ROI** = `(Annual Net Profit / Total Investment) * 100`
- **Break-even (Months)** = `Total Setup Cost / Monthly Contribution Margin`
- **EMI** = `[P x R x (1+R)^N] / [(1+R)^N - 1]` (P=Principal, R=Monthly Rate, N=Tenure)

### Viability Score (Weighted Average)
- **Market Demand (30%)**
- **Financial Feasibility (30%)**
- **Competition Level (20%)**
- **Risk Profile (20%)**

## 7. Highest-Risk Technical Components
1. **Data Scarcity**: Finding real hyper-local data for every possible business.
   - *Mitigation*: Use a transparent proxy architecture; clearly label "Estimates".
2. **LLM Hallucinations**: LLM inventing scheme eligibility.
   - *Mitigation*: Force RAG to use strict source documents; avoid free-form generation for eligibility.
3. **Calculation Errors**: LLM doing math.
   - *Mitigation*: Absolute separation. Backend handles all math; LLM only explains the result.
