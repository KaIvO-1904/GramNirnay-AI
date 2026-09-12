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

# In-memory stores for demo purposes
USERS_DB: Dict[str, Any] = {}
USER_ANALYSES_DB: Dict[str, List[Any]] = {}
RATE_LIMIT_STORE: Dict[str, List[float]] = defaultdict(list)

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

# Initialize Firebase Admin SDK
try:
    # In production, firebase_service_account_path should be the path to the JSON file
    # or the JSON content itself.
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

    # Window: 1 minute, Limit: 60 requests
    window = 60
    limit = 60

    # Clean old timestamps
    RATE_LIMIT_STORE[client_ip] = [t for t in RATE_LIMIT_STORE[client_ip] if now - t < window]

    if len(RATE_LIMIT_STORE[client_ip]) >= limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    RATE_LIMIT_STORE[client_ip].append(now)

app = FastAPI(
    title=settings.app_title,
    description="AI-Driven Hyper-Local Business Advisory for Rural Micro-Entrepreneurs"
)

# Enable CORS for the frontend to communicate with the backend
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
workflow_manager = WorkflowManager()
location_service = LocationService()
voice_service = VoiceService()
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
    """Search for a place name and return candidates."""
    return location_service.search_place(request.query)

class LocationResolveRequest(BaseModel):
    provider_id: str
    source: LocationSource

@app.post("/api/location/resolve", dependencies=[Depends(rate_limit)])
async def resolve_location(request: LocationResolveRequest) -> LocationIdentity:
    """Confirm and resolve a location candidate to a canonical identity."""
    try:
        return location_service.resolve_location(request.provider_id, request.source)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class GpsLocationRequest(BaseModel):
    lat: float
    lng: float

@app.post("/api/location/gps", dependencies=[Depends(rate_limit)])
async def resolve_gps(request: GpsLocationRequest) -> LocationIdentity:
    """Convert GPS coordinates to a structured location identity."""
    try:
        return location_service.resolve_gps(request.lat, request.lng)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/voice/upload", dependencies=[Depends(rate_limit)])
async def upload_voice(request: Request) -> Dict[str, Any]:
    """
    Uploads audio and returns the initial transcription and normalization.
    """
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
    """
    Confirms the transcript and triggers the viability pipeline.
    """
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

