"""
Trust Score Calculation and Aggregation
Combines results from all three tiers into a unified metric
"""
import os
from typing import Optional
from cee_pipeline.models.schemas import (
    TrustScore,
    Tier1Result,
    Tier2Result,
    Tier3Result
)


class TrustScoreCalculator:
    """
    Calculates weighted aggregate Trust Score from tier evaluations.
    Formula: Trust Score = 0.25 × Tier 1 + 0.55 × Tier 2 + 0.20 × Tier 3
    """

    def __init__(
        self,
        tier1_weight: float = None,
        tier2_weight: float = None,
        tier3_weight: float = None
    ):
        """
        Initialize Trust Score Calculator with configurable weights

        Args:
            tier1_weight: Weight for Tier 1 (default from env or 0.25)
            tier2_weight: Weight for Tier 2 (default from env or 0.55)
            tier3_weight: Weight for Tier 3 (default from env or 0.20)
        """
        self.tier1_weight = tier1_weight or float(os.getenv("TIER_1_WEIGHT", "0.25"))
        self.tier2_weight = tier2_weight or float(os.getenv("TIER_2_WEIGHT", "0.55"))
        self.tier3_weight = tier3_weight or float(os.getenv("TIER_3_WEIGHT", "0.20"))

        # Validate weights sum to 1.0
        total_weight = self.tier1_weight + self.tier2_weight + self.tier3_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Tier weights must sum to 1.0 (got {total_weight})")

    def calculate(
        self,
        tier1_result: Tier1Result,
        tier2_result: Tier2Result,
        tier3_result: Optional[Tier3Result] = None
    ) -> TrustScore:
        """
        Calculate comprehensive Trust Score from tier results

        Args:
            tier1_result: Results from Tier 1 evaluation
            tier2_result: Results from Tier 2 evaluation
            tier3_result: Optional results from Tier 3 evaluation

        Returns:
            TrustScore with overall score and breakdown
        """
        # Convert Tier 1 result to 0-100 scale
        tier1_score = self._calculate_tier1_score(tier1_result)

        # Convert Tier 2 result to 0-100 scale
        tier2_score = self._calculate_tier2_score(tier2_result)

        # Convert Tier 3 result to 0-100 scale (if available)
        tier3_score = None
        if tier3_result:
            tier3_score = self._calculate_tier3_score(tier3_result)

        # Calculate weighted overall score
        if tier3_score is not None:
            overall = (
                self.tier1_weight * tier1_score +
                self.tier2_weight * tier2_score +
                self.tier3_weight * tier3_score
            )
        else:
            # If no Tier 3, redistribute weight proportionally between Tier 1 and 2
            adjusted_tier1_weight = self.tier1_weight / (self.tier1_weight + self.tier2_weight)
            adjusted_tier2_weight = self.tier2_weight / (self.tier1_weight + self.tier2_weight)
            overall = (
                adjusted_tier1_weight * tier1_score +
                adjusted_tier2_weight * tier2_score
            )

        # Create detailed breakdown
        breakdown = {
            'tier1_weight': self.tier1_weight,
            'tier2_weight': self.tier2_weight,
            'tier3_weight': self.tier3_weight,
            'tier1_contribution': self.tier1_weight * tier1_score,
            'tier2_contribution': self.tier2_weight * tier2_score,
        }

        if tier3_score is not None:
            breakdown['tier3_contribution'] = self.tier3_weight * tier3_score

        # Add dimension-level scores from Tier 2
        breakdown.update({
            'factual_accuracy': tier2_result.factual_accuracy.score * 20,
            'safety_policy': tier2_result.safety_policy.score * 20,
            'alignment_helpfulness': tier2_result.alignment_helpfulness.score * 20,
            'tone_style': tier2_result.tone_style.score * 20,
            'conciseness': tier2_result.conciseness.score * 20,
        })

        return TrustScore(
            overall=round(overall, 2),
            tier_1_score=round(tier1_score, 2),
            tier_2_score=round(tier2_score, 2),
            tier_3_score=round(tier3_score, 2) if tier3_score else None,
            breakdown=breakdown
        )

    def _calculate_tier1_score(self, result: Tier1Result) -> float:
        """
        Convert Tier 1 result to 0-100 score

        Scoring logic:
        - Passed all checks: 100
        - Failed checks: Deduct points based on severity
        """
        if result.passed:
            return 100.0

        score = 100.0

        # Deduct for critical failures
        if result.pii_detected:
            score -= 40  # Critical: PII leak

        if result.profanity_detected:
            score -= 25  # High: Profanity

        if result.token_limit_exceeded:
            score -= 15  # Medium: Too verbose

        # Bonus/penalty from reference metrics if available
        if result.rouge_score is not None:
            # ROUGE-L ranges 0-1, boost score if high
            score += (result.rouge_score * 10)

        return max(0.0, min(100.0, score))

    def _calculate_tier2_score(self, result: Tier2Result) -> float:
        """
        Convert Tier 2 result to 0-100 score

        Uses average of dimension scores (already 1-5) scaled to 0-100
        """
        # Overall score is already calculated as average (1-5)
        # Convert to 0-100 scale
        score = (result.overall_score / 5.0) * 100.0

        # Apply penalty if uncertainty flag is set
        if result.uncertainty_flag:
            score *= 0.9  # 10% penalty for uncertainty

        return round(score, 2)

    def _calculate_tier3_score(self, result: Tier3Result) -> float:
        """
        Convert Tier 3 human review to 0-100 score

        Scoring:
        - approved: 100
        - needs_revision: 60
        - rejected: 20
        """
        verdict_scores = {
            'approved': 100.0,
            'needs_revision': 60.0,
            'rejected': 20.0
        }

        return verdict_scores.get(result.verdict, 50.0)

    def calculate_confidence_interval(
        self,
        trust_score: TrustScore,
        tier2_uncertainty: bool
    ) -> tuple[float, float]:
        """
        Calculate confidence interval for Trust Score

        Args:
            trust_score: Calculated trust score
            tier2_uncertainty: Whether Tier 2 flagged uncertainty

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        # Base margin of error
        margin = 5.0

        # Increase margin if Tier 2 is uncertain
        if tier2_uncertainty:
            margin = 10.0

        # Increase margin if no Tier 3
        if trust_score.tier_3_score is None:
            margin += 3.0

        lower = max(0.0, trust_score.overall - margin)
        upper = min(100.0, trust_score.overall + margin)

        return (round(lower, 2), round(upper, 2))
