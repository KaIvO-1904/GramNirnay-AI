# Roadmap - GramNirnay.ai MVP (48-60 Hour Sprint)

## Goal: High-Probability-to-Win Prototype
The priority is a **convincing vertical slice**: One phenomenal demo scenario (e.g., Rural Dairy Business) that proves the end-to-end flow.

---

## Phase 1: Foundation (Hours 0-12)
- [ ] **Shared**: Finalize API contracts and Data Schema.
- [ ] **Backend**: Set up FastAPI project structure and basic routing.
- [ ] **Frontend**: Set up Next.js project with basic routing and theme.
- [ ] **Data**: Identify and collect 1 primary dataset for the demo scenario.
- [ ] **AI**: Set up LLM prompts for structured business extraction.

## Phase 2: Core Engines (Hours 12-30)
- [ ] **Financial Engine**: Implement deterministic EMI, Break-even, and ROI logic. (P0)
- [ ] **RAG Layer**: Set up vector store and ingest primary scheme documents. (P0)
- [ ] **Data Engine**: Implement proxy scoring for demand and competition. (P1)
- [ ] **AI Engine**: Build the risk analysis and modification logic. (P1)
- [ ] **Frontend**: Build Screen 1 (Profile) and Screen 2 (Local Intelligence).

## Phase 3: Integration & Reporting (Hours 30-48)
- [ ] **Decision Engine**: Integrate Financial + Market + AI outputs. (P0)
- [ ] **Report Generator**: Build the AI Decision Report (Screen 4). (P0)
- [ ] **Frontend**: Build Screen 3 (Financials) and Screen 4 (Report).
- [ ] **Integration**: Connect Frontend to Backend API.
- [ ] **Demo Mode**: Implement "One-Click Demo Scenario".

## Phase 4: Polish & Validation (Hours 48-60)
- [ ] **Testing**: Unit tests for financial engine and adversarial tests for AI.
- [ ] **UI Polish**: Ensure professional, government-style aesthetic.
- [ ] **Docs**: Complete ARCHITECTURE.md, DATA_SOURCES.md, and DEMO.md.
- [ ] **Pitch Prep**: Finalize PPT based on the working MVP.

---

## Team Allocation (Parallelization)

| Role | Primary Ownership | Key MVP Deliverable |
| :--- | :--- | :--- |
| **Person 1 (AI/ML)** | LLM Pipeline & Reasoning | Structured outputs, Risk Engine |
| **Person 2 (AI/Data)** | RAG & Scheme DB | Vector DB, Scheme Ingestion |
| **Person 3 (Backend)** | API & Financials | Financial Engine, Scoring API |
| **Person 4 (Frontend)** | User Interface | 4-Screen Application Flow |
| **Person 5 (Data Viz)** | Geospatial & Charts | Map view, Financial Charts |
| **Person 6 (Integration)**| Security & Testing | API Security, E2E Testing, Deploy |
