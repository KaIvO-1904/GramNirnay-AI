# Implementation Plan: Render Deployment Fix & Production Audit for GramNirnay.ai

## 1. Problem Analysis

### Current Blockers
- Render Startup Failure: ModuleNotFoundError: No module named 'backend'
- Backend Syntax Error: backend/main.py in promote_mapping
- Backend Import Error: Missing backend/orchestration/manager.py
- Broken Relative Imports: backend/orchestration/workflow.py uses . instead of ..

### Production Risks
- Hardcoded Configs: allowed_origins fixed to localhost:3000
- Env Var Management: Lack of formal matrix
- Business Logic Gaps: Coffee should be rejected
- Frontend Stability: Hydration/Build errors

## 2. Implementation Strategy

### Phase 1: Critical Fixes
1. Fix backend/main.py Syntax and Imports
2. Fix relative imports in backend/orchestration/
3. Configure Render: Root='.', Start='python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT'
