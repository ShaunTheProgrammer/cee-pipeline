# CEE Pipeline - Quick Start Guide

Get up and running with the Contextual Evaluation Engine in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key OR Anthropic API key

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your API key(s)
# Add at least one of:
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=your-key-here
```

### 3. Initialize Database

```bash
python -c "from cee_pipeline.database.database import db; db.create_tables()"
```

## Running Your First Evaluation

### Option 1: Interactive Mode (Recommended for First-Time Users)

```bash
python run_pipeline.py
```

This launches an interactive menu where you can:
1. Select your preferred model (OpenAI or Anthropic)
2. Enter your evaluation data
3. See detailed results

### Option 2: Python Script

```python
from cee_pipeline.database.database import db
from cee_pipeline.core.pipeline import CEEPipeline
from cee_pipeline.models.schemas import EvaluationRequest, ModelProvider

# Initialize database
db.create_tables()

# Create pipeline
pipeline = CEEPipeline(
    judge_provider=ModelProvider.OPENAI,
    judge_model="gpt-4-turbo-preview"
)

# Create evaluation request
request = EvaluationRequest(
    run_id="quickstart-001",
    prompt="What is the capital of France?",
    model_output="The capital of France is Paris.",
    model_name="gpt-4",
    model_provider=ModelProvider.OPENAI
)

# Run evaluation
with db.get_session() as session:
    result = pipeline.evaluate(db=session, request=request)
    print(f"Trust Score: {result.trust_score.overall}/100")
```

### Option 3: API Server

```bash
# Start the server
python -m cee_pipeline.api.main

# In another terminal, make a request
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "api-test",
    "prompt": "What is machine learning?",
    "model_output": "Machine learning is...",
    "model_name": "gpt-4",
    "model_provider": "openai"
  }'
```

## Model Selection Guide

### For LLM-as-a-Judge (Tier 2 Evaluation)

**OpenAI Models:**
- `gpt-4-turbo-preview` - Best quality, recommended for production
- `gpt-4` - High quality, slightly slower
- `gpt-3.5-turbo` - Fast and cost-effective for bulk evaluations

**Anthropic Models:**
- `claude-3-opus-20240229` - Highest capability
- `claude-3-sonnet-20240229` - Balanced performance/cost
- `claude-3-haiku-20240307` - Fast and efficient

### Which Model to Choose?

**Use GPT-4 Turbo when:**
- Evaluating high-stakes production outputs
- Need detailed reasoning
- Quality is more important than speed/cost

**Use GPT-3.5 Turbo when:**
- Processing large batches
- Cost optimization is important
- Quick feedback is needed

**Use Claude Opus when:**
- Want alternative perspective from non-OpenAI model
- Evaluating nuanced content
- Need strong reasoning capabilities

**Use Claude Haiku when:**
- Processing very large volumes
- Need fast turnaround
- Cost is a primary concern

## Understanding Your Results

### Trust Score (0-100)

Your overall quality metric combining all three evaluation tiers:

- **90-100**: Excellent - production ready
- **80-89**: Good - minor improvements possible
- **70-79**: Acceptable - some issues to address
- **60-69**: Poor - significant improvements needed
- **<60**: Failing - major issues detected

### Tier Breakdown

**Tier 1 (25% weight)**: Automated safety checks
- Pass = 100, Fail = variable based on violations
- Critical: PII leaks, profanity, policy violations

**Tier 2 (55% weight)**: AI judge quality assessment
- 5 dimensions scored 1-5 each
- Converted to 0-100 scale
- Largest contributor to Trust Score

**Tier 3 (20% weight)**: Human review (if triggered)
- Approved = 100
- Needs Revision = 60
- Rejected = 20

## Common Use Cases

### 1. Evaluate Model Before Deployment

```python
# Test your model output before going live
request = EvaluationRequest(
    run_id="pre-deployment",
    prompt=user_prompt,
    model_output=model_response,
    ground_truth=expected_answer,  # if available
    model_name="your-model",
    model_provider=ModelProvider.OPENAI
)
```

### 2. Batch Test Dataset

```python
# Run examples/batch_evaluation.py
python examples/batch_evaluation.py
```

### 3. Monitor Production Outputs

```python
# Continuous monitoring
for output in production_outputs:
    result = pipeline.evaluate(db=session, request=output)
    if result.trust_score.overall < 70:
        alert_team(result)
```

### 4. Compare Models

```python
# Evaluate same prompt with different models
for model in ["gpt-4", "gpt-3.5-turbo"]:
    request.model_name = model
    result = pipeline.evaluate(db=session, request=request)
    print(f"{model}: {result.trust_score.overall}")
```

## Viewing the Dashboard

### Option 1: Simple HTTP Server

```bash
cd cee_pipeline/dashboard
python -m http.server 8080
# Navigate to http://localhost:8080/dashboard.html
```

### Option 2: With API Running

```bash
# Terminal 1: Start API
python -m cee_pipeline.api.main

# Terminal 2: Serve dashboard
cd cee_pipeline/dashboard
python -m http.server 8080

# Open http://localhost:8080/dashboard.html in browser
```

The dashboard shows:
- Real-time trust scores
- Tier performance breakdown
- Drift alerts
- Evaluation trends

## Next Steps

1. **Run Examples**: Check `examples/` directory for more use cases
2. **Read Full Docs**: See `README.md` for comprehensive documentation
3. **Explore API**: Visit `http://localhost:8000/docs` when server is running
4. **Customize**: Adjust weights in `.env` for your use case
5. **Monitor Drift**: Set up alerts for production monitoring

## Troubleshooting

**"No module named 'cee_pipeline'"**
```bash
# Make sure you're in the project root directory
cd /Users/shaundeshpande/Documents/pmpproj1
```

**"API key not found"**
```bash
# Check .env file exists and has your key
cat .env | grep API_KEY
```

**"Connection refused" when using API**
```bash
# Make sure API server is running
python -m cee_pipeline.api.main
```

**Database errors**
```bash
# Reinitialize database
python -c "from cee_pipeline.database.database import db; db.create_tables()"
```

## Support

- Full documentation: `README.md`
- API docs: `http://localhost:8000/docs` (when server running)
- Examples: `examples/` directory
- Issues: Create an issue on GitHub

---

Happy Evaluating! 🚀
