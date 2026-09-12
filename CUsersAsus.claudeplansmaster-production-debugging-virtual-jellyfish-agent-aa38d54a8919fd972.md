# Implementation Plan: GramNirnay.ai Production Audit & Render Fix

## 1. Executive Summary
This plan addresses the critical failure of the Render deployment (`ModuleNotFoundError: No module named 'backend'`) and performs a comprehensive production audit to ensure the platform is robust, consistent, and production-ready.

### Critical Blockers Identified
- **Render Startup**: Mismatch between root directory and start command.
- **Syntax Error**: `backend/main.py` has a `SyntaxError` in `promote_mapping` (non-default argument following default arguments).
- **Import Error**: `backend/main.py` attempts to import `orchestration.manager`, which is missing from the codebase.

---

## 2. Detailed Implementation Phases

### Phase 1: Immediate Blockers & Backend Startup (High Priority)
**Goal**: Get the backend running on Render.

1.  **Fix `backend/main.py` Syntax**:
    - Move `status: str` before `district` and `biz` in the `promote_mapping` function signature.
2.  **Fix `backend/main.py` Imports**:
    - Remove `from .orchestration.manager import OrchestrationManager`.
    - Verify if `OrchestrationManager` functionality is now handled by `WorkflowManager` (found in `backend/orchestration/workflow.py`).
3.  **Standardize Startup Command**:
    - Root Directory: `.`
    - Start Command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4.  **Verification**:
    - Local test: `python -m uvicorn backend.main:app` from root.
    - Verify no `ImportError` or `SyntaxError` on boot.

### Phase 2: Environment & Configuration Audit
**Goal**: Remove hardcoded values and ensure 12-factor app compliance.

1.  **Dynamic CORS**:
    - Update `backend/config.py` to read `ALLOWED_ORIGINS` from an environment variable.
    - Default to `["http://localhost:3000"]` only in dev mode.
2.  **Environment Variable Matrix**:
    - Create a comprehensive list of required variables:
        - `OPENAI_API_KEY`
        - `OPENAI_BASE_URL` (optional)
        - `LLM_MODEL`
        - `ALLOWED_ORIGINS` (comma-separated list)
        - `PORT` (provided by Render)
3.  **Remove Local-Only Logic**:
    - Audit `backend/config.py` and `run_backend.py` for any Windows-specific paths (e.g., `d:/Projects/...`). Ensure `pathlib` is used throughout.

### Phase 3: API Contract & Integration Audit
**Goal**: Ensure seamless communication between Frontend and Backend.

1.  **Endpoint Consistency**:
    - Audit all endpoints for `snake_case` vs `camelCase` consistency.
    - Frontend uses `camelCase` for some payloads (e.g., `businessIdea`); Backend uses `snake_case` for some and `camelCase` for others. Standardize on `camelCase` for API boundaries.
2.  **Health Check Implementation**:
    - Add a proper `/health` endpoint that checks:
        - LLM connectivity.
        - Data directory accessibility.
        - Basic internal state.
3.  **Frontend Base URL**:
    - Confirm `NEXT_PUBLIC_API_URL` is used consistently in `frontend/lib/api.ts`.

### Phase 4: Frontend Production Audit
**Goal**: Eliminate build-time errors and runtime hydration issues.

1.  **Build Pipeline**:
    - Run `npm install` $\rightarrow$ `npm run lint` $\rightarrow$ `npm run build`.
2.  **Error Resolution**:
    - Fix all TypeScript errors identified during build.
    - Resolve ESLint warnings that could lead to runtime bugs.
3.  **Hydration Fixes**:
    - Search for `useEffect` or `useState` patterns that cause mismatches between server and client rendering in Next.js.

### Phase 5: Business Logic & Regression Validation
**Goal**: Ensure deterministic outputs and rule compliance.

1.  **"Poultry" Logic Verification**:
    - Locate logic that differentiates "Coffee" (reject/invalid) vs "Country Chicken" (accept).
    - Ensure this logic is explicitly handled in the `BusinessInterpreter` or `ContextEngine` and not solely left to the LLM's "mood".
2.  **Financial Determinism**:
    - Audit `backend/financial_engine.py`.
    - Verify that ROI, Break-even, and Project Cost calculations are deterministic and use the provided benchmarks.
3.  **LLM Guardrails**:
    - Ensure the LLM does not bypass the deterministic financial model when generating the final viability report.

### Phase 6: Robustness & Compatibility
**Goal**: Ensure the app survives production failures.

1.  **Path Compatibility**:
    - Replace any string-based path concatenation with `pathlib.Path`.
2.  **Graceful Degradation**:
    - Implement try-except blocks around LLM calls with meaningful error messages for the user.
    - Ensure the app doesn't crash if `demo_scenarios.json` is missing.

---

## 3. Final Recommended Render Configuration

| Setting | Value |
| :--- | :--- |
| **Root Directory** | `.` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| **Environment Variables** | `OPENAI_API_KEY`, `ALLOWED_ORIGINS`, `LLM_MODEL`, `PORT` |

---

## 4. Testing Matrix

| Category | Test Case | Expected Result |
| :--- | :--- | :--- |
| **Startup** | Run start command in Linux container | Backend boots without `ModuleNotFoundError` |
| **API** | Call `/health` endpoint | Returns `{"status": "healthy"}` |
| **Business** | Input "Coffee Shop" vs "Country Chicken" | Correct viability assessment per domain rules |
| **Finance** | Fixed input $\rightarrow$ Financial Engine | Deterministic, repeatable financial numbers |
| **Location** | GPS coordinates $\rightarrow$ `/api/location/gps` | Correct `LocationIdentity` returned |
| **Auth** | Google Auth flow $\rightarrow$ `/api/auth/google` | User profile created and token returned |
