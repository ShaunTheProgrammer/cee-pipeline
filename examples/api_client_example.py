"""
API client example
Demonstrates using the CEE API endpoints
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"


def create_evaluation():
    """Create a new evaluation via API"""
    print("Creating evaluation...")

    payload = {
        "run_id": "api-test-001",
        "prompt": "What is quantum computing?",
        "model_output": "Quantum computing uses quantum mechanics principles like superposition and entanglement to process information. Unlike classical computers that use bits (0 or 1), quantum computers use qubits that can be both 0 and 1 simultaneously, enabling parallel processing of vast amounts of data.",
        "ground_truth": "Quantum computing is a type of computation that harnesses quantum mechanical phenomena like superposition and entanglement to process information in fundamentally different ways than classical computers.",
        "model_name": "gpt-4-turbo-preview",
        "model_provider": "openai",
        "dataset_name": "tech-qa",
        "metadata": {
            "source": "api_example"
        }
    }

    response = requests.post(f"{API_BASE_URL}/evaluate", json=payload)
    response.raise_for_status()

    result = response.json()
    print(f"✓ Evaluation created: {result['evaluation_id']}")
    print(f"  Trust Score: {result['trust_score']['overall']}/100")
    print(f"  Status: {result['status']}")

    return result['evaluation_id']


def get_evaluation(evaluation_id):
    """Retrieve evaluation by ID"""
    print(f"\nRetrieving evaluation {evaluation_id}...")

    response = requests.get(f"{API_BASE_URL}/evaluations/{evaluation_id}")
    response.raise_for_status()

    result = response.json()
    print(f"✓ Retrieved evaluation")
    print(f"  Trust Score: {result['trust_score']['overall']}/100")
    print(f"  Tier 1 Passed: {result['tier_1_result']['passed']}")
    print(f"  Tier 2 Overall: {result['tier_2_result']['overall_score']}/5")

    return result


def get_dashboard_metrics():
    """Get dashboard metrics"""
    print("\nFetching dashboard metrics...")

    response = requests.get(f"{API_BASE_URL}/dashboard/metrics?hours=24")
    response.raise_for_status()

    metrics = response.json()
    print("✓ Dashboard Metrics:")
    print(f"  Total Evaluations: {metrics['total_evaluations']}")
    print(f"  Average Trust Score: {metrics['average_trust_score']}/100")
    print(f"  Tier 1 Pass Rate: {metrics['tier_1_pass_rate']}%")
    print(f"  Tier 2 Avg Score: {metrics['tier_2_average_score']}/100")
    print(f"  Tier 3 Review Count: {metrics['tier_3_review_count']}")
    print(f"  Drift Stability Index: {metrics['current_drift_index']}/100")

    return metrics


def get_review_queue():
    """Get items in review queue"""
    print("\nFetching review queue...")

    response = requests.get(f"{API_BASE_URL}/review/queue")
    response.raise_for_status()

    queue = response.json()
    print(f"✓ Items in review queue: {len(queue)}")

    if queue:
        for item in queue[:5]:  # Show first 5
            print(f"  - {item['evaluation_id']}: {item['reason']} (Priority: {item['priority']})")

    return queue


def submit_review(evaluation_id):
    """Submit human review for an evaluation"""
    print(f"\nSubmitting review for {evaluation_id}...")

    payload = {
        "reviewer_id": "human_reviewer_001",
        "verdict": "approved",
        "notes": "Output is accurate and well-structured. No issues found.",
        "corrected_output": None
    }

    response = requests.post(
        f"{API_BASE_URL}/review/{evaluation_id}/submit",
        params=payload
    )
    response.raise_for_status()

    result = response.json()
    print(f"✓ Review submitted")
    print(f"  New Trust Score: {result['new_trust_score']}/100")

    return result


def get_drift_alerts():
    """Get drift alerts"""
    print("\nFetching drift alerts...")

    response = requests.get(f"{API_BASE_URL}/drift/alerts?hours=24")
    response.raise_for_status()

    data = response.json()
    alerts = data.get('alerts', [])

    print(f"✓ Active alerts: {len(alerts)}")

    if alerts:
        for alert in alerts:
            print(f"  [{alert['severity'].upper()}] {alert['metric_name']}")
            print(f"    {alert['message']}")

    return alerts


def main():
    """Run API client examples"""
    print("="*80)
    print("CEE API Client Example")
    print("="*80)

    try:
        # Create evaluation
        eval_id = create_evaluation()

        # Wait a moment
        time.sleep(1)

        # Retrieve evaluation
        evaluation = get_evaluation(eval_id)

        # Get dashboard metrics
        metrics = get_dashboard_metrics()

        # Get review queue
        queue = get_review_queue()

        # Get drift alerts
        alerts = get_drift_alerts()

        print("\n" + "="*80)
        print("✓ All API operations completed successfully!")
        print("="*80)

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server")
        print("  Make sure the API server is running on http://localhost:8000")
        print("  Start it with: python -m cee_pipeline.api.main")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    main()
