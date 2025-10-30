"""
Basic usage example for CEE Pipeline
Demonstrates evaluation of a single model output
"""
import os
from dotenv import load_dotenv
from cee_pipeline.database.database import db
from cee_pipeline.core.pipeline import CEEPipeline
from cee_pipeline.models.schemas import EvaluationRequest, ModelProvider

# Load environment variables
load_dotenv()

# Initialize database
db.create_tables()


def main():
    """Run a basic evaluation example"""

    # Create evaluation request
    request = EvaluationRequest(
        run_id="example-run-001",
        prompt="Explain what photosynthesis is in simple terms.",
        model_output="Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to create oxygen and energy in the form of sugar. It's how plants make their own food!",
        ground_truth="Photosynthesis is a process used by plants to convert light energy into chemical energy that can be stored and used later. Plants use sunlight, water, and CO2 to produce glucose and oxygen.",
        model_name="gpt-4-turbo-preview",
        model_provider=ModelProvider.OPENAI,
        dataset_name="science-explanations",
        metadata={
            "temperature": 0.7,
            "max_tokens": 150
        }
    )

    # Initialize pipeline
    pipeline = CEEPipeline(
        judge_provider=ModelProvider.OPENAI,
        judge_model="gpt-4-turbo-preview"
    )

    # Run evaluation
    print("Running evaluation...")
    with db.get_session() as session:
        response = pipeline.evaluate(db=session, request=request)

    # Print results
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    print(f"Evaluation ID: {response.evaluation_id}")
    print(f"Status: {response.status}")
    print()

    # Tier 1 Results
    print("TIER 1 - Rule-Based Checks")
    print("-" * 80)
    if response.tier_1_result:
        t1 = response.tier_1_result
        print(f"PII Detected: {t1.pii_detected}")
        print(f"Profanity Detected: {t1.profanity_detected}")
        print(f"Token Count: {t1.token_count}")
        print(f"ROUGE Score: {t1.rouge_score:.4f}" if t1.rouge_score else "ROUGE Score: N/A")
        print(f"BLEU Score: {t1.bleu_score:.4f}" if t1.bleu_score else "BLEU Score: N/A")
        print(f"Passed: {t1.passed}")
    print()

    # Tier 2 Results
    print("TIER 2 - LLM-as-a-Judge")
    print("-" * 80)
    if response.tier_2_result:
        t2 = response.tier_2_result
        print(f"Factual Accuracy: {t2.factual_accuracy.score}/5")
        print(f"  → {t2.factual_accuracy.reasoning}")
        print()
        print(f"Safety & Policy: {t2.safety_policy.score}/5")
        print(f"  → {t2.safety_policy.reasoning}")
        print()
        print(f"Alignment (Helpfulness): {t2.alignment_helpfulness.score}/5")
        print(f"  → {t2.alignment_helpfulness.reasoning}")
        print()
        print(f"Tone & Style: {t2.tone_style.score}/5")
        print(f"  → {t2.tone_style.reasoning}")
        print()
        print(f"Conciseness: {t2.conciseness.score}/5")
        print(f"  → {t2.conciseness.reasoning}")
        print()
        print(f"Overall Score: {t2.overall_score:.2f}/5")
        print(f"Uncertainty Flag: {t2.uncertainty_flag}")
    print()

    # Trust Score
    print("TRUST SCORE")
    print("-" * 80)
    if response.trust_score:
        ts = response.trust_score
        print(f"Overall Trust Score: {ts.overall}/100")
        print(f"Tier 1 Score: {ts.tier_1_score}/100")
        print(f"Tier 2 Score: {ts.tier_2_score}/100")
        if ts.tier_3_score:
            print(f"Tier 3 Score: {ts.tier_3_score}/100")
        print()
        print("Breakdown:")
        for key, value in ts.breakdown.items():
            print(f"  {key}: {value:.2f}")
    print()

    # Tier 3 Status
    if response.status == "needs_human_review":
        print("⚠️  This evaluation has been flagged for human review")
    else:
        print("✓ Evaluation completed successfully")

    print("="*80)


if __name__ == "__main__":
    main()
