"""
SQLAlchemy database models for persistence
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, JSON, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class EvaluationStatusEnum(str, enum.Enum):
    """Evaluation status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class Evaluation(Base):
    """Main evaluation record"""
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True)
    run_id = Column(String, nullable=False, index=True)

    # Input data
    prompt = Column(Text, nullable=False)
    model_output = Column(Text, nullable=False)
    ground_truth = Column(Text, nullable=True)
    model_name = Column(String, nullable=False)
    model_provider = Column(String, nullable=False)
    dataset_name = Column(String, nullable=True)
    metadata = Column(JSON, default={})

    # Status
    status = Column(SQLEnum(EvaluationStatusEnum), default=EvaluationStatusEnum.PENDING)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tier1_result = relationship("Tier1ResultDB", back_populates="evaluation", uselist=False)
    tier2_result = relationship("Tier2ResultDB", back_populates="evaluation", uselist=False)
    tier3_result = relationship("Tier3ResultDB", back_populates="evaluation", uselist=False)
    trust_score = relationship("TrustScoreDB", back_populates="evaluation", uselist=False)


class Tier1ResultDB(Base):
    """Tier 1 evaluation results"""
    __tablename__ = "tier1_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)

    pii_detected = Column(Boolean, default=False)
    profanity_detected = Column(Boolean, default=False)
    token_count = Column(Integer, nullable=False)
    token_limit_exceeded = Column(Boolean, default=False)
    rouge_score = Column(Float, nullable=True)
    bleu_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=False)
    details = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    evaluation = relationship("Evaluation", back_populates="tier1_result")


class Tier2ResultDB(Base):
    """Tier 2 LLM-as-a-Judge evaluation results"""
    __tablename__ = "tier2_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)

    # Dimension scores
    factual_accuracy_score = Column(Integer, nullable=False)
    factual_accuracy_reasoning = Column(Text, nullable=False)

    safety_policy_score = Column(Integer, nullable=False)
    safety_policy_reasoning = Column(Text, nullable=False)

    alignment_helpfulness_score = Column(Integer, nullable=False)
    alignment_helpfulness_reasoning = Column(Text, nullable=False)

    tone_style_score = Column(Integer, nullable=False)
    tone_style_reasoning = Column(Text, nullable=False)

    conciseness_score = Column(Integer, nullable=False)
    conciseness_reasoning = Column(Text, nullable=False)

    overall_score = Column(Float, nullable=False)
    uncertainty_flag = Column(Boolean, default=False)
    judge_model = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    evaluation = relationship("Evaluation", back_populates="tier2_result")


class Tier3ResultDB(Base):
    """Tier 3 human review results"""
    __tablename__ = "tier3_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)

    reviewer_id = Column(String, nullable=False)
    verdict = Column(String, nullable=False)  # approved, rejected, needs_revision
    notes = Column(Text, nullable=False)
    corrected_output = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    evaluation = relationship("Evaluation", back_populates="tier3_result")


class TrustScoreDB(Base):
    """Trust Score results"""
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)

    overall = Column(Float, nullable=False)
    tier_1_score = Column(Float, nullable=False)
    tier_2_score = Column(Float, nullable=False)
    tier_3_score = Column(Float, nullable=True)
    breakdown = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    evaluation = relationship("Evaluation", back_populates="trust_score")


class HumanReviewQueue(Base):
    """Queue for human review requests"""
    __tablename__ = "human_review_queue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)

    priority = Column(Integer, default=1)
    reason = Column(Text, nullable=False)
    flagged_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)


class DriftMetric(Base):
    """Drift monitoring metrics"""
    __tablename__ = "drift_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)

    metric_name = Column(String, nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=True)

    model_name = Column(String, nullable=True)
    dataset_name = Column(String, nullable=True)

    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)


class DriftAlertDB(Base):
    """Drift monitoring alerts"""
    __tablename__ = "drift_alerts"

    id = Column(String, primary_key=True)

    metric_name = Column(String, nullable=False, index=True)
    current_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=False)
    absolute_change = Column(Float, nullable=False)
    relative_change = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # warning, critical
    message = Column(Text, nullable=False)

    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
