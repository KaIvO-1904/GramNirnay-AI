# Implementation Plan: Render Deployment Resolution & Production Audit for GramNirnay.ai

## 1. Overview
This plan resolves the `ModuleNotFoundError` and `SyntaxError` blocking the Render deployment and conducts a comprehensive production audit to ensure the system is robust, consistent, and production-ready.

## 2. Immediate Blockers (Phase 1: Backend Stability)
**Goal**: Get the backend booting without errors.

### 2.1 Fix SyntaxError in `backend/main.py`
- **Issue**: In `promote_mapping`, the `status: str` argument follows default arguments `district` and `biz`.
- **Fix**: Move `status: str` before arguments with default values.

### 2.2 Resolve ImportError in `backend/main.py`
- **Issue**: `from .orchestration.manager import OrchestrationManager` fails because `backend/orchestration/manager.py` is missing.
- **Fix**: Remove the dead import. If `OrchestrationManager` was intended for use, identify the replacement (likely `WorkflowManager` in `backend/orchestration/workflow.py`).

### 2.3 Verify Requirements
- Ensure `backend/requirements.txt` is complete and compatible with the Render environment (Python 3.12).

**Verification**: Run `python -m uvicorn backend.main:app` locally and ensure it starts without import or syntax errors.

---

## 3. Environment & Deployment (Phase 2: Render Configuration)
**Goal**: Correct the deployment mismatch and secure configuration.

### 3.1 Render Configuration
- **Root Directory**: Set to `.` (Project Root).
- **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`.
- **Reasoning**: Using `-m uvicorn` from the root allows the `backend` package to be resolved correctly, supporting the relative imports used within the package.

### 3.2 Configuration Audit (`backend/config.py`)
- **Dynamic CORS**: Update `allowed_origins` to read from an environment variable (e.g., `ALLOWED_ORIGINS`).
- **Hardcoded Values**: Remove any remaining hardcoded ports or localhost references.

### 3.3 Environment Variable Matrix
Create a matrix for all required variables:

| Variable | Default | Purpose | Prod Value |
|---|---|---|---|
| `PORT` | `8000` | Backend port | Render provided |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS whitelist | `https://gramnirnay.ai` |
| `OPENAI_API_KEY` | None | LLM Auth | [Secret] |
| `OPENAI_BASE_URL` | None | LLM Proxy/Base | [Optional] |
| `LLM_MODEL` | `gpt-4o-mini` | Model selection | `gpt-4o-mini` |
| `NEXT_PUBLIC_API_URL`| `http://localhost:8000` | Frontend API target | `https://api.gramnirnay.ai` |

**Verification**: Deploy to Render and verify the "Health Check" returns `{"status": "online"}`.

---

## 4. API & Integration Audit (Phase 3: Consistency)
**Goal**: Ensure seamless communication between frontend and backend.

### 4.1 Case Consistency Audit
- Audit all Pydantic models and API endpoints for `snake_case` (Python convention) vs `camelCase` (JS convention).
- **Target**: Use `camelCase` for API requests/responses and `snake_case` internally in Python.
- **Check**: `UserProfile`, `GenerateQuestionsRequest`, `SavedAnalysisRequest`.

### 4.2 CORS & Base URL Verification
- Verify `frontend/lib/api.ts` uses `process.env.NEXT_PUBLIC_API_URL`.
- Test cross-origin requests from a staged frontend to the Render backend.

**Verification**: Use Postman/Insomnia to verify all endpoints return correct case and status codes.

---

## 5. Frontend Production Audit (Phase 4: Stability)
**Goal**: Zero-error production build.

### 5.1 Build Pipeline
- Execute: `npm install` $\rightarrow$ `npm run lint` $\rightarrow$ `npm run build`.
- Fix all TypeScript errors (especially in `types/` and `lib/`).
- Fix ESLint warnings that block build.

### 5.2 Hydration & Runtime Audit
- Inspect `app/layout.tsx` and `app/page.tsx` for potential hydration mismatches.
- Verify that all environment variables are prefixed with `NEXT_PUBLIC_`.

**Verification**: Successful `npm run build` without errors.

---

## 6. Business Logic & Regression (Phase 5: Accuracy)
**Goal**: Ensure the AI doesn't break deterministic rules.

### 6.1 Poultry Logic Verification
- **Scenario A**: User input "Coffee" $\rightarrow$ Backend should reject/flag as non-poultry.
- **Scenario B**: User input "Country Chicken" $\rightarrow$ Backend should accept as poultry.
- **Check**: Verify logic in `backend/interpreter.py` and `backend/validation/rules_engine.py`.

### 6.2 Financial Determinism
- Verify ROI, Break-even, and Setup Cost calculations are deterministic and not modified by the LLM.
- **Check**: `backend/financial_engine.py` and `backend/services/financial/calculator.py`.

### 6.3 LLM Guardrails
- Ensure LLM responses are constrained by the financial engine's outputs.

**Verification**: Run a test suite of 10 "Golden Scenarios" (including Poultry/Non-Poultry) and compare results against a verified baseline.

---

## 7. Robustness & Compatibility (Phase 6: Hardening)
**Goal**: OS-agnostic and fail-safe operation.

### 7.1 Path Compatibility
- Audit all file paths (e.g., `data/` access). Replace any string concatenation paths with `pathlib.Path`.
- **Check**: `backend/config.py` and `backend/main.py` demo scenario loading.

### 7.2 Graceful Failure
- Implement try-except blocks around LLM and Database calls.
- Ensure the API returns a structured error (`GramNirnayError`) instead of a raw 500 traceback.

### 7.3 Health Endpoint
- Implement a robust `/health` endpoint that checks:
    - LLM Connectivity
    - Data Directory Access
    - Memory Store status

**Verification**: Simulate service failure (e.g., invalid API key) and verify graceful error response.

---

## 8. Testing Matrix (Phase 7: Final Validation)

| Test Category | Test Case | Expected Result | Priority |
|---|---|---|---|
| **Startup** | Render Cold Boot | App boots in < 60s, `/health` = 200 | P0 |
| **API** | CORS Request | Allowed from Production Domain | P0 |
| **Business** | Poultry Filter | "Country Chicken" OK, "Coffee" Fail | P1 |
| **Finance** | Break-even Calc | Consistent result for fixed inputs | P1 |
| **Location** | District Resolve | Valid district returns canonical ID | P2 |
| **Services** | LLM Timeout | Returns cached or generic response | P2 |

---

## Critical Files for Implementation
- `backend/main.py` (Blocker fixes, Health endpoint)
- `backend/config.py` (Env vars, CORS)
- `backend/requirements.txt` (Dependency audit)
- `frontend/lib/api.ts` (API URL check)
- `backend/interpreter.py` & `backend/validation/rules_engine.py` (Business logic)
