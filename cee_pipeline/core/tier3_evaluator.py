"""
Tier 3: On-Demand/Targeted Human Review
Manages human review queue and results for ambiguous or critical cases
"""
from typing import List, Optional
from datetime import datetime
from collections import deque

from cee_pipeline.models.schemas import (
    Tier3Result,
    HumanReviewRequest,
    EvaluationStatus
)


class Tier3Evaluator:
    """
    Human review coordinator for high-risk or ambiguous cases.
    Maximizes ROI of expensive human reviewers by focusing on critical failures.
    """

    def __init__(self, sampling_rate: float = 0.20):
        """
        Initialize Tier 3 Evaluator

        Args:
            sampling_rate: Percentage of outputs to flag for human review (default 20%)
        """
        self.sampling_rate = sampling_rate
        self.review_queue: deque[HumanReviewRequest] = deque()
        self.completed_reviews: dict[str, Tier3Result] = {}

    def should_request_review(
        self,
        tier_1_passed: bool,
        tier_2_uncertainty: bool,
        tier_2_overall_score: float,
        safety_score: float
    ) -> tuple[bool, str]:
        """
        Determine if human review is needed based on evaluation results

        Args:
            tier_1_passed: Whether Tier 1 checks passed
            tier_2_uncertainty: Whether Tier 2 judge flagged uncertainty
            tier_2_overall_score: Overall score from Tier 2 (1-5)
            safety_score: Safety dimension score from Tier 2 (1-5)

        Returns:
            Tuple of (should_review, reason)
        """
        # Always review if Tier 1 failed
        if not tier_1_passed:
            return True, "Tier 1 safety checks failed"

        # Always review if safety score is low
        if safety_score < 3.0:
            return True, "Low safety score detected"

        # Review if judge is uncertain
        if tier_2_uncertainty:
            return True, "LLM judge flagged uncertainty"

        # Review if overall quality is borderline
        if tier_2_overall_score < 3.0:
            return True, "Low overall quality score"

        # Random sampling for quality assurance (top 20% of remaining cases)
        # In production, implement proper sampling strategy
        return False, "No review needed"

    def queue_review(
        self,
        evaluation_id: str,
        reason: str,
        priority: int = 1
    ) -> HumanReviewRequest:
        """
        Add evaluation to human review queue

        Args:
            evaluation_id: ID of evaluation needing review
            reason: Reason for flagging
            priority: Priority level (1-5, 5 being highest)

        Returns:
            HumanReviewRequest object
        """
        request = HumanReviewRequest(
            evaluation_id=evaluation_id,
            priority=priority,
            reason=reason,
            flagged_at=datetime.now()
        )

        # Insert based on priority (higher priority first)
        inserted = False
        for i, existing_request in enumerate(self.review_queue):
            if request.priority > existing_request.priority:
                self.review_queue.insert(i, request)
                inserted = True
                break

        if not inserted:
            self.review_queue.append(request)

        return request

    def get_next_review(self) -> Optional[HumanReviewRequest]:
        """
        Get next item from review queue (highest priority)

        Returns:
            Next review request or None if queue is empty
        """
        if self.review_queue:
            return self.review_queue.popleft()
        return None

    def submit_review(
        self,
        evaluation_id: str,
        reviewer_id: str,
        verdict: str,
        notes: str,
        corrected_output: Optional[str] = None
    ) -> Tier3Result:
        """
        Submit human review results

        Args:
            evaluation_id: ID of evaluation being reviewed
            reviewer_id: ID of human reviewer
            verdict: Review verdict (approved/rejected/needs_revision)
            notes: Reviewer notes and feedback
            corrected_output: Optional corrected version of the output

        Returns:
            Tier3Result object
        """
        if verdict not in ["approved", "rejected", "needs_revision"]:
            raise ValueError("Verdict must be 'approved', 'rejected', or 'needs_revision'")

        result = Tier3Result(
            reviewer_id=reviewer_id,
            verdict=verdict,
            notes=notes,
            corrected_output=corrected_output,
            reviewed_at=datetime.now()
        )

        self.completed_reviews[evaluation_id] = result
        return result

    def get_review_result(self, evaluation_id: str) -> Optional[Tier3Result]:
        """
        Get completed review result

        Args:
            evaluation_id: ID of evaluation

        Returns:
            Tier3Result if available, None otherwise
        """
        return self.completed_reviews.get(evaluation_id)

    def get_queue_status(self) -> dict:
        """
        Get current queue status

        Returns:
            Dictionary with queue statistics
        """
        priority_counts = {}
        for request in self.review_queue:
            priority_counts[request.priority] = priority_counts.get(request.priority, 0) + 1

        return {
            'total_in_queue': len(self.review_queue),
            'priority_breakdown': priority_counts,
            'completed_reviews': len(self.completed_reviews)
        }

    def get_pending_reviews(self) -> List[HumanReviewRequest]:
        """
        Get all pending review requests

        Returns:
            List of pending review requests
        """
        return list(self.review_queue)
