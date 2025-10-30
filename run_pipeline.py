#!/usr/bin/env python3
"""
CEE Pipeline - Interactive Runner
Allows users to select models and run evaluations
"""
import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_requirements():
    """Check if all requirements are met"""
    print("Checking requirements...")

    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not openai_key and not anthropic_key:
        print("❌ Error: No API keys found!")
        print("   Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        return False

    if openai_key:
        print("✓ OpenAI API key found")
    if anthropic_key:
        print("✓ Anthropic API key found")

    # Check database
    try:
        from cee_pipeline.database.database import db
        print("✓ Database module loaded")
    except ImportError as e:
        print(f"❌ Error importing database: {e}")
        return False

    return True


def initialize_database():
    """Initialize database tables"""
    print("\nInitializing database...")
    from cee_pipeline.database.database import db

    try:
        db.create_tables()
        print("✓ Database tables created/verified")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False


def select_model():
    """Interactive model selection"""
    from cee_pipeline.models.schemas import ModelProvider

    print("\n" + "="*80)
    print("MODEL SELECTION")
    print("="*80)

    # Determine available providers
    available_providers = []
    if os.getenv("OPENAI_API_KEY"):
        available_providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        available_providers.append("anthropic")

    # Select provider
    if len(available_providers) == 0:
        print("❌ No API keys configured")
        return None, None

    if len(available_providers) == 1:
        provider = available_providers[0]
        print(f"Using provider: {provider}")
    else:
        print("\nAvailable providers:")
        for idx, p in enumerate(available_providers, 1):
            print(f"  {idx}. {p.upper()}")

        while True:
            choice = input("\nSelect provider (1-{}): ".format(len(available_providers)))
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available_providers):
                    provider = available_providers[idx]
                    break
                print("Invalid choice")
            except ValueError:
                print("Please enter a number")

    # Select model
    models = {
        "openai": [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-3.5-turbo"
        ],
        "anthropic": [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    }

    print(f"\nAvailable {provider.upper()} models:")
    model_list = models[provider]
    for idx, model in enumerate(model_list, 1):
        print(f"  {idx}. {model}")

    while True:
        choice = input(f"\nSelect model (1-{len(model_list)}): ")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(model_list):
                model = model_list[idx]
                break
            print("Invalid choice")
        except ValueError:
            print("Please enter a number")

    provider_enum = ModelProvider.OPENAI if provider == "openai" else ModelProvider.ANTHROPIC

    print(f"\n✓ Selected: {provider.upper()} - {model}")

    return provider_enum, model


def get_evaluation_input():
    """Get evaluation input from user"""
    print("\n" + "="*80)
    print("EVALUATION INPUT")
    print("="*80)

    prompt = input("\nEnter prompt: ").strip()
    if not prompt:
        print("❌ Prompt cannot be empty")
        return None

    model_output = input("\nEnter model output to evaluate: ").strip()
    if not model_output:
        print("❌ Model output cannot be empty")
        return None

    ground_truth = input("\nEnter ground truth (optional, press Enter to skip): ").strip()
    ground_truth = ground_truth if ground_truth else None

    run_id = input("\nEnter run ID (default: 'interactive-run'): ").strip()
    run_id = run_id if run_id else "interactive-run"

    return {
        "run_id": run_id,
        "prompt": prompt,
        "model_output": model_output,
        "ground_truth": ground_truth
    }


def run_evaluation(provider, model, eval_input):
    """Run the evaluation"""
    from cee_pipeline.database.database import db
    from cee_pipeline.core.pipeline import CEEPipeline
    from cee_pipeline.models.schemas import EvaluationRequest

    print("\n" + "="*80)
    print("RUNNING EVALUATION")
    print("="*80)

    # Initialize pipeline
    print(f"\nInitializing pipeline with {provider.value} - {model}...")
    pipeline = CEEPipeline(
        judge_provider=provider,
        judge_model=model
    )

    # Create request
    request = EvaluationRequest(
        run_id=eval_input["run_id"],
        prompt=eval_input["prompt"],
        model_output=eval_input["model_output"],
        ground_truth=eval_input["ground_truth"],
        model_name=model,
        model_provider=provider,
        dataset_name="interactive",
        metadata={"source": "interactive"}
    )

    # Run evaluation
    print("Running Tier 1 evaluation...")
    print("Running Tier 2 evaluation (this may take a few seconds)...")
    print("Checking Tier 3 requirements...")

    with db.get_session() as session:
        response = pipeline.evaluate(db=session, request=request)

    # Display results
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)
    print(f"\nEvaluation ID: {response.evaluation_id}")
    print(f"Status: {response.status}")

    # Trust Score
    print("\n" + "-"*80)
    print("TRUST SCORE")
    print("-"*80)
    print(f"Overall: {response.trust_score.overall}/100")
    print(f"Tier 1: {response.trust_score.tier_1_score}/100")
    print(f"Tier 2: {response.trust_score.tier_2_score}/100")
    if response.trust_score.tier_3_score:
        print(f"Tier 3: {response.trust_score.tier_3_score}/100")

    # Tier 1 Results
    print("\n" + "-"*80)
    print("TIER 1 - Rule-Based Checks")
    print("-"*80)
    t1 = response.tier_1_result
    print(f"✓ Passed: {t1.passed}")
    print(f"  PII Detected: {t1.pii_detected}")
    print(f"  Profanity Detected: {t1.profanity_detected}")
    print(f"  Token Count: {t1.token_count}")
    if t1.rouge_score:
        print(f"  ROUGE-L: {t1.rouge_score:.4f}")
    if t1.bleu_score:
        print(f"  BLEU: {t1.bleu_score:.4f}")

    # Tier 2 Results
    print("\n" + "-"*80)
    print("TIER 2 - LLM-as-a-Judge")
    print("-"*80)
    t2 = response.tier_2_result
    print(f"Overall Score: {t2.overall_score:.2f}/5")
    print(f"\nDimension Scores:")
    print(f"  Factual Accuracy: {t2.factual_accuracy.score}/5")
    print(f"    → {t2.factual_accuracy.reasoning}")
    print(f"  Safety & Policy: {t2.safety_policy.score}/5")
    print(f"    → {t2.safety_policy.reasoning}")
    print(f"  Alignment: {t2.alignment_helpfulness.score}/5")
    print(f"    → {t2.alignment_helpfulness.reasoning}")
    print(f"  Tone & Style: {t2.tone_style.score}/5")
    print(f"    → {t2.tone_style.reasoning}")
    print(f"  Conciseness: {t2.conciseness.score}/5")
    print(f"    → {t2.conciseness.reasoning}")

    # Tier 3 Status
    if response.status == "needs_human_review":
        print("\n" + "-"*80)
        print("⚠️  TIER 3 - Human Review Required")
        print("-"*80)
        print("This evaluation has been queued for human review.")

    print("\n" + "="*80)


