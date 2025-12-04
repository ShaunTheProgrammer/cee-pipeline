"""
Main CEE Pipeline Orchestrator
Coordinates all three tiers of evaluation
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from cee_pipeline.core.tier1_evaluator import Tier1Evaluator
from cee_pipeline.core.tier2_evaluator import Tier2Evaluator
from cee_pipeline.core.tier3_evaluator import Tier3Evaluator
from cee_pipeline.core.trust_score import TrustScoreCalculator
from cee_pipeline.core.drift_monitor import DriftMonitor
from cee_pipeline.models.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    EvaluationStatus,
    ModelProvider,
    Tier2Dimension
)
from cee_pipeline.database.models import (
    Evaluation,
    Tier1ResultDB,
    Tier2ResultDB,
    Tier3ResultDB,
    TrustScoreDB,
    HumanReviewQueue
)


class CEEPipeline:
    """
    Main Contextual Evaluation Engine Pipeline
    Orchestrates three-tier evaluation process
    """

    def __init__(
        self,
        judge_provider: ModelProvider = ModelProvider.OPENAI,
        judge_model: str = "gpt-4-turbo-preview",
        token_limit: int = 4096
    ):
        """
        Initialize CEE Pipeline

        Args:
            judge_provider: LLM provider for Tier 2 judging
            judge_model: Specific model for judging
            token_limit: Token limit for Tier 1 checks
        """
        self.tier1_evaluator = Tier1Evaluator(token_limit=token_limit)
        self.tier2_evaluator = Tier2Evaluator(
            judge_provider=judge_provider,
            judge_model=judge_model
        )
        self.tier3_evaluator = Tier3Evaluator()
        self.trust_score_calculator = TrustScoreCalculator()
        self.drift_monitor = DriftMonitor()

    def evaluate(
        self,
        db: Session,
        request: EvaluationRequest
    ) -> EvaluationResponse:
        """
        Run complete evaluation pipeline

        Args:
            db: Database session
            request: Evaluation request

        Returns:
            EvaluationResponse with all results
        """
        # Create evaluation record
        evaluation_id = str(uuid.uuid4())
        evaluation = Evaluation(
            id=evaluation_id,
            run_id=request.run_id,
            prompt=request.prompt,
            model_output=request.model_output,
            ground_truth=request.ground_truth,
            model_name=request.model_name,
            model_provider=request.model_provider.value,
            dataset_name=request.dataset_name,
            extra_metadata=request.metadata,
            status=EvaluationStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()

        try:
            # TIER 1: Rule-based checks
            tier1_result = self.tier1_evaluator.evaluate(
                model_output=request.model_output,
                ground_truth=request.ground_truth
            )

            # Save Tier 1 results
            tier1_db = Tier1ResultDB(
                evaluation_id=evaluation_id,
                pii_detected=tier1_result.pii_detected,
                profanity_detected=tier1_result.profanity_detected,
                token_count=tier1_result.token_count,
                token_limit_exceeded=tier1_result.token_limit_exceeded,
                rouge_score=tier1_result.rouge_score,
                bleu_score=tier1_result.bleu_score,
                passed=tier1_result.passed,
                details=tier1_result.details
            )
            db.add(tier1_db)
            db.commit()

            # TIER 2: LLM-as-a-Judge
            tier2_result = self.tier2_evaluator.evaluate(
                prompt=request.prompt,
                model_output=request.model_output,
                ground_truth=request.ground_truth
            )

            # Save Tier 2 results
            tier2_db = Tier2ResultDB(
                evaluation_id=evaluation_id,
                factual_accuracy_score=tier2_result.factual_accuracy.score,
                factual_accuracy_reasoning=tier2_result.factual_accuracy.reasoning,
                safety_policy_score=tier2_result.safety_policy.score,
                safety_policy_reasoning=tier2_result.safety_policy.reasoning,
                alignment_helpfulness_score=tier2_result.alignment_helpfulness.score,
                alignment_helpfulness_reasoning=tier2_result.alignment_helpfulness.reasoning,
                tone_style_score=tier2_result.tone_style.score,
                tone_style_reasoning=tier2_result.tone_style.reasoning,
                conciseness_score=tier2_result.conciseness.score,
                conciseness_reasoning=tier2_result.conciseness.reasoning,
                overall_score=tier2_result.overall_score,
                uncertainty_flag=tier2_result.uncertainty_flag,
                judge_model=tier2_result.judge_model
            )
            db.add(tier2_db)
            db.commit()

            # TIER 3: Check if human review is needed
            needs_review, reason = self.tier3_evaluator.should_request_review(
                tier_1_passed=tier1_result.passed,
                tier_2_uncertainty=tier2_result.uncertainty_flag,
                tier_2_overall_score=tier2_result.overall_score,
                safety_score=tier2_result.safety_policy.score
            )

            tier3_result = None
            if needs_review:
                # Queue for human review
                self.tier3_evaluator.queue_review(
                    evaluation_id=evaluation_id,
                    reason=reason,
                    priority=5 if not tier1_result.passed else 3
                )

                # Add to database queue
                queue_item = HumanReviewQueue(
                    evaluation_id=evaluation_id,
                    priority=5 if not tier1_result.passed else 3,
                    reason=reason,
                    flagged_at=datetime.utcnow()
                )
                db.add(queue_item)

                evaluation.status = EvaluationStatus.NEEDS_HUMAN_REVIEW
            else:
                evaluation.status = EvaluationStatus.COMPLETED

            # Calculate Trust Score
            trust_score = self.trust_score_calculator.calculate(
                tier1_result=tier1_result,
                tier2_result=tier2_result,
                tier3_result=tier3_result
            )

            # Save Trust Score
            trust_score_db = TrustScoreDB(
                evaluation_id=evaluation_id,
                overall=trust_score.overall,
                tier_1_score=trust_score.tier_1_score,
                tier_2_score=trust_score.tier_2_score,
                tier_3_score=trust_score.tier_3_score,
                breakdown=trust_score.breakdown
            )
            db.add(trust_score_db)

            # Record metrics for drift monitoring
            self.drift_monitor.record_metric(
                db=db,
                metric_name="trust_score",
                metric_value=trust_score.overall,
                model_name=request.model_name,
                dataset_name=request.dataset_name
            )

            # Check for drift
            drift_alert = self.drift_monitor.check_drift(
                db=db,
                metric_name="trust_score",
                current_value=trust_score.overall,
                model_name=request.model_name,
                dataset_name=request.dataset_name
            )

            evaluation.updated_at = datetime.utcnow()
            db.commit()

            # Build response
            response = EvaluationResponse(
                evaluation_id=evaluation_id,
                run_id=request.run_id,
                status=evaluation.status,
                tier_1_result=tier1_result,
                tier_2_result=tier2_result,
                tier_3_result=tier3_result,
                trust_score=trust_score,
                created_at=evaluation.created_at,
                updated_at=evaluation.updated_at
            )

            return response

        except Exception as e:
            evaluation.status = EvaluationStatus.FAILED
            db.commit()
            raise e

    def get_evaluation(self, db: Session, evaluation_id: str) -> Optional[EvaluationResponse]:
        """
        Retrieve evaluation by ID

        Args:
            db: Database session
            evaluation_id: Evaluation ID

        Returns:
            EvaluationResponse or None
        """
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if not evaluation:
            return None

        # Reconstruct response
        tier1_result = None
        if evaluation.tier1_result:
            from cee_pipeline.models.schemas import Tier1Result
            tier1_result = Tier1Result(
                pii_detected=evaluation.tier1_result.pii_detected,
                profanity_detected=evaluation.tier1_result.profanity_detected,
                token_count=evaluation.tier1_result.token_count,
                token_limit_exceeded=evaluation.tier1_result.token_limit_exceeded,
                rouge_score=evaluation.tier1_result.rouge_score,
                bleu_score=evaluation.tier1_result.bleu_score,
                passed=evaluation.tier1_result.passed,
                details=evaluation.tier1_result.details
            )

        tier2_result = None
        if evaluation.tier2_result:
            from cee_pipeline.models.schemas import Tier2Result
            tier2_result = Tier2Result(
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

        tier3_result = None
        if evaluation.tier3_result:
            from cee_pipeline.models.schemas import Tier3Result
            tier3_result = Tier3Result(
                reviewer_id=evaluation.tier3_result.reviewer_id,
                verdict=evaluation.tier3_result.verdict,
                notes=evaluation.tier3_result.notes,
                corrected_output=evaluation.tier3_result.corrected_output,
                reviewed_at=evaluation.tier3_result.reviewed_at
            )

        trust_score = None
        if evaluation.trust_score:
            from cee_pipeline.models.schemas import TrustScore
            trust_score = TrustScore(
                overall=evaluation.trust_score.overall,
                tier_1_score=evaluation.trust_score.tier_1_score,
                tier_2_score=evaluation.trust_score.tier_2_score,
                tier_3_score=evaluation.trust_score.tier_3_score,
                breakdown=evaluation.trust_score.breakdown
            )

        return EvaluationResponse(
            evaluation_id=evaluation.id,
            run_id=evaluation.run_id,
            status=evaluation.status,
            tier_1_result=tier1_result,
            tier_2_result=tier2_result,
            tier_3_result=tier3_result,
            trust_score=trust_score,
            created_at=evaluation.created_at,
            updated_at=evaluation.updated_at
        )
