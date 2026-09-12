# Implementation Plan: Render Deployment Fix & Production Audit for GramNirnay.ai

## 1. Problem Analysis

### Current Blockers
- **Render Startup Failure**: `ModuleNotFoundError: No module named 'backend'`. This is caused by a mismatch between the execution context (Root vs /backend) and the use of relative imports. `run_backend.py` masks this locally by hacking `sys.path`.
- **Backend Syntax Error**: `backend/main.py` has a `SyntaxError` in `promote_mapping` where a non-default argument `status` follows default arguments (`district`, `biz`).
- **Backend Import Error**: `backend/main.py` attempts to import `OrchestrationManager` from `backend/orchestration/manager.py`, which does not exist.
- **Broken Relative Imports**: `backend/orchestration/workflow.py` uses `from .scoring` instead of `from ..scoring` to access sibling packages.

### Production Risks
- **Hardcoded Configs**: `allowed_origins` is fixed to `localhost:3000`.
- **Env Var Management**: Lack of a formalized variable matrix for production.
- **Business Logic Gaps**: No explicit rejection for non-target ventures (e.g., "Coffee" is treated as generic instead of rejected).
- **Frontend Stability**: Potential hydration and build errors in the Next.js app.

---

## 2. Implementation Strategy

### Phase 1: Critical Fixes (Blocker Removal)
**Goal**: Get the backend to boot on Render.

1. **Fix `backend/main.py`**:
   - Move `status: str` before `district: Optional[str] = None` and `biz: str = "GENERAL"` in `promote_mapping`.
   - Remove the dead import: `from .orchestration.manager import OrchestrationManager`.
2. **Resolve Package Imports**:
   - Audit all files in `backend/orchestration/` and change relative imports for sibling packages from `.` to `..` (e.g., `from .scoring` -> `from ..scoring`).
   - Ensure `backend/__init__.py` exists to treat the directory as a package.
3. **Correct Render Configuration**:
   - **Root Directory**: `.`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Dependency Install**: Ensure Render is configured to install from `backend/requirements.txt` (or move it to root).

**Verification**: 
- Run `python -m uvicorn backend.main:app` from the root directory locally to confirm no `ImportError` or `SyntaxError`.

### Phase 2: Environment & Configuration Audit
**Goal**: Ensure the app is configurable without code changes.

1. **Config Variable Matrix**:
   - Create a comprehensive list of required environment variables (OpenAI keys, DB URLs, CORS origins).
2. **Update `backend/config.py`**:
   - Change `allowed_origins` to read from an environment variable: `allowed_origins: List[str] = Field(default=["http://localhost:3000"], validation_alias="ALLOWED_ORIGINS")`.
   - Ensure `app_port` defaults to `os.environ.get("PORT", 8000)`.
3. **Frontend API Update**:
   - Audit `frontend/` for hardcoded `http://localhost:8000`.
   - Implement a `.env.local` / `.env.production` pattern for `NEXT_PUBLIC_API_BASE_URL`.

**Verification**:
- Change `ALLOWED_ORIGINS` in a local `.env` and verify CORS behavior.

### Phase 3: Business Logic & Regression
**Goal**: Ensure deterministic and correct business behavior.

1. **Implement Venture Filtering**:
   - In `backend/interpreter.py` or a new `backend/validation/filter.py`, implement a "Rejected Venture" check.
   - Add a list of non-target keywords (e.g., "Coffee" -> reject if it doesn't meet rural agricultural criteria).
2. **Verify Poultry Logic**:
   - Create a test script to verify that "Country Chicken" -> `category: poultry` and "Coffee" -> `status: rejected`.
3. **Financial Determinism**:
   - Verify that `FinancialEngine` produces consistent results for the same inputs across different platforms.

**Verification**:
- Run a test matrix of 10 diverse business ideas and verify their categorization.

### Phase 4: Frontend & Robustness Audit
**Goal**: Eliminate runtime errors and improve reliability.

1. **Frontend Build Audit**:
   - Run `npm install` -> `npm run lint` -> `npm run build`.
   - Resolve any TypeScript errors or ESLint warnings.
   - Fix hydration issues by auditing `useEffect` and `useState` in pages.
2. **Path Compatibility**:
   - Verify all file operations in the backend use `pathlib.Path` instead of string concatenation to ensure Windows -> Linux compatibility.
3. **Health Endpoint**:
   - Expand `/` or implement `/health` to return a JSON status of downstream dependencies (LLM, Data files).

**Verification**:
- Successful `npm run build` with zero errors.
- `GET /health` returns 200 OK.

---

## 3. Testing Matrix

| Category | Test Case | Expected Result |
| :--- | :--- | :--- |
| **Startup** | `python -m uvicorn backend.main:app` | App starts without errors |
| **API** | `GET /health` | 200 OK with dependency status |
| **Business** | Input: "Country Chicken" | `category: poultry`, financial model generated |
| **Business** | Input: "Coffee" | Rejected or flagged as non-target |
| **Location** | Input: "District X, State Y" | Correct `LocationIdentity` returned |
| **Finance** | Input: Poultry (2500 birds) | Deterministic `setup_cost` matching benchmarks |
| **External** | OpenAI API Down | Graceful fallback to deterministic models |

## 4. Critical Files for Implementation
- `backend/main.py` (Syntax & Import fixes)
- `backend/config.py` (Env var migration)
- `backend/orchestration/workflow.py` (Relative import fixes)
- `backend/interpreter.py` (Business logic filtering)
- `run_backend.py` (Audit for removal of path hacks)
EOF`
