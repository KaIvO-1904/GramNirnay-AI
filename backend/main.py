from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import json
import time
from collections import defaultdict

from .config import settings
from .logger import setup_logging, logger
from .financial_engine import FinancialEngine
from .rag_engine import RAGEngine
from .interpreter import BusinessInterpreter
from .context_engine import ContextEngine
from .question_generator import QuestionGenerator
from .utils import normalize_state
from .core.schemas.context import LocationContext
from .core.schemas.domain import VentureProfile, FinancialBenchmarks, MarketAnalysis
from .database import SessionLocal, User, Analysis, get_db
from sqlalchemy.orm import Session

# In-memory store for rate limiting only (as per goal: process-local is okay)
RATE_LIMIT_STORE: Dict[str, List[float]] = defaultdict(list)

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate(settings.firebase_service_account_path)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase Admin SDK initialized successfully")
except Exception as e:
    logger.warning(f"Firebase Admin SDK failed to initialize: {e}. Auth verification will be disabled.")

# Initialize Logging
setup_logging()

def rate_limit(request: Request):
    """Simple in-memory rate limiter to prevent API abuse."""
    client_ip = request.client.host
    now = time.time()
    window = 60
    limit = 60
    RATE_LIMIT_STORE[client_ip] = [t for t in RATE_LIMIT_STORE[client_ip] if now - t < window]
    if len(RATE_LIMIT_STORE[client_ip]) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
    RATE_LIMIT_STORE[client_ip].append(now)

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Any:
    """
    Verify the Firebase ID token from the Authorization header.
    Returns the User record from the database.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token.")

    token = auth_header.split(" ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        google_id = decoded_token['uid']
        user_id = f"usr_{google_id[:12]}"

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found. Please authenticate first.")

        return user
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")

app = FastAPI(
    title=settings.app_title,
    description="AI-Driven Hyper-Local Business Advisory for Rural Micro-Entrepreneurs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(",") if settings.allowed_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
from .orchestration.workflow import WorkflowManager
from .location.service import LocationService
from .location.models import LocationCandidate, LocationIdentity, LocationSource
from .voice.service import VoiceService
from .intelligence.providers import AIIntelligenceProvider
workflow_manager = WorkflowManager()
location_service = LocationService()
voice_service = VoiceService()
ai_provider = AIIntelligenceProvider()
fin_engine = FinancialEngine()
rag_engine = RAGEngine()
interpreter = BusinessInterpreter()
ctx_engine = ContextEngine()

class GenerateQuestionsRequest(BaseModel):
    businessIdea: str = Field(..., min_length=2, description="The business idea")
    location: Dict[str, Any] = Field(default_factory=dict, description="Location data (district, state)")

class UserProfile(BaseModel):
    location: Dict[str, Any] = Field(default_factory=dict, description="User location data (district, state)")
    businessIdea: str = Field(..., min_length=2, description="The business idea to analyze")
    experience: int = Field(0, ge=0, description="Years of experience in the field")
    availableCapital: Optional[float] = Field(0.0, description="Optional capital provided by user")
    targetInvestment: Optional[float] = Field(0.0, description="Optional target investment")
    answers: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tailored questionnaire answers")

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    google_id: Optional[str] = None

class SavedAnalysisRequest(BaseModel):
    businessIdea: str
    district: str
    state: str
    score: int
    recommendation: str
    projectCost: float
    data: Optional[Dict[str, Any]] = None

class LocationSearchRequest(BaseModel):
    query: str

@app.post("/api/location/search", dependencies=[Depends(rate_limit)])
async def search_location(request: LocationSearchRequest) -> List[LocationCandidate]:
    return location_service.search_place(request.query)

class LocationResolveRequest(BaseModel):
    provider_id: str
    source: LocationSource

@app.post("/api/location/resolve", dependencies=[Depends(rate_limit)])
async def resolve_location(request: LocationResolveRequest) -> LocationIdentity:
    try:
        return location_service.resolve_location(request.provider_id, request.source)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class GpsLocationRequest(BaseModel):
    lat: float
    lng: float

@app.post("/api/location/gps", dependencies=[Depends(rate_limit)])
async def resolve_gps(request: GpsLocationRequest) -> LocationIdentity:
    try:
        return location_service.resolve_gps(request.lat, request.lng)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/voice/upload", dependencies=[Depends(rate_limit)])
async def upload_voice(request: Request) -> Dict[str, Any]:
    try:
        audio_file = await request.body()
        language_hint = request.query_params.get("language_hint")
        if not audio_file:
            raise HTTPException(status_code=400, detail="No audio data provided.")
        result = await voice_service.process_audio(audio_file, language_hint)
        return result.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Voice upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@app.post("/api/voice/confirm", dependencies=[Depends(rate_limit)])
async def confirm_voice(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        confirmed_text = payload.get("confirmed_text")
        if not confirmed_text or not confirmed_text.strip():
            raise HTTPException(status_code=400, detail="Confirmed text cannot be empty.")
        state = workflow_manager.run_pipeline(user_input=confirmed_text)
        return workflow_manager.format_for_frontend(state)
    except Exception as e:
        logger.exception(f"Voice confirmation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# ── Learning Memory Endpoints ──

@app.post("/api/memory/correct", dependencies=[Depends(get_current_user)])
async def record_correction(
    current_user: Any,
    session_id: str,
    phrase: str,
    canonical: str,
    lang: str,
    state: str,
    district: Optional[str] = None,
    biz: str = "GENERAL"
) -> Dict[str, Any]:
    try:
        from .voice.normalization import memory_manager
        from .memory.models import RegionalContext
        region = RegionalContext(state=state, district=district)
        mapping = memory_manager.record_correction(
            user_id=current_user.id, session_id=session_id, phrase=phrase,
            canonical=canonical, lang=lang, region=region, biz=biz
        )
        return {"status": "recorded", "mapping": mapping.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Correction recording failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/terms")
async def get_learned_terms() -> List[Dict[str, Any]]:
    try:
        from .voice.normalization import memory_manager
        return [m.model_dump() for m in memory_manager.get_community_stats()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/promote")
async def promote_mapping(
    phrase: str,
    lang: str,
    state: str,
    status: str, # "verified" or "rejected"
    district: Optional[str] = None,
    biz: str = "GENERAL",
) -> Dict[str, Any]:
    try:
        from .voice.normalization import memory_manager
        from .memory.models import RegionalContext, VerificationStatus
        region = RegionalContext(state=state, district=district)
        mapping = memory_manager.promote_mapping(
            phrase=phrase, lang=lang, region=region, biz=biz,
            status=VerificationStatus(status)
        )
        return {"status": "updated", "mapping": mapping.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Promotion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/google")
async def google_auth(auth_req: GoogleAuthRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        import time
        token = auth_req.credential
        if not token:
            raise HTTPException(status_code=400, detail="Missing Firebase ID Token.")
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            google_id = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name', 'Rural Entrepreneur')
            avatar = decoded_token.get('picture', '')
        except Exception as e:
            logger.error(f"Firebase token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid or expired Firebase token.")
        if not email:
            raise HTTPException(status_code=400, detail="User email not found in token.")
        user_id = f"usr_{google_id[:12]}"
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(
                id=user_id,
                name=name,
                email=email,
                avatar=avatar,
                provider="google",
                last_login=int(time.time())
            )
            db.add(user)
            db.commit()
        else:
            user.last_login = int(time.time())
            db.commit()
        session_token = f"gn_jwt_{user_id}_{int(time.time())}"
        return {
            "user": {"id": user.id, "name": user.name, "email": user.email, "avatar": user.avatar},
            "token": session_token,
            "message": "Authentication successful"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Google auth error: {e}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.get("/api/user/analyses", dependencies=[Depends(get_current_user)])
async def get_user_analyses(current_user: Any, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).all()
    return [
        {
            "id": a.id,
            "businessIdea": a.business_idea,
            "district": a.district,
            "state": a.state,
            "date": a.date,
            "score": a.score,
            "recommendation": a.recommendation,
            "projectCost": a.project_cost,
            "data": a.data
        } for a in analyses
    ]

@app.post("/api/user/analyses", dependencies=[Depends(get_current_user)])
async def save_user_analysis(current_user: Any, analysis: SavedAnalysisRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    import time
    import uuid
    analysis_item = Analysis(
        id=f"analysis-{uuid.uuid4().hex[:12]}",
        user_id=current_user.id,
        business_idea=analysis.businessIdea,
        district=analysis.district,
        state=analysis.state,
        date=time.strftime("%Y-%m-%d"),
        score=analysis.score,
        recommendation=analysis.recommendation,
        project_cost=analysis.projectCost,
        data=analysis.data
    )
    db.add(analysis_item)
    db.commit()
    return {"status": "saved", "item": {"id": analysis_item.id, "businessIdea": analysis_item.business_idea}}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "code": "INTERNAL_SERVER_ERROR"
        }
    )

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    return {"message": "Welcome to Gram-AI API", "status": "online"}

@app.get("/api/health/llm")
async def health_llm() -> Dict[str, Any]:
    try:
        start_time = time.time()
        response = ai_provider._query_ai("Ping. Reply with 'pong'.")
        latency = (time.time() - start_time) * 1000
        return {
            "status": "healthy",
            "model": ai_provider.model,
            "latency_ms": round(latency, 2),
            "response": response
        }
    except Exception as e:
        logger.error(f"LLM Health Check Failed: {e}")
        raise HTTPException(status_code=503, detail=f"LLM unavailable: {str(e)}")

@app.post("/api/generate-questions", dependencies=[Depends(rate_limit)])
async def generate_questions(payload: GenerateQuestionsRequest) -> Dict[str, Any]:
    try:
        data = QuestionGenerator.generate_questions(payload.businessIdea, payload.location)
        return data
    except Exception as e:
        logger.exception(f"Question generation failed for '{payload.businessIdea}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

@app.post("/api/analyze-viability", dependencies=[Depends(rate_limit)])
async def analyze_viability(profile: UserProfile) -> Dict[str, Any]:
    try:
        loc_data = profile.location or {}
        if "state" in loc_data and loc_data["state"]:
            loc_data["state"] = normalize_state(loc_data["state"])
        location_ctx = LocationContext(**loc_data)
        if profile.answers:
            params_dict = interpreter.interpret_from_answers(
                profile.businessIdea,
                loc_data,
                profile.experience,
                profile.answers
            )
        else:
            params_dict = interpreter.interpret(profile.businessIdea, profile.availableCapital or 0.0)
        if profile.targetInvestment and profile.targetInvestment > 0:
            params_dict["setup_cost"] = profile.targetInvestment
        params_dict["user_capital"] = profile.availableCapital or 0.0
        venture_profile = VentureProfile(
            businessIdea=profile.businessIdea,
            location=location_ctx,
            experience=profile.experience,
            availableCapital=profile.availableCapital or 0.0,
            targetInvestment=profile.targetInvestment or 0.0,
            answers=profile.answers or {}
        )
        benchmarks = FinancialBenchmarks(**params_dict)
        from .ontology.models import BusinessProfile, FinancialParams
        biz_profile = BusinessProfile(
            business_idea=profile.businessIdea,
            category=params_dict.get("category", "other"),
            available_capital=profile.availableCapital or 0.0,
            location=f"{loc_data.get('district', 'Unknown')}, {loc_data.get('state', 'Unknown')}",
            experience_years=profile.experience
        )
        fin_params = FinancialParams(
            setup_cost=params_dict.get("setup_cost", 0.0),
            monthly_revenue=params_dict.get("monthly_revenue", 0.0),
            monthly_expenses=params_dict.get("monthly_expenses", 0.0),
            interest_rate=params_dict.get("interest_rate", 0.0),
            tenure_years=params_dict.get("tenure_years", 5),
            user_capital=profile.availableCapital or 0.0,
            capital_breakdown=params_dict.get("capital_breakdown", {}),
            business_blueprint=params_dict.get("business_blueprint"),
            startup_roadmap=params_dict.get("startup_roadmap"),
            regulatory_requirements=params_dict.get("regulatory_requirements"),
            risk_matrix=params_dict.get("risk_matrix")
        )
        state = workflow_manager.run_pipeline(
            user_input=profile.businessIdea,
            profile=biz_profile,
            financial_params=fin_params
        )
        return workflow_manager.format_for_frontend(state)
    except Exception as e:
        logger.exception(f"Analysis failed for idea '{profile.businessIdea}': {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/demo/{scenario_id}")
async def get_demo_scenario(scenario_id: str) -> Dict[str, Any]:
    try:
        import os
        scenario_path = os.path.join(settings.data_dir, "demo_scenarios.json")
        with open(scenario_path, "r") as f:
            scenarios = json.load(f)
        if scenario_id not in scenarios:
            raise HTTPException(status_code=404, detail="Scenario not found")
        scenario = scenarios[scenario_id]
        financials = fin_engine.compute_full_model(scenario["financial_params"])
        financials["user_capital"] = scenario["profile"]["availableCapital"]
        schemes = rag_engine.get_best_schemes(scenario["profile"], scenario["financial_params"])
        viability_score = 85 if financials["is_viable"] else 45
        return {
            "viabilityScore": viability_score,
            "recommendation": "Proceed" if viability_score >= 80 else "Proceed with Modification" if viability_score >= 50 else "Reconsider",
            "category": scenario["profile"].get("category", "micro_enterprise"),
            "marketAnalysis": scenario["market_proxies"],
            "financials": financials,
            "interpreter_reasoning": f"Demo analysis for {scenario['profile']['businessIdea']} in {scenario['profile']['location']['district']}.",
            "modifications": scenario["ai_insights"]["modifications"],
            "matchedSchemes": [
                {
                    "schemeId": s.schemeId,
                    "name": s.name,
                    "ministry": s.ministry,
                    "benefit": s.benefit,
                    "sourceUrl": s.sourceUrl,
                    "eligibility": s.eligibility
                } for s in schemes
            ],
            "is_demo": True
        }
    except FileNotFoundError:
        logger.error("demo_scenarios.json not found")
        raise HTTPException(status_code=500, detail="Demo data not found")
    except Exception as e:
        logger.exception(f"Error retrieving demo {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
