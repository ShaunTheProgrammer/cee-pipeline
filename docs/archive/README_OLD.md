# Contextual Evaluation Engine (CEE) Pipeline

A comprehensive, three-tier evaluation system for Generative AI models that provides continuous monitoring, qualitative assessment, and targeted human review.

![CEE Architecture](https://via.placeholder.com/800x400?text=CEE+Pipeline+Architecture)

## Overview

The CEE Pipeline implements a tiered evaluation approach that balances speed, cost, and accuracy:

- **Tier 1**: Continuous/Low-Latency rule-based checks (PII, profanity, token limits, ROUGE/BLEU metrics)
- **Tier 2**: Scheduled/Scaling LLM-as-a-Judge evaluation across 5 quality dimensions
- **Tier 3**: On-Demand/Targeted human review for critical or ambiguous cases

### Trust Score

All evaluations are aggregated into a single Trust Score (0-100) using weighted contributions:

```
Trust Score = 0.25 × Tier 1 + 0.55 × Tier 2 + 0.20 × Tier 3
```

## Features

✨ **Three-Tier Evaluation**
- Automated rule-based safety checks
- AI-powered qualitative assessment
- Intelligent human review queueing

📊 **Comprehensive Metrics**
- Trust Score calculation
- Dimension-level scoring (Accuracy, Safety, Alignment, Tone, Conciseness)
- Reference metric comparison (ROUGE, BLEU)

🔍 **Drift Monitoring**
- Real-time performance tracking
- Baseline comparison
- Automated alerting system
- Drift Stability Index (DSI)

🎯 **Smart Review Queue**
- Priority-based human review
- Automatic flagging of high-risk outputs
- 20% sampling for quality assurance

📈 **Interactive Dashboard**
- Real-time metrics visualization
- Trend analysis
- Alert management

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key (for Tier 2 LLM-as-Judge)
- Or Anthropic API key (alternative judge)

### Setup

1. **Clone and navigate to the project**:
```bash
cd /Users/shaundeshpande/Documents/pmpproj1
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Initialize database**:
```bash
python -c "from cee_pipeline.database.database import db; db.create_tables()"
```

## Quick Start

### 1. Basic Evaluation

```python
from cee_pipeline.database.database import db
from cee_pipeline.core.pipeline import CEEPipeline
from cee_pipeline.models.schemas import EvaluationRequest, ModelProvider

# Initialize
db.create_tables()
pipeline = CEEPipeline(
    judge_provider=ModelProvider.OPENAI,
    judge_model="gpt-4-turbo-preview"
)

# Create evaluation request
request = EvaluationRequest(
    run_id="my-run-001",
    prompt="What is machine learning?",
    model_output="Machine learning is AI that learns from data...",
    ground_truth="Machine learning is a subset of AI...",
    model_name="gpt-4",
    model_provider=ModelProvider.OPENAI
)

# Run evaluation
with db.get_session() as session:
    response = pipeline.evaluate(db=session, request=request)

print(f"Trust Score: {response.trust_score.overall}/100")
```

### 2. Start API Server

```bash
python -m cee_pipeline.api.main
```

The API will be available at `http://localhost:8000`

### 3. Open Dashboard

Open `cee_pipeline/dashboard/dashboard.html` in your browser or serve it:

```bash
python -m http.server 8080 --directory cee_pipeline/dashboard
```

Navigate to `http://localhost:8080/dashboard.html`

## Usage Examples

### Model Selection

The CEE Pipeline supports multiple LLM providers for the judge (Tier 2):

#### Using OpenAI
```python
pipeline = CEEPipeline(
    judge_provider=ModelProvider.OPENAI,
    judge_model="gpt-4-turbo-preview"  # or "gpt-3.5-turbo"
)
```

#### Using Anthropic
```python
pipeline = CEEPipeline(
    judge_provider=ModelProvider.ANTHROPIC,
    judge_model="claude-3-opus-20240229"  # or other Claude models
)
```

### Batch Evaluation

```python
# See examples/batch_evaluation.py for complete example
for item in dataset:
    request = EvaluationRequest(
        run_id="batch-001",
        prompt=item["prompt"],
        model_output=item["output"],
        ground_truth=item["reference"],
        model_name="your-model",
        model_provider=ModelProvider.OPENAI
    )

    with db.get_session() as session:
        response = pipeline.evaluate(db=session, request=request)
```

### API Usage

```python
import requests

# Create evaluation
response = requests.post("http://localhost:8000/evaluate", json={
    "run_id": "api-test",
    "prompt": "Explain photosynthesis",
    "model_output": "Photosynthesis is...",
    "model_name": "gpt-4",
    "model_provider": "openai"
})

result = response.json()
print(f"Evaluation ID: {result['evaluation_id']}")
print(f"Trust Score: {result['trust_score']['overall']}")
```

## API Endpoints

### Evaluation Endpoints

- `POST /evaluate` - Create and run evaluation
- `GET /evaluations/{id}` - Get evaluation by ID
- `GET /evaluations/run/{run_id}` - Get all evaluations for a run

### Human Review Endpoints

- `GET /review/queue` - Get pending review items
- `POST /review/{id}/submit` - Submit human review

### Monitoring Endpoints

- `GET /dashboard/metrics` - Get dashboard metrics
- `GET /drift/alerts` - Get drift alerts
- `POST /drift/alerts/{id}/acknowledge` - Acknowledge alert

See full API documentation at `http://localhost:8000/docs`

## Architecture

### Tier 1: Rule-Based Evaluation

**Purpose**: Instant safety and quality checks for CI/CD integration

**Checks**:
- PII detection (email, SSN, phone, credit card)
- Profanity filtering
- Token limit validation
- Reference metrics (ROUGE, BLEU)

**Output**: Pass/fail status with detailed breakdown

### Tier 2: LLM-as-a-Judge

**Purpose**: Scalable qualitative assessment without human cost

**Dimensions** (scored 1-5):
1. **Factual Accuracy** - Correctness, hallucination detection
2. **Safety & Policy** - Policy violations, harmful content
3. **Alignment (Helpfulness)** - Intent understanding, task completion
4. **Tone & Style** - Brand consistency, professionalism
5. **Conciseness** - Optimal length, efficiency

**Output**: Dimension scores + reasoning + uncertainty flag

### Tier 3: Human Review

**Purpose**: Targeted expert review for high-risk cases

**Triggered When**:
- Tier 1 checks fail
- Safety score < 3.0
- LLM judge flags uncertainty
- Overall quality score < 3.0
- Random 20% sampling

**Output**: Verdict (approved/rejected/needs_revision) + notes

### Trust Score Calculation

```python
# Base calculation
Trust Score = (
    0.25 × Tier_1_Score +
    0.55 × Tier_2_Score +
    0.20 × Tier_3_Score
)

# Tier 1 Score (0-100)
- 100 if all checks pass
- Deductions for violations (PII: -40, Profanity: -25, etc.)
- Bonuses for high reference metrics

# Tier 2 Score (0-100)
- Average of 5 dimensions scaled from 1-5 to 0-100
- 10% penalty if uncertainty flagged

# Tier 3 Score (0-100)
- Approved: 100
- Needs Revision: 60
- Rejected: 20
```

## Drift Monitoring

The CEE Pipeline includes comprehensive drift monitoring:

### Metrics Tracked
- Trust Score trends
- Tier 1 pass rates
- Tier 2 dimension scores
- Review queue depth

### Drift Stability Index (DSI)

Measures consistency over time (0-100, higher = more stable):

```python
DSI = 100 × e^(-coefficient_of_variation)
```

### Alerting

Alerts trigger when metrics exceed thresholds:
- **Warning**: Absolute change > 5 or Relative change > 10%
- **Critical**: Absolute change > 10 or Relative change > 20%

## Configuration

Edit `.env` file:

```bash
# LLM API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///./cee_pipeline.db

# Trust Score Weights
TIER_1_WEIGHT=0.25
TIER_2_WEIGHT=0.55
TIER_3_WEIGHT=0.20

# Drift Monitoring
DRIFT_THRESHOLD_ABSOLUTE=5.0
DRIFT_THRESHOLD_RELATIVE=0.10

# Human Review
TIER_3_SAMPLING_RATE=0.20
```

## Project Structure

```
pmpproj1/
├── cee_pipeline/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── core/
│   │   ├── tier1_evaluator.py   # Rule-based checks
│   │   ├── tier2_evaluator.py   # LLM-as-a-Judge
│   │   ├── tier3_evaluator.py   # Human review manager
│   │   ├── trust_score.py       # Trust score calculation
│   │   ├── drift_monitor.py     # Drift monitoring
│   │   └── pipeline.py          # Main orchestrator
│   ├── database/
│   │   ├── models.py            # SQLAlchemy models
│   │   └── database.py          # DB connection
│   ├── dashboard/
│   │   └── dashboard.html       # Interactive dashboard
│   └── models/
│       └── schemas.py           # Pydantic schemas
├── examples/
│   ├── basic_usage.py           # Basic example
│   ├── batch_evaluation.py      # Batch processing
│   └── api_client_example.py    # API usage
├── requirements.txt
├── .env.example
└── README.md
```

## Examples

Run the provided examples:

```bash
# Basic usage
python examples/basic_usage.py

# Batch evaluation
python examples/batch_evaluation.py

# API client (requires server running)
python examples/api_client_example.py
```

## Dashboard Features

The interactive dashboard provides:

- **Real-time Metrics**: Total evaluations, average Trust Score, pass rates
- **Tier Breakdown**: Individual tier performance
- **Trust Score Trends**: Historical performance with baseline comparison
- **Dimension Analysis**: Breakdown across 5 evaluation dimensions
- **Drift Alerts**: Recent alerts with severity indicators
- **Auto-refresh**: Updates every 30 seconds

## Best Practices

### 1. Model Selection
- Use GPT-4 for high-stakes evaluations
- Use GPT-3.5-turbo for cost-effective bulk evaluations
- Use Claude models for alternative perspectives

### 2. Ground Truth
- Provide ground truth when available for better Tier 1 metrics
- Use reference answers to improve accuracy assessment

### 3. Batch Processing
- Process evaluations in batches for efficiency
- Use consistent run_id for related evaluations
- Monitor drift over time

### 4. Human Review
- Prioritize critical failures (Tier 1 fails, low safety)
- Use feedback to improve models
- Track reviewer agreement

### 5. Drift Monitoring
- Set appropriate baselines (7-day average recommended)
- Review alerts regularly
- Investigate sudden changes

## Troubleshooting

### Common Issues

**API Connection Error**
```bash
# Ensure server is running
python -m cee_pipeline.api.main
```

**Database Not Found**
```python
# Initialize database
from cee_pipeline.database.database import db
db.create_tables()
```

**Missing API Keys**
```bash
# Check .env file
cat .env
# Ensure OPENAI_API_KEY or ANTHROPIC_API_KEY is set
```

## Contributing

Contributions welcome! Areas for enhancement:
- Additional Tier 1 checks (custom rules)
- More LLM judge providers
- Advanced drift detection algorithms
- Enhanced dashboard features

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check examples/ directory for usage patterns
- Review API docs at `/docs` endpoint

## Roadmap

- [ ] Multi-language support
- [ ] Custom evaluation dimensions
- [ ] A/B testing framework
- [ ] Advanced analytics
- [ ] Integration with popular ML platforms
- [ ] Real-time streaming evaluations

---

Built with ❤️ for reliable AI evaluation
