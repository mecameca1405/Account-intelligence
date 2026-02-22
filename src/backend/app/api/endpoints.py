"""
endpoints.py — API Routes
All REST endpoints for the Account Intelligence platform.
"""

from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.api.dependencies import (
    get_current_user, hash_password, verify_password,
    create_access_token
)
from app.services.ai_engine import AIEngine
from app.services.rag_service import RAGService
from app.services.web_search import WebSearchService
from app.config import settings

router = APIRouter()

# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=schemas.TokenResponse, tags=["Auth"])
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT token."""
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
    }


@router.post("/auth/register", response_model=schemas.UserResponse, tags=["Auth"])
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user (admin only in production)."""
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = models.User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Accounts ──────────────────────────────────────────────────────────────────

@router.get("/accounts", response_model=List[schemas.AccountResponse], tags=["Accounts"])
def list_accounts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all accounts with pagination."""
    return db.query(models.Account).offset(skip).limit(limit).all()


@router.post("/accounts/analyze", response_model=schemas.AnalysisResponse, tags=["Accounts"])
async def analyze_account(
    request: schemas.AccountAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Analyze a company by URL:
    1. Scrape public web data
    2. Extract signals and entities with AI
    3. Generate propensity score, recommendations and speech
    """
    # 1. Check if account already exists
    account = db.query(models.Account).filter(
        models.Account.company_url == request.url
    ).first()

    # 2. Web scraping
    web_svc = WebSearchService()
    web_data = await web_svc.scrape_company(request.url)

    # 3. Create or update account
    if not account:
        account = models.Account(
            company_name=web_data.get("company_name", "Unknown"),
            company_url=request.url,
            industry=web_data.get("industry"),
            country=web_data.get("country"),
            created_by=current_user.id,
        )
        db.add(account)
        db.commit()
        db.refresh(account)

    # 4. AI Analysis
    ai = AIEngine()

    # 4a. Detect signals
    signals_data = await ai.detect_signals(web_data.get("content", ""))
    signals = []
    for s in signals_data:
        signal = models.Signal(
            account_id=account.id,
            signal_type=s["type"],
            signal_text=s["text"],
            confidence_score=s["confidence"],
            signal_source=request.url,
        )
        db.add(signal)
        signals.append(signal)

    # 4b. Propensity score
    score_value, breakdown = await ai.compute_propensity_score(signals_data)
    prop_score = models.PropensityScore(
        account_id=account.id,
        score=score_value,
        score_breakdown=breakdown,
        model_version="v1.0",
    )
    db.add(prop_score)

    # 4c. Recommendations (RAG-enhanced)
    rag = RAGService()
    recs_data = await rag.get_recommendations(web_data.get("content", ""), signals_data)
    recs = []
    for r in recs_data:
        rec = models.Recommendation(
            account_id=account.id,
            product_name=r["product"],
            product_family=r.get("family"),
            relevance_score=r["relevance"],
            rationale=r["rationale"],
        )
        db.add(rec)
        recs.append(rec)

    # 4d. Speech generation
    speech_text = await ai.generate_speech(account, signals_data, recs_data)
    speech = models.Speech(
        account_id=account.id,
        speech_text=speech_text,
        tone="consultivo",
        word_count=len(speech_text.split()),
        model_used=settings.LLM_MODEL_NAME,
    )
    db.add(speech)

    # Update last analyzed
    from datetime import datetime
    account.last_analyzed_at = datetime.utcnow()
    db.commit()
    db.refresh(account)

    return schemas.AnalysisResponse(
        account=account,
        signals=signals,
        propensity=prop_score,
        recommendations=recs,
        speech=speech,
    )


@router.get("/accounts/{account_id}", response_model=schemas.AccountResponse, tags=["Accounts"])
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return account


@router.get("/accounts/{account_id}/propensity", response_model=schemas.PropensityScoreResponse, tags=["Accounts"])
def get_propensity(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    score = (
        db.query(models.PropensityScore)
        .filter(models.PropensityScore.account_id == account_id)
        .order_by(models.PropensityScore.calculated_at.desc())
        .first()
    )
    if not score:
        raise HTTPException(status_code=404, detail="Score no encontrado")
    return score


@router.get("/accounts/{account_id}/recommendations", response_model=List[schemas.RecommendationResponse], tags=["Accounts"])
def get_recommendations(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Recommendation)
        .filter(models.Recommendation.account_id == account_id)
        .order_by(models.Recommendation.relevance_score.desc())
        .all()
    )


@router.get("/accounts/{account_id}/speech", response_model=schemas.SpeechResponse, tags=["Accounts"])
def get_speech(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    speech = (
        db.query(models.Speech)
        .filter(models.Speech.account_id == account_id)
        .order_by(models.Speech.created_at.desc())
        .first()
    )
    if not speech:
        raise HTTPException(status_code=404, detail="Speech no encontrado")
    return speech


# ── Top 5 ─────────────────────────────────────────────────────────────────────

@router.get("/top5/today", response_model=List[schemas.Top5ItemResponse], tags=["Top5"])
def get_top5_today(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Returns today's Top 5. If not yet generated, compute it from
    the latest propensity scores across all accounts.
    """
    today = date.today()
    existing = (
        db.query(models.Top5History)
        .filter(models.Top5History.date == today)
        .order_by(models.Top5History.rank)
        .all()
    )
    if existing:
        return [
            schemas.Top5ItemResponse(
                rank=e.rank,
                account_id=e.account_id,
                company_name=e.account.company_name,
                score_snapshot=e.score_snapshot,
                date=e.date,
            )
            for e in existing
        ]

    # Compute Top 5 dynamically
    top_scores = (
        db.query(models.PropensityScore, models.Account)
        .join(models.Account, models.Account.id == models.PropensityScore.account_id)
        .order_by(models.PropensityScore.score.desc())
        .limit(5)
        .all()
    )

    result = []
    for rank, (score, account) in enumerate(top_scores, start=1):
        entry = models.Top5History(
            date=today,
            rank=rank,
            account_id=account.id,
            score_snapshot=score.score,
        )
        db.add(entry)
        result.append(
            schemas.Top5ItemResponse(
                rank=rank,
                account_id=account.id,
                company_name=account.company_name,
                score_snapshot=score.score,
                date=today,
            )
        )
    db.commit()
    return result


# ── Feedback ──────────────────────────────────────────────────────────────────

@router.post("/feedback", response_model=schemas.FeedbackResponse, tags=["Feedback"])
def submit_feedback(
    feedback_data: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    feedback = models.Feedback(
        user_id=current_user.id,
        **feedback_data.model_dump(),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback
