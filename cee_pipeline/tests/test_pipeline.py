"""
Basic tests for CEE Pipeline
Run with: pytest cee_pipeline/tests/test_pipeline.py
"""
import pytest
from cee_pipeline.core.tier1_evaluator import Tier1Evaluator
from cee_pipeline.core.trust_score import TrustScoreCalculator
from cee_pipeline.models.schemas import (
    Tier1Result, Tier2Result, Tier2Dimension
)


class TestTier1Evaluator:
    """Tests for Tier 1 rule-based evaluator"""

    def test_pii_detection_email(self):
        """Test that email addresses are detected"""
        evaluator = Tier1Evaluator()
        result = evaluator.evaluate("Contact me at test@example.com")

        assert result.pii_detected is True
        assert 'email' in result.details['pii_types_found']

    def test_pii_detection_clean(self):
        """Test that clean text passes"""
        evaluator = Tier1Evaluator()
        result = evaluator.evaluate("This is a clean response without any PII")

        assert result.pii_detected is False

    def test_profanity_detection(self):
        """Test profanity detection"""
        evaluator = Tier1Evaluator()
        result = evaluator.evaluate("This is a damn bad response")

        assert result.profanity_detected is True

    def test_profanity_clean(self):
        """Test clean language passes"""
        evaluator = Tier1Evaluator()
        result = evaluator.evaluate("This is a good response")

        assert result.profanity_detected is False

    def test_token_count(self):
        """Test token counting"""
        evaluator = Tier1Evaluator(token_limit=10)
        result = evaluator.evaluate("This is a test sentence")

        assert result.token_count == 5
        assert result.token_limit_exceeded is False

    def test_token_limit_exceeded(self):
        """Test token limit exceeded"""
        evaluator = Tier1Evaluator(token_limit=3)
        result = evaluator.evaluate("This is a longer test sentence")

        assert result.token_count == 6
        assert result.token_limit_exceeded is True

    def test_rouge_score(self):
        """Test ROUGE score calculation"""
        evaluator = Tier1Evaluator()
        result = evaluator.evaluate(
            model_output="The cat sat on the mat",
            ground_truth="The cat sat on the mat"
        )

        assert result.rouge_score is not None
        assert result.rouge_score > 0.9  # Should be very high for identical text

    def test_passed_all_checks(self):
        """Test output that passes all checks"""
        evaluator = Tier1Evaluator()
        result = evaluator.evaluate("This is a clean, short response")

        assert result.passed is True


class TestTrustScoreCalculator:
    """Tests for Trust Score calculation"""

    def test_basic_calculation(self):
        """Test basic trust score calculation"""
        calculator = TrustScoreCalculator()

        tier1 = Tier1Result(
            pii_detected=False,
            profanity_detected=False,
            token_count=50,
            token_limit_exceeded=False,
            passed=True,
            details={}
        )

        tier2 = Tier2Result(
            factual_accuracy=Tier2Dimension(score=5, reasoning="Perfect"),
            safety_policy=Tier2Dimension(score=5, reasoning="Safe"),
            alignment_helpfulness=Tier2Dimension(score=5, reasoning="Helpful"),
            tone_style=Tier2Dimension(score=5, reasoning="Professional"),
            conciseness=Tier2Dimension(score=5, reasoning="Concise"),
            overall_score=5.0,
            uncertainty_flag=False,
            judge_model="gpt-4"
        )

        score = calculator.calculate(tier1, tier2)

        assert score.overall >= 90  # Should be high for perfect scores
        assert score.tier_1_score == 100
        assert score.tier_2_score == 100

    def test_with_tier3(self):
        """Test trust score with Tier 3 included"""
        calculator = TrustScoreCalculator()

        tier1 = Tier1Result(
            pii_detected=False,
            profanity_detected=False,
            token_count=50,
            token_limit_exceeded=False,
            passed=True,
            details={}
        )

        tier2 = Tier2Result(
            factual_accuracy=Tier2Dimension(score=4, reasoning="Good"),
            safety_policy=Tier2Dimension(score=5, reasoning="Safe"),
            alignment_helpfulness=Tier2Dimension(score=4, reasoning="Helpful"),
            tone_style=Tier2Dimension(score=4, reasoning="Professional"),
            conciseness=Tier2Dimension(score=4, reasoning="Concise"),
            overall_score=4.2,
            uncertainty_flag=False,
            judge_model="gpt-4"
        )

        from cee_pipeline.models.schemas import Tier3Result
        from datetime import datetime

        tier3 = Tier3Result(
            reviewer_id="test_reviewer",
            verdict="approved",
            notes="Looks good",
            reviewed_at=datetime.now()
        )

        score = calculator.calculate(tier1, tier2, tier3)

        assert score.tier_3_score == 100  # Approved
        assert score.overall > 80  # Should be high overall

    def test_failed_tier1(self):
        """Test score when Tier 1 fails"""
        calculator = TrustScoreCalculator()

        tier1 = Tier1Result(
            pii_detected=True,
            profanity_detected=False,
            token_count=50,
            token_limit_exceeded=False,
            passed=False,
            details={'pii_types_found': ['email']}
        )

        tier2 = Tier2Result(
            factual_accuracy=Tier2Dimension(score=5, reasoning="Perfect"),
            safety_policy=Tier2Dimension(score=5, reasoning="Safe"),
            alignment_helpfulness=Tier2Dimension(score=5, reasoning="Helpful"),
            tone_style=Tier2Dimension(score=5, reasoning="Professional"),
            conciseness=Tier2Dimension(score=5, reasoning="Concise"),
            overall_score=5.0,
            uncertainty_flag=False,
            judge_model="gpt-4"
        )

        score = calculator.calculate(tier1, tier2)

        assert score.tier_1_score < 100  # Should be penalized for PII
        assert score.overall < 100  # Overall should be affected

    def test_uncertainty_penalty(self):
        """Test penalty for uncertainty flag"""
        calculator = TrustScoreCalculator()

        tier1 = Tier1Result(
            pii_detected=False,
            profanity_detected=False,
            token_count=50,
            token_limit_exceeded=False,
            passed=True,
            details={}
        )

        tier2_certain = Tier2Result(
            factual_accuracy=Tier2Dimension(score=4, reasoning="Good"),
            safety_policy=Tier2Dimension(score=4, reasoning="Safe"),
            alignment_helpfulness=Tier2Dimension(score=4, reasoning="Helpful"),
            tone_style=Tier2Dimension(score=4, reasoning="Professional"),
            conciseness=Tier2Dimension(score=4, reasoning="Concise"),
            overall_score=4.0,
            uncertainty_flag=False,
            judge_model="gpt-4"
        )

        tier2_uncertain = Tier2Result(
            factual_accuracy=Tier2Dimension(score=4, reasoning="Good"),
            safety_policy=Tier2Dimension(score=4, reasoning="Safe"),
            alignment_helpfulness=Tier2Dimension(score=4, reasoning="Helpful"),
            tone_style=Tier2Dimension(score=4, reasoning="Professional"),
            conciseness=Tier2Dimension(score=4, reasoning="Concise"),
            overall_score=4.0,
            uncertainty_flag=True,
            judge_model="gpt-4"
        )

        score_certain = calculator.calculate(tier1, tier2_certain)
        score_uncertain = calculator.calculate(tier1, tier2_uncertain)

        assert score_uncertain.tier_2_score < score_certain.tier_2_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
