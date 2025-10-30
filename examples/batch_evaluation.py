"""
Batch evaluation example
Demonstrates evaluating multiple outputs from a dataset
"""
import os
from dotenv import load_dotenv
from cee_pipeline.database.database import db
from cee_pipeline.core.pipeline import CEEPipeline
from cee_pipeline.models.schemas import EvaluationRequest, ModelProvider

load_dotenv()
db.create_tables()


# Sample dataset
DATASET = [
    {
        "prompt": "What is the capital of France?",
        "model_output": "The capital of France is Paris.",
        "ground_truth": "Paris is the capital of France."
    },
    {
        "prompt": "Explain machine learning in one sentence.",
        "model_output": "Machine learning is when computers learn from data to make decisions without being explicitly programmed.",
        "ground_truth": "Machine learning is a type of artificial intelligence that enables computers to learn and improve from experience without explicit programming."
    },
    {
        "prompt": "What are the benefits of exercise?",
        "model_output": "Exercise improves cardiovascular health, strengthens muscles, boosts mental health, helps with weight management, and increases energy levels.",
        "ground_truth": "Regular exercise benefits physical health (cardiovascular fitness, muscle strength, weight control) and mental health (mood, stress reduction, cognitive function)."
    },
    {
        "prompt": "How does a microwave work?",
        "model_output": "Microwaves work by using electromagnetic radiation to heat food. The microwaves cause water molecules in food to vibrate rapidly, generating heat.",
        "ground_truth": "A microwave oven heats food using microwave radiation, which causes water molecules in the food to vibrate and produce thermal energy."
    }
]


def main():
    """Run batch evaluation"""
    run_id = "batch-run-001"

    # Initialize pipeline
    pipeline = CEEPipeline(
        judge_provider=ModelProvider.OPENAI,
        judge_model="gpt-4-turbo-preview"
    )

    results = []
    total_items = len(DATASET)

    print(f"Starting batch evaluation of {total_items} items...")
    print("="*80)

    for idx, item in enumerate(DATASET, 1):
        print(f"\nEvaluating item {idx}/{total_items}...")

        request = EvaluationRequest(
            run_id=run_id,
            prompt=item["prompt"],
            model_output=item["model_output"],
            ground_truth=item["ground_truth"],
            model_name="gpt-4-turbo-preview",
            model_provider=ModelProvider.OPENAI,
            dataset_name="general-qa",
            metadata={"batch_index": idx}
        )

        with db.get_session() as session:
            response = pipeline.evaluate(db=session, request=request)
            results.append(response)

        print(f"  Trust Score: {response.trust_score.overall}/100")
        print(f"  Status: {response.status}")

    # Summary statistics
    print("\n" + "="*80)
    print("BATCH EVALUATION SUMMARY")
    print("="*80)
    print(f"Total Evaluations: {len(results)}")
    print()

    avg_trust_score = sum(r.trust_score.overall for r in results) / len(results)
    print(f"Average Trust Score: {avg_trust_score:.2f}/100")

    tier1_pass_count = sum(1 for r in results if r.tier_1_result.passed)
    tier1_pass_rate = (tier1_pass_count / len(results)) * 100
    print(f"Tier 1 Pass Rate: {tier1_pass_rate:.1f}%")

    avg_tier2_score = sum(r.tier_2_result.overall_score for r in results) / len(results)
    print(f"Average Tier 2 Score: {avg_tier2_score:.2f}/5")

    needs_review = sum(1 for r in results if r.status == "needs_human_review")
    print(f"Items Needing Human Review: {needs_review}")

    print()
    print("Individual Results:")
    print("-" * 80)
    for idx, result in enumerate(results, 1):
        print(f"{idx}. Trust Score: {result.trust_score.overall}/100 | "
              f"Tier 1: {'✓' if result.tier_1_result.passed else '✗'} | "
              f"Tier 2: {result.tier_2_result.overall_score:.2f}/5 | "
              f"Status: {result.status}")

    print("="*80)


if __name__ == "__main__":
    main()
