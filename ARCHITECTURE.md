# Architecture Document - GramNirnay.ai

## 1. High-Level System Design
GramNirnay.ai is designed as a decoupled system where deterministic logic is strictly separated from probabilistic AI reasoning.

### Core Flow:
`User Input` $\rightarrow$ `Input Validation` $\rightarrow$ `(Data Engine + AI Engine)` $\rightarrow$ `Decision Engine` $\rightarrow$ `Explainability Engine` $\rightarrow$ `User Advisory`

## 2. Component Breakdown

### A. Data Engine (Deterministic)
- **Geospatial Processor**: Handles location-based queries.
- **Demographic Analyzer**: Processes population and economic data.
- **Market Proxy Engine**: Calculates demand/competition scores based on available data or weighted proxies.

### B. AI/RAG Engine (Probabilistic)
- **Business Interpreter**: Extracts structured parameters from free-text business ideas.
- **Scheme RAG**:
    - **Vector DB**: Stores official government scheme documentation.
    - **Retrieval**: Semantic search for matching schemes.
    - **Synthesis**: Generates eligibility summaries with citations.
- **Risk Reasoner**: Identifies qualitative risks based on business type and location.

### C. Decision Engine (Deterministic + AI)
- **Financial Engine**:
    - Calculates Project Cost, ROI, Break-even, and EMI.
    - **Strict Rule**: No LLM for math. All calculations use pure Python.
- **Scoring Model**: Combines data engine scores and AI reasoning into a final "Viability Score".

### D. Explainability Engine (AI)
- Synthesizes the "Why" behind the Decision Engine's output.
- Maps findings to evidence (e.g., "Demand is high because [Data Source X] shows Y").

## 3. Data Flow
1. **Profile Entry**: User provides Location, Capital, Idea, and Experience.
2. **Context Gathering**:
   - Backend fetches local data (Data Engine).
   - LLM extracts structured business specs (AI Engine).
3. **Viability Assessment**:
   - Financial engine runs projections.
   - Market scores are calculated.
4. **Financing Match**:
   - RAG retrieves schemes based on profile and project cost.
5. **Final Synthesis**:
   - LLM generates the final report, including modifications (e.g., "reduce cow count").

## 4. Technology Stack
- **Frontend**: Next.js 15+, Tailwind CSS.
- **Backend**: FastAPI (Python 3.12+).
- **Vector Store**: pgvector (PostgreSQL).
- **LLM**: Claude 3.5 Sonnet.
- **Deployment**: Vercel (Frontend), Docker/AWS/Azure (Backend).

## 5. Trust & Hallucination Mitigation
- **Source-Backed RAG**: All scheme claims must have a `source_url`.
- **Calculation Guardrails**: Financial results are computed in code, then passed to the LLM as "facts" for explanation.
- **Confidence Levels**: AI outputs are tagged with Low/Medium/High confidence based on data availability.
