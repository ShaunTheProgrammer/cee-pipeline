"""
Tier 1: Continuous/Low-Latency Rule-based Evaluation
Performs instant checks for PII, profanity, token limits, and reference metrics
"""
import re
from typing import Optional, List
from rouge_score import rouge_scorer
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

from cee_pipeline.models.schemas import Tier1Result


class Tier1Evaluator:
    """
    Rule-based evaluator for immediate quality and safety checks.
    Designed for CI/CD pipeline integration with low latency.
    """

    # Common PII patterns (simplified - use proper PII detection library in production)
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    }

    # Common profanity list (simplified - use comprehensive library in production)
    PROFANITY_LIST = {
        'damn', 'hell', 'crap', 'fuck', 'shit', 'ass', 'bitch',
        'bastard', 'dick', 'piss', 'pussy', 'cock', 'asshole'
    }

    def __init__(self, token_limit: int = 4096):
        """
        Initialize Tier 1 Evaluator

        Args:
            token_limit: Maximum allowed tokens in output
        """
        self.token_limit = token_limit
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

        # Download NLTK data if not present
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

    def evaluate(
        self,
        model_output: str,
        ground_truth: Optional[str] = None
    ) -> Tier1Result:
        """
        Perform comprehensive Tier 1 evaluation

        Args:
            model_output: The generated text to evaluate
            ground_truth: Optional reference text for metric calculation

        Returns:
            Tier1Result with all check results
        """
        # PII Detection
        pii_detected = self._check_pii(model_output)

        # Profanity Detection
        profanity_detected = self._check_profanity(model_output)

        # Token counting (simplified - use proper tokenizer in production)
        token_count = self._count_tokens(model_output)
        token_limit_exceeded = token_count > self.token_limit

        # Reference metrics (if ground truth available)
        rouge_score = None
        bleu_score = None
        if ground_truth:
            rouge_score = self._calculate_rouge(model_output, ground_truth)
            bleu_score = self._calculate_bleu(model_output, ground_truth)

        # Determine if output passed all checks
        passed = not (pii_detected or profanity_detected or token_limit_exceeded)

        details = {
            'pii_types_found': self._get_pii_types(model_output) if pii_detected else [],
            'profanity_words_found': self._get_profanity_words(model_output) if profanity_detected else [],
            'token_limit': self.token_limit,
        }

        return Tier1Result(
            pii_detected=pii_detected,
            profanity_detected=profanity_detected,
            token_count=token_count,
            token_limit_exceeded=token_limit_exceeded,
            rouge_score=rouge_score,
            bleu_score=bleu_score,
            passed=passed,
            details=details
        )

    def _check_pii(self, text: str) -> bool:
        """Check if text contains PII"""
        for pattern in self.PII_PATTERNS.values():
            if re.search(pattern, text):
                return True
        return False

    def _get_pii_types(self, text: str) -> List[str]:
        """Get types of PII found in text"""
        found_types = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, text):
                found_types.append(pii_type)
        return found_types

    def _check_profanity(self, text: str) -> bool:
        """Check if text contains profanity"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        return any(word in self.PROFANITY_LIST for word in words)

    def _get_profanity_words(self, text: str) -> List[str]:
        """Get profanity words found in text"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        return [word for word in words if word in self.PROFANITY_LIST]

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens (simplified word-based count)
        In production, use proper tokenizer for your model
        """
        return len(text.split())

    def _calculate_rouge(self, candidate: str, reference: str) -> float:
        """Calculate ROUGE-L F1 score"""
        scores = self.rouge_scorer.score(reference, candidate)
        return scores['rougeL'].fmeasure

    def _calculate_bleu(self, candidate: str, reference: str) -> float:
        """Calculate BLEU score"""
        reference_tokens = [nltk.word_tokenize(reference.lower())]
        candidate_tokens = nltk.word_tokenize(candidate.lower())

        # Use smoothing to handle edge cases
        smoothing = SmoothingFunction().method1
        return sentence_bleu(reference_tokens, candidate_tokens, smoothing_function=smoothing)