def main():
    """Main interactive runner"""
    print("="*80)
    print("CEE PIPELINE - Interactive Runner")
    print("Contextual Evaluation Engine for Generative AI")
    print("="*80)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Initialize database
    if not initialize_database():
        sys.exit(1)

    while True:
        print("\n" + "="*80)
        print("MAIN MENU")
        print("="*80)
        print("1. Run single evaluation")
        print("2. Run batch evaluation (from examples)")
        print("3. Start API server")
        print("4. View dashboard metrics")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == "1":
            # Single evaluation
            provider, model = select_model()
            if not provider or not model:
                continue

            eval_input = get_evaluation_input()
            if not eval_input:
                continue

            run_evaluation(provider, model, eval_input)

            input("\nPress Enter to continue...")

        elif choice == "2":
            # Batch evaluation
            print("\nRunning batch evaluation example...")
            try:
                import examples.batch_evaluation as batch
                batch.main()
            except Exception as e:
                print(f"❌ Error: {e}")

            input("\nPress Enter to continue...")

        elif choice == "3":
            # Start API server
            print("\nStarting API server...")
            print("Server will run on http://localhost:8000")
            print("Press Ctrl+C to stop")
            try:
                from cee_pipeline.api.main import app
                import uvicorn
                uvicorn.run(app, host="0.0.0.0", port=8000)
            except KeyboardInterrupt:
                print("\n\n✓ Server stopped")
            except Exception as e:
                print(f"❌ Error: {e}")

            input("\nPress Enter to continue...")

        elif choice == "4":
            # View metrics
            print("\nFetching dashboard metrics...")
            try:
                from cee_pipeline.database.database import db
                from cee_pipeline.core.drift_monitor import DriftMonitor

                monitor = DriftMonitor()
                with db.get_session() as session:
                    metrics = monitor.get_dashboard_metrics(session, hours=24)

                print("\n" + "="*80)
                print("DASHBOARD METRICS (Last 24 hours)")
                print("="*80)
                print(f"Total Evaluations: {metrics['total_evaluations']}")
                print(f"Average Trust Score: {metrics['average_trust_score']}/100")
                print(f"Recent Alerts: {metrics['recent_alerts_count']}")
                print(f"Critical Alerts: {metrics['critical_alerts_count']}")
                print("="*80)
            except Exception as e:
                print(f"❌ Error: {e}")

            input("\nPress Enter to continue...")

        elif choice == "5":
            print("\n✓ Goodbye!")
            sys.exit(0)

        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
