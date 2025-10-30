# 🚀 Get Started with CEE Pipeline

Welcome to the **Contextual Evaluation Engine (CEE) Pipeline**!

This is a complete system for evaluating Generative AI model outputs using a three-tier approach combining automated checks, AI-powered judging, and human review.

## 📋 What You Need

- Python 3.8 or higher
- An API key from either:
  - OpenAI (for GPT models)
  - Anthropic (for Claude models)

## ⚡ Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Your API Key

Create a `.env` file:

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
OPENAI_API_KEY=sk-your-key-here

# OR for Anthropic:
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Verify Installation

```bash
python setup_and_verify.py
```

This will check everything is working correctly!

## 🎯 Choose Your Path

### Path 1: Interactive Mode (Easiest)

Perfect for first-time users:

```bash
python run_pipeline.py
```

This launches a menu where you can:
- Select your model (OpenAI or Anthropic)
- Enter text to evaluate
- See detailed results instantly

### Path 2: Python Script

For programmatic usage:

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

# Evaluate
request = EvaluationRequest(
    run_id="my-test",
    prompt="What is AI?",
    model_output="AI is artificial intelligence...",
    model_name="gpt-4",
    model_provider=ModelProvider.OPENAI
)

with db.get_session() as session:
    result = pipeline.evaluate(db=session, request=request)
    print(f"Trust Score: {result.trust_score.overall}/100")
```

### Path 3: API Server

For integration with other systems:

```bash
# Start server
python -m cee_pipeline.api.main

# Server runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 🎨 Model Selection

You can choose from multiple models for evaluation:

### OpenAI Models
```python
# Best quality
judge_model="gpt-4-turbo-preview"

# Fast and cost-effective
judge_model="gpt-3.5-turbo"
```

### Anthropic Models
```python
# Highest capability
judge_model="claude-3-opus-20240229"

# Balanced
judge_model="claude-3-sonnet-20240229"

# Fast
judge_model="claude-3-haiku-20240307"
```

**Just change the `judge_provider` and `judge_model` parameters!**

## 📊 Understanding Results

Every evaluation gives you a **Trust Score** (0-100):

- **90-100**: Excellent - production ready ✨
- **80-89**: Good - minor improvements possible 👍
- **70-79**: Acceptable - some issues to address 📝
- **60-69**: Poor - significant improvements needed ⚠️
- **<60**: Failing - major issues detected ❌

The score combines:
- **Tier 1** (25%): Automated safety checks
- **Tier 2** (55%): AI judge quality assessment
- **Tier 3** (20%): Human review (if needed)

## 🔍 Examples Included

Try these ready-to-run examples:

```bash
# Single evaluation
python examples/basic_usage.py

# Batch processing
python examples/batch_evaluation.py

# API client
python examples/api_client_example.py
```

## 📱 Dashboard

View your evaluation metrics:

1. Start the API server:
   ```bash
   python -m cee_pipeline.api.main
   ```

2. Open the dashboard:
   ```bash
   # Navigate to cee_pipeline/dashboard/dashboard.html in your browser
   ```

The dashboard shows:
- Real-time Trust Scores
- Tier performance breakdown
- Evaluation trends
- Drift alerts

## 🆘 Troubleshooting

**"No module named 'cee_pipeline'"**
```bash
# Make sure you're in the project directory
cd /Users/shaundeshpande/Documents/pmpproj1
```

**"API key not found"**
```bash
# Check your .env file
cat .env
# Make sure OPENAI_API_KEY or ANTHROPIC_API_KEY is set
```

**"Connection refused"**
```bash
# Make sure the API server is running
python -m cee_pipeline.api.main
```

## 📚 Learn More

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md) - Detailed getting started guide
- **Full Docs**: [README.md](README.md) - Complete documentation
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) - Technical deep dive
- **Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview

## 💡 What to Do Next

1. ✅ Run `python setup_and_verify.py` to verify everything works
2. ✅ Try `python run_pipeline.py` for interactive evaluation
3. ✅ Run the examples in `examples/` directory
4. ✅ Read [QUICKSTART.md](QUICKSTART.md) for detailed instructions
5. ✅ Explore the API at `http://localhost:8000/docs`

## 🎓 How It Works

```
Your Input
    ↓
┌─────────────────────┐
│  TIER 1: Rules      │  PII, profanity, length checks
│  ⚡ Instant         │  → Pass/Fail + metrics
└─────────────────────┘
    ↓
┌─────────────────────┐
│  TIER 2: AI Judge   │  5 quality dimensions
│  🤖 2-5 seconds     │  → Scores 1-5 + reasoning
└─────────────────────┘
    ↓
┌─────────────────────┐
│  TIER 3: Human      │  Only if needed (20%)
│  👤 As needed       │  → Approved/Rejected
└─────────────────────┘
    ↓
┌─────────────────────┐
│  Trust Score        │  Single metric 0-100
│  📊 Weighted avg    │  → Your quality score
└─────────────────────┘
```

## ❓ Need Help?

1. Check the documentation files listed above
2. Run `python setup_and_verify.py` to diagnose issues
3. Look at the examples in `examples/` directory
4. Review the flowchart diagram you provided

## 🌟 Features

✨ **Three-tier evaluation** - Balanced automation + quality
✨ **Multiple models** - OpenAI and Anthropic support
✨ **Trust Score** - Single actionable metric
✨ **Drift monitoring** - Track changes over time
✨ **Dashboard** - Visual analytics
✨ **API + Python** - Flexible integration
✨ **Production ready** - Database, tests, documentation

---

**Ready to evaluate your AI models? Start with:**
```bash
python run_pipeline.py
```

Happy evaluating! 🎉