@app.post("/api/memory/correct")
async def record_correction(
    user_id: str,
    session_id: str,
    phrase: str,
    canonical: str,
    lang: str,
    state: str,
    district: Optional[str] = None,
    biz: str = "GENERAL"
) -> Dict[str, Any]:
    """
    Records a user's correction of a transcribed term.
    """
    try:
        from .voice.normalization import memory_manager
        from .memory.models import RegionalContext
        region = RegionalContext(state=state, district=district)
        mapping = memory_manager.record_correction(
            user_id=user_id, session_id=session_id, phrase=phrase,
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
    """
    Retrieves all current candidate terminology mappings.
    """
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
    """
    Admin endpoint to promote a mapping to Curated Knowledge or reject it.
    """
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
async def google_auth(auth_req: GoogleAuthRequest) -> Dict[str, Any]:
    """
    Authenticate user with Google credentials using Firebase ID Token verification.
    """
    try:
        import time

        # 1. Extract and verify the Firebase ID Token
        token = auth_req.credential
        if not token:
            raise HTTPException(status_code=400, detail="Missing Firebase ID Token.")

        try:
            # Verify the token with Firebase Admin SDK
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

        # 2. Create or retrieve the user record
        user_id = f"usr_{google_id[:12]}"
        user_record = {
            "id": user_id,
            "name": name,
            "email": email,
            "avatar": avatar,
            "provider": "google",
            "last_login": int(time.time()),
        }

        USERS_DB[user_id] = user_record
        # Use the actual Firebase UID as the session token for this demo
        session_token = f"gn_jwt_{user_id}_{int(time.time())}"

        if user_id not in USER_ANALYSES_DB:
            USER_ANALYSES_DB[user_id] = []

        return {
            "user": user_record,
            "token": session_token,
            "message": "Authentication successful"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Google auth error: {e}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@app.get("/api/user/analyses")
async def get_user_analyses(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve saved analysis history for an authenticated user.
    """
    if user_id and user_id in USER_ANALYSES_DB:
        return USER_ANALYSES_DB[user_id]
    return []

@app.post("/api/user/analyses")
async def save_user_analysis(user_id: str, analysis: SavedAnalysisRequest) -> Dict[str, Any]:
    """
    Save a business viability assessment to user's backend profile.
    """
    import time
    if user_id not in USER_ANALYSES_DB:
        USER_ANALYSES_DB[user_id] = []

    analysis_item = {
        "id": f"analysis-{int(time.time())}",
        "businessIdea": analysis.businessIdea,
        "district": analysis.district,
        "state": analysis.state,
        "date": time.strftime("%Y-%m-%d"),
        "score": analysis.score,
        "recommendation": analysis.recommendation,
        "projectCost": analysis.projectCost,
        "data": analysis.data,
    }

    USER_ANALYSES_DB[user_id].insert(0, analysis_item)
    return {"status": "saved", "item": analysis_item}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to ensure all errors return a structured JSON response.
    """
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
    """
    Health check endpoint.
    """
    return {"message": "Welcome to Gram-AI API", "status": "online"}

@app.post("/api/generate-questions", dependencies=[Depends(rate_limit)])
async def generate_questions(payload: GenerateQuestionsRequest) -> Dict[str, Any]:
    """
    Generates domain-tailored MCQ questions for the user's specific business idea and location.
    """
    try:
        data = QuestionGenerator.generate_questions(payload.businessIdea, payload.location)
        return data
    except Exception as e:
        logger.exception(f"Question generation failed for '{payload.businessIdea}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

@app.post("/api/analyze-viability", dependencies=[Depends(rate_limit)])
async def analyze_viability(profile: UserProfile) -> Dict[str, Any]:
    """
    Main endpoint for analyzing the viability of a business idea without requiring the user to estimate capital.

    Flow:
    1. Interpretation: Business answers -> Required capital, revenue & cost parameters.
    2. Calculation: Run deterministic financial model.
    3. Context: Get hyper-local market proxies.
    4. RAG: Match government schemes for funding.
    """
    try:
        # Normalize location data
        loc_data = profile.location or {}
        if "state" in loc_data and loc_data["state"]:
            loc_data["state"] = normalize_state(loc_data["state"])

        location_ctx = LocationContext(**loc_data)

        # 1. AI & Domain Interpretation: Compute benchmarked capital & revenues
        if profile.answers:
            params_dict = interpreter.interpret_from_answers(
                profile.businessIdea,
                loc_data,
                profile.experience,
                profile.answers
            )
        else:
            # Fallback for legacy requests
            params_dict = interpreter.interpret(profile.businessIdea, profile.availableCapital or 0.0)

        # Apply targetInvestment override if user specifically gave one
        if profile.targetInvestment and profile.targetInvestment > 0:
            params_dict["setup_cost"] = profile.targetInvestment

        params_dict["user_capital"] = profile.availableCapital or 0.0

        # Convert to new standardized schemas
        venture_profile = VentureProfile(
            businessIdea=profile.businessIdea,
            location=location_ctx,
            experience=profile.experience,
            availableCapital=profile.availableCapital or 0.0,
            targetInvestment=profile.targetInvestment or 0.0,
            answers=profile.answers or {}
        )

        benchmarks = FinancialBenchmarks(**params_dict)

        # Use the new WorkflowManager for the intelligence pipeline
        # Pass the interpreted profile and financial params to skip re-interpretation
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
            user_capital=profile.availableCapital or 0.0
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
    """
    Retrieves a pre-defined demo scenario for showcase purposes.
    """
    try:
        import os
        scenario_path = os.path.join(settings.data_dir, "demo_scenarios.json")

        with open(scenario_path, "r") as f:
            scenarios = json.load(f)

        if scenario_id not in scenarios:
            raise HTTPException(status_code=404, detail="Scenario not found")

        scenario = scenarios[scenario_id]

        # Run actual financial engine on the scenario data
        financials = fin_engine.compute_full_model(scenario["financial_params"])
        financials["user_capital"] = scenario["profile"]["availableCapital"]

        # Use RAG engine to find schemes for this scenario
        schemes = rag_engine.get_best_schemes(scenario["profile"], scenario["financial_params"])

        # Construct a response that matches the analysis result format
        # We simulate a viability score based on the financial result
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
        logger.exception(f"Error retrieving demo scenario {scenario_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.app_host, port=settings.app_port)
