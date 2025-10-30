"""
Pydantic models for data validation and serialization
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class ModelProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class EvaluationStatus(str, Enum):
    """Evaluation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class Tier1Result(BaseModel):
    """Tier 1 evaluation results"""
    pii_detected: bool = False
    profanity_detected: bool = False
    token_count: int
    token_limit_exceeded: bool = False
    rouge_score: Optional[float] = None
    bleu_score: Optional[float] = None
    passed: bool
    details: Dict[str, Any] = Field(default_factory=dict)


class Tier2Dimension(BaseModel):
    """Individual dimension score from LLM-as-a-Judge"""
    score: int = Field(..., ge=1, le=5)
    reasoning: str


class Tier2Result(BaseModel):
    """Tier 2 LLM-as-a-Judge evaluation results"""
    factual_accuracy: Tier2Dimension
    safety_policy: Tier2Dimension
    alignment_helpfulness: Tier2Dimension
    tone_style: Tier2Dimension
    conciseness: Tier2Dimension
    overall_score: float = Field(..., ge=0, le=5)
    uncertainty_flag: bool = False
    judge_model: str


class Tier3Result(BaseModel):
    """Tier 3 human evaluation results"""
    reviewer_id: str
    verdict: str  # "approved", "rejected", "needs_revision"
    notes: str
    corrected_output: Optional[str] = None
    reviewed_at: datetime


class TrustScore(BaseModel):
    """Aggregated Trust Score"""
    overall: float = Field(..., ge=0, le=100)
    tier_1_score: float = Field(..., ge=0, le=100)
    tier_2_score: float = Field(..., ge=0, le=100)
    tier_3_score: Optional[float] = Field(None, ge=0, le=100)
    breakdown: Dict[str, float]


class EvaluationRequest(BaseModel):
    """Request to evaluate a model output"""
    run_id: str
    prompt: str
    model_output: str
    ground_truth: Optional[str] = None
    model_name: str
    model_provider: ModelProvider
    dataset_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationResponse(BaseModel):
    """Response from evaluation pipeline"""
    evaluation_id: str
    run_id: str
    status: EvaluationStatus
    tier_1_result: Optional[Tier1Result] = None
    tier_2_result: Optional[Tier2Result] = None
    tier_3_result: Optional[Tier3Result] = None
    trust_score: Optional[TrustScore] = None
    created_at: datetime
    updated_at: datetime


class HumanReviewRequest(BaseModel):
    """Request for human review"""
    evaluation_id: str
    priority: int = Field(default=1, ge=1, le=5)
    reason: str
    flagged_at: datetime


class DashboardMetrics(BaseModel):
    """Dashboard metrics for monitoring"""
    total_evaluations: int
    average_trust_score: float
    tier_1_pass_rate: float
    tier_2_average_score: float
    tier_3_review_count: int
    current_drift_index: float
    recent_alerts: List[Dict[str, Any]]


class DriftAlert(BaseModel):
    """Drift monitoring alert"""
    alert_id: str
    metric_name: str
    current_value: float
    baseline_value: float
    absolute_change: float
    relative_change: float
    severity: str  # "warning", "critical"
    triggered_at: datetime
    message: str
