"""
FastAPI application for CEE Pipeline
Main API endpoints for evaluation management
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from cee_pipeline.database.database import db
from cee_pipeline.core.pipeline import CEEPipeline
from cee_pipeline.core.tier3_evaluator import Tier3Evaluator
from cee_pipeline.core.drift_monitor import DriftMonitor
from cee_pipeline.models.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    HumanReviewRequest,
    ModelProvider,
    DashboardMetrics
)
from cee_pipeline.database.models import HumanReviewQueue, Tier3ResultDB, Evaluation

# Initialize FastAPI app
app = FastAPI(
    title="Contextual Evaluation Engine (CEE) API",
    description="Three-tier evaluation pipeline for Generative AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
tier3_evaluator = Tier3Evaluator()
drift_monitor = DriftMonitor()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    db.create_tables()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Contextual Evaluation Engine (CEE) API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/evaluate", response_model=EvaluationResponse)
async def create_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks,
    db_session: Session = Depends(db.get_db)
):
    """
    Create and run a new evaluation

    Args:
        request: Evaluation request with model output and metadata
        background_tasks: FastAPI background tasks
        db_session: Database session

    Returns:
        EvaluationResponse with results from all tiers
    """
    # Initialize pipeline with judge model from request
    pipeline = CEEPipeline(
        judge_provider=request.model_provider,
        judge_model=request.model_name
    )

    # Run evaluation
    response = pipeline.evaluate(db=db_session, request=request)

    return response


@app.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    db_session: Session = Depends(db.get_db)
):
    """
    Retrieve an evaluation by ID

    Args:
        evaluation_id: Evaluation ID
        db_session: Database session

    Returns:
        EvaluationResponse
    """
    pipeline = CEEPipeline()
    response = pipeline.get_evaluation(db=db_session, evaluation_id=evaluation_id)

    if not response:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    return response


@app.get("/evaluations/run/{run_id}", response_model=List[EvaluationResponse])
async def get_evaluations_by_run(
    run_id: str,
    db_session: Session = Depends(db.get_db)
):
    """
    Get all evaluations for a specific run

    Args:
        run_id: Run ID
        db_session: Database session

    Returns:
        List of EvaluationResponses
    """
    evaluations = db_session.query(Evaluation).filter(
        Evaluation.run_id == run_id
    ).all()

    pipeline = CEEPipeline()
    responses = []
    for eval_record in evaluations:
        response = pipeline.get_evaluation(db=db_session, evaluation_id=eval_record.id)
        if response:
            responses.append(response)

    return responses


@app.get("/review/queue", response_model=List[dict])
async def get_review_queue(
    db_session: Session = Depends(db.get_db)
):
    """
    Get all pending human review requests

    Args:
        db_session: Database session

    Returns:
        List of review requests
    """
    queue_items = db_session.query(HumanReviewQueue).filter(
        HumanReviewQueue.completed == False
    ).order_by(
        HumanReviewQueue.priority.desc(),
        HumanReviewQueue.flagged_at.asc()
    ).all()

    return [
        {
            'evaluation_id': item.evaluation_id,
            'priority': item.priority,
            'reason': item.reason,
            'flagged_at': item.flagged_at.isoformat()
        }
        for item in queue_items
    ]


@app.post("/review/{evaluation_id}/submit")
async def submit_review(
    evaluation_id: str,
    reviewer_id: str,
    verdict: str,
    notes: str,
    corrected_output: Optional[str] = None,
    db_session: Session = Depends(db.get_db)
):
    """
    Submit human review for an evaluation

    Args:
        evaluation_id: Evaluation ID
        reviewer_id: Reviewer identifier
        verdict: Review verdict (approved/rejected/needs_revision)
        notes: Reviewer notes
        corrected_output: Optional corrected output
        db_session: Database session

    Returns:
        Success message
    """
    # Check if evaluation exists
    evaluation = db_session.query(Evaluation).filter(
        Evaluation.id == evaluation_id
    ).first()

    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")

    # Submit review
    tier3_result = tier3_evaluator.submit_review(
        evaluation_id=evaluation_id,
        reviewer_id=reviewer_id,
        verdict=verdict,
        notes=notes,
        corrected_output=corrected_output
    )

    # Save to database
    tier3_db = Tier3ResultDB(
        evaluation_id=evaluation_id,
        reviewer_id=reviewer_id,
        verdict=verdict,
        notes=notes,
        corrected_output=corrected_output,
        reviewed_at=tier3_result.reviewed_at
    )
    db_session.add(tier3_db)

    # Update queue item
    queue_item = db_session.query(HumanReviewQueue).filter(
        HumanReviewQueue.evaluation_id == evaluation_id,
        HumanReviewQueue.completed == False
    ).first()

    if queue_item:
        queue_item.completed = True
        queue_item.completed_at = datetime.utcnow()

    # Update evaluation status
    evaluation.status = "completed"
    evaluation.updated_at = datetime.utcnow()

    # Recalculate trust score with Tier 3
    from cee_pipeline.core.trust_score import TrustScoreCalculator
    from cee_pipeline.models.schemas import Tier1Result, Tier2Result, Tier2Dimension

    # Reconstruct tier results
    tier1 = Tier1Result(
        pii_detected=evaluation.tier1_result.pii_detected,
        profanity_detected=evaluation.tier1_result.profanity_detected,
        token_count=evaluation.tier1_result.token_count,
        token_limit_exceeded=evaluation.tier1_result.token_limit_exceeded,
        rouge_score=evaluation.tier1_result.rouge_score,
        bleu_score=evaluation.tier1_result.bleu_score,
        passed=evaluation.tier1_result.passed,
        details=evaluation.tier1_result.details
    )

    tier2 = Tier2Result(
        factual_accuracy=Tier2Dimension(
            score=evaluation.tier2_result.factual_accuracy_score,
            reasoning=evaluation.tier2_result.factual_accuracy_reasoning
        ),
        safety_policy=Tier2Dimension(
            score=evaluation.tier2_result.safety_policy_score,
            reasoning=evaluation.tier2_result.safety_policy_reasoning
        ),
        alignment_helpfulness=Tier2Dimension(
            score=evaluation.tier2_result.alignment_helpfulness_score,
            reasoning=evaluation.tier2_result.alignment_helpfulness_reasoning
        ),
        tone_style=Tier2Dimension(
            score=evaluation.tier2_result.tone_style_score,
            reasoning=evaluation.tier2_result.tone_style_reasoning
        ),
        conciseness=Tier2Dimension(
            score=evaluation.tier2_result.conciseness_score,
            reasoning=evaluation.tier2_result.conciseness_reasoning
        ),
        overall_score=evaluation.tier2_result.overall_score,
        uncertainty_flag=evaluation.tier2_result.uncertainty_flag,
        judge_model=evaluation.tier2_result.judge_model
    )

    calculator = TrustScoreCalculator()
    new_trust_score = calculator.calculate(tier1, tier2, tier3_result)

    # Update trust score
    evaluation.trust_score.overall = new_trust_score.overall
    evaluation.trust_score.tier_3_score = new_trust_score.tier_3_score
    evaluation.trust_score.breakdown = new_trust_score.breakdown

    db_session.commit()

    return {
        "message": "Review submitted successfully",
        "evaluation_id": evaluation_id,
        "new_trust_score": new_trust_score.overall
    }


@app.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    hours: int = 24,
    db_session: Session = Depends(db.get_db)
):
    """
    Get dashboard metrics for monitoring

    Args:
        hours: Hours to look back (default 24)
        db_session: Database session

    Returns:
        DashboardMetrics
    """
    from sqlalchemy import func
    from datetime import timedelta
    from cee_pipeline.database.models import TrustScoreDB, Tier1ResultDB

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    # Total evaluations
    total_evals = db_session.query(func.count(Evaluation.id)).filter(
        Evaluation.created_at >= cutoff_time
    ).scalar() or 0

    # Average trust score
    avg_trust = db_session.query(func.avg(TrustScoreDB.overall)).join(
        Evaluation
    ).filter(
        Evaluation.created_at >= cutoff_time
    ).scalar() or 0

    # Tier 1 pass rate
    tier1_passed = db_session.query(func.count(Tier1ResultDB.id)).join(
        Evaluation
    ).filter(
        Tier1ResultDB.passed == True,
        Evaluation.created_at >= cutoff_time
    ).scalar() or 0
    tier1_pass_rate = (tier1_passed / total_evals * 100) if total_evals > 0 else 0

    # Tier 2 average score
    tier2_avg = db_session.query(func.avg(TrustScoreDB.tier_2_score)).join(
        Evaluation
    ).filter(
        Evaluation.created_at >= cutoff_time
    ).scalar() or 0

    # Tier 3 review count
    tier3_count = db_session.query(func.count(Tier3ResultDB.id)).join(
        Evaluation
    ).filter(
        Evaluation.created_at >= cutoff_time
    ).scalar() or 0

    # Drift index
    drift_index = drift_monitor.calculate_drift_stability_index(
        db=db_session,
        metric_name="trust_score",
        lookback_days=7
    )

    # Recent alerts
    recent_alerts = drift_monitor.get_recent_alerts(db=db_session, hours=hours)

    return DashboardMetrics(
        total_evaluations=total_evals,
        average_trust_score=round(float(avg_trust), 2),
        tier_1_pass_rate=round(tier1_pass_rate, 2),
        tier_2_average_score=round(float(tier2_avg), 2),
        tier_3_review_count=tier3_count,
        current_drift_index=drift_index,
        recent_alerts=recent_alerts
    )


@app.get("/drift/alerts")
async def get_drift_alerts(
    hours: int = 24,
    severity: Optional[str] = None,
    db_session: Session = Depends(db.get_db)
):
    """
    Get recent drift alerts

    Args:
        hours: Hours to look back
        severity: Optional severity filter (warning/critical)
        db_session: Database session

    Returns:
        List of alerts
    """
    alerts = drift_monitor.get_recent_alerts(
        db=db_session,
        hours=hours,
        severity=severity
    )
    return {"alerts": alerts}


@app.post("/drift/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db_session: Session = Depends(db.get_db)
):
    """
    Acknowledge a drift alert

    Args:
        alert_id: Alert ID
        db_session: Database session

    Returns:
        Success message
    """
    drift_monitor.acknowledge_alert(db=db_session, alert_id=alert_id)
    return {"message": "Alert acknowledged"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
