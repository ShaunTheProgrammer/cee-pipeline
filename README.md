# CEE Pipeline - Contextual Evaluation Engine

> **Three-tier AI evaluation system with Trust Score calculation**

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 🎯 What is CEE Pipeline?

CEE Pipeline evaluates AI model outputs through **three complementary tiers**:

```
Input → Tier 1 (Rules) → Tier 2 (AI Judge) → Tier 3 (Human) → Trust Score (0-100)
```

- **Tier 1** (25%): Fast rule-based checks (PII, profanity, token limits, ROUGE/BLEU)
- **Tier 2** (55%): LLM-as-a-Judge across 5 quality dimensions
- **Tier 3** (20%): Targeted human review for critical cases

**Result**: Single actionable **Trust Score** (0-100) with detailed breakdown

## 🚀 Quick Start

Choose your preferred method:

### 🐳 Option 1: Docker (Recommended for Production)

**Best for:** Production deployment, complete isolation, scalability

```bash
# 3 commands to run everything
make setup              # Create .env file
# Edit .env and add your OPENAI_API_KEY or ANTHROPIC_API_KEY
make up                 # Start all services (API + PostgreSQL + Redis + Nginx)
```

**Access:**
- Dashboard: http://localhost/dashboard/dashboard.html
- API Docs: http://localhost:8000/docs

**Services included:** API, PostgreSQL, Redis, Nginx

→ **[Docker Setup Guide](#docker-setup)**

### 💻 Option 2: Native Python

**Best for:** Development, learning, quick experiments

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your API key
python run_pipeline.py  # Interactive mode
```

→ **[Native Setup Guide](#native-setup)**

## 📋 Table of Contents

- [Features](#features)
- [Docker Setup](#docker-setup)
- [Native Setup](#native-setup)
- [Usage Examples](#usage-examples)
- [Model Selection](#model-selection)
- [Configuration](#configuration)
- [Dashboard](#dashboard)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)

## ✨ Features

### Core Capabilities

- **Three-Tier Evaluation**: Automated, AI-powered, and human review
- **Trust Score**: Single 0-100 metric combining all tiers
- **Multiple Models**: OpenAI (GPT-4, GPT-3.5) and Anthropic (Claude 3)
- **Drift Monitoring**: Track performance changes over time
- **Smart Review Queue**: Automatic flagging of high-risk outputs
- **5 Quality Dimensions**: Accuracy, Safety, Alignment, Tone, Conciseness

### Deployment Options

- **Docker**: Production-ready with PostgreSQL, Redis, Nginx
- **Native**: Simple Python installation for development
- **Both Supported**: Choose based on your needs

### Interfaces

- **Web Dashboard**: Real-time metrics and visualization
- **REST API**: Integration-ready with OpenAPI docs
- **Python Library**: Direct programmatic access
- **Interactive CLI**: Hands-on evaluation

## 🐳 Docker Setup

### Prerequisites

- Docker Desktop or Docker Engine 20.10+
- Docker Compose 2.0+
- OpenAI or Anthropic API key

### Installation

```bash
# 1. Setup environment
make setup
# This creates .env file from template

# 2. Configure API key
nano .env
# Add: OPENAI_API_KEY=sk-your-key-here
# Or:  ANTHROPIC_API_KEY=sk-ant-your-key-here
# Change: POSTGRES_PASSWORD=your_secure_password

# 3. Start all services
make up

# 4. Verify health
make health
```

### Docker Architecture

```
┌──────────┐
│  Nginx   │  Port 80 → Dashboard + Reverse Proxy
│  :80     │
└────┬─────┘
     │
     ▼
┌──────────┐
│   API    │  Port 8000 → CEE Pipeline
│  :8000   │  • Tier 1, 2, 3 Evaluators
└─┬──────┬─┘  • Trust Score Calculator
  │      │    • Drift Monitor
  ▼      ▼
┌────┐ ┌────┐
│ PG │ │Redis│
│:5432│ │:6379│
└────┘ └────┘
```

### Docker Commands

```bash
# Essential
make up              # Start all services
make down            # Stop all services
make restart         # Restart services
make logs            # View logs
make status          # Check status
make health          # Health check

# Development
make dev             # Dev mode with live reload
make shell           # Access API container
make db-shell        # PostgreSQL shell

# Database
make db-backup       # Backup database
make db-restore      # Restore from backup

# Monitoring
make stats           # Resource usage
make logs-api        # API logs only

# Help
make help            # Show all commands
```

### Docker Services

- **cee-api**: FastAPI application (CEE Pipeline)
- **cee-postgres**: PostgreSQL 15 database
- **cee-redis**: Redis 7 for caching
- **cee-nginx**: Nginx reverse proxy

### Development vs Production

```bash
# Development (live reload, debug ports)
make dev

# Production (optimized, resource-limited)
make prod
```

## 💻 Native Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI or Anthropic API key

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
nano .env  # Add your API key

# 3. Initialize database
python -c "from cee_pipeline.database.database import db; db.create_tables()"

# 4. Verify installation
python setup_and_verify.py
```

### Running the Pipeline

```bash
# Interactive mode (easiest)
python run_pipeline.py

# API server
python -m cee_pipeline.api.main
# Access at http://localhost:8000/docs

# Run examples
python examples/basic_usage.py
python examples/batch_evaluation.py

# Run tests
pytest cee_pipeline/tests/
```

## 📖 Usage Examples

### Example 1: Single Evaluation (Python)

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

# Create request
request = EvaluationRequest(
    run_id="example-001",
    prompt="What is machine learning?",
    model_output="Machine learning is a type of AI that learns from data...",
    ground_truth="Machine learning is a subset of AI...",  # Optional
    model_name="gpt-4",
    model_provider=ModelProvider.OPENAI
)

# Evaluate
with db.get_session() as session:
    result = pipeline.evaluate(db=session, request=request)

print(f"Trust Score: {result.trust_score.overall}/100")
print(f"Tier 1 Passed: {result.tier_1_result.passed}")
print(f"Tier 2 Score: {result.tier_2_result.overall_score}/5")
```

### Example 2: Using the API

```bash
# Start API server (Docker or Native)
# Docker: make up
# Native: python -m cee_pipeline.api.main

# Make request
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "api-test-001",
    "prompt": "Explain photosynthesis",
    "model_output": "Photosynthesis is the process plants use to convert light into energy...",
    "model_name": "gpt-4",
    "model_provider": "openai"
  }'
```

### Example 3: Batch Processing

```python
# See examples/batch_evaluation.py for complete example
for item in dataset:
    request = EvaluationRequest(
        run_id="batch-001",
        prompt=item["prompt"],
        model_output=item["output"],
        model_name="gpt-4",
        model_provider=ModelProvider.OPENAI
    )

    with db.get_session() as session:
        result = pipeline.evaluate(db=session, request=request)
        print(f"Item {item['id']}: Trust Score {result.trust_score.overall}/100")
```

### Example 4: From Docker Container

```bash
# Access container
make shell

# Run evaluation
python examples/basic_usage.py

# Or use interactive mode
python run_pipeline.py
```

## 🎨 Model Selection

CEE Pipeline supports multiple LLM providers for Tier 2 (LLM-as-a-Judge):

### OpenAI Models

```python
pipeline = CEEPipeline(
    judge_provider=ModelProvider.OPENAI,
    judge_model="gpt-4-turbo-preview"  # Recommended
    # or "gpt-4"                        # High quality
    # or "gpt-3.5-turbo"                # Fast & cost-effective
)
```

### Anthropic Models

```python
pipeline = CEEPipeline(
    judge_provider=ModelProvider.ANTHROPIC,
    judge_model="claude-3-opus-20240229"     # Highest capability
    # or "claude-3-sonnet-20240229"          # Balanced
    # or "claude-3-haiku-20240307"           # Fast
)
```

### Choosing the Right Model

| Model | Best For | Cost | Speed |
|-------|----------|------|-------|
| GPT-4 Turbo | Production, high-stakes | $$$ | Medium |
| GPT-3.5 Turbo | Bulk evaluations, dev | $ | Fast |
| Claude Opus | Nuanced content | $$$ | Medium |
| Claude Haiku | Large volumes | $ | Fast |

## ⚙️ Configuration

All configuration is done via `.env` file:

```bash
# Required: At least one API key
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Trust Score Weights (must sum to 1.0)
TIER_1_WEIGHT=0.25
TIER_2_WEIGHT=0.55
TIER_3_WEIGHT=0.20

# Drift Monitoring
DRIFT_THRESHOLD_ABSOLUTE=5.0      # Absolute change threshold
DRIFT_THRESHOLD_RELATIVE=0.10     # 10% relative change

# Human Review
TIER_3_SAMPLING_RATE=0.20         # 20% random sampling

# Database (Docker only)
POSTGRES_PASSWORD=secure_password_here
DATABASE_URL=postgresql://user:pass@host:5432/db

# Optional
LOG_LEVEL=INFO
```

## 📊 Dashboard

### Accessing the Dashboard

**Docker:**
```bash
make up
# Visit http://localhost/dashboard/dashboard.html
```

**Native:**
```bash
# Terminal 1: Start API
python -m cee_pipeline.api.main

# Terminal 2: Serve dashboard
cd cee_pipeline/dashboard
python -m http.server 8080

# Visit http://localhost:8080/dashboard.html
```

### Dashboard Features

- **Real-time Metrics**: Total evaluations, average Trust Score
- **Tier Breakdown**: Individual tier performance
- **Trust Score Trends**: Historical performance with baseline
- **Dimension Analysis**: 5 quality dimensions breakdown
- **Drift Alerts**: Recent alerts with severity
- **Auto-refresh**: Updates every 30 seconds

## 🔌 API Reference

### Main Endpoints

**POST /evaluate** - Create evaluation
```json
{
  "run_id": "test-001",
  "prompt": "User prompt",
  "model_output": "Model response",
  "ground_truth": "Reference answer (optional)",
  "model_name": "gpt-4",
  "model_provider": "openai"
}
```

**GET /evaluations/{id}** - Get evaluation by ID

**GET /evaluations/run/{run_id}** - Get all evaluations for a run

**GET /review/queue** - Get pending human reviews

**POST /review/{id}/submit** - Submit human review

**GET /dashboard/metrics** - Get dashboard metrics

**GET /drift/alerts** - Get drift alerts

### Interactive API Docs

Visit http://localhost:8000/docs (when API is running)

## 🏗️ Architecture

### Evaluation Flow

```
1. User → API → EvaluationRequest
2. API → Tier 1 Evaluator → Rule-based checks
   ↓ Pass/Fail + Metrics
3. API → Tier 2 Evaluator → LLM Judge (5 dimensions)
   ↓ Scores + Reasoning
4. API → Tier 3 Decision → Queue if needed
   ↓ Human review (optional)
5. API → Trust Score Calculator → Weighted aggregation
   ↓ Trust Score (0-100)
6. API → Database → Persist results
7. API → Drift Monitor → Track metrics
8. API → Response → Return to user
```

### Three-Tier Evaluation

**Tier 1: Rule-Based (Continuous)**
- PII detection (email, SSN, phone, credit cards)
- Profanity filtering
- Token limit validation
- ROUGE and BLEU scores (if ground truth provided)
- **Output**: Pass/fail with detailed breakdown

**Tier 2: LLM-as-a-Judge (Scheduled)**
- **Factual Accuracy**: Correctness, hallucination detection
- **Safety & Policy**: Policy violations, harmful content
- **Alignment**: Intent understanding, helpfulness
- **Tone & Style**: Brand consistency, professionalism
- **Conciseness**: Optimal length, efficiency
- **Output**: 1-5 scores + reasoning + uncertainty flag

**Tier 3: Human Review (On-Demand)**
- Triggered by: Tier 1 fail, low safety, uncertainty, low quality
- Priority-based queue
- **Output**: Approved/Rejected/Needs Revision + notes

### Trust Score Formula

```python
Trust Score = 0.25 × Tier_1_Score + 0.55 × Tier_2_Score + 0.20 × Tier_3_Score

# Tier 1: 0-100 (100 if passed, deductions for violations)
# Tier 2: 0-100 (average of 5 dimensions × 20)
# Tier 3: 0-100 (approved=100, revision=60, rejected=20)
```

For complete technical details, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 🐛 Troubleshooting

### Docker Issues

```bash
# Check service status
make status

# View logs
make logs

# Health check all services
make health

# Restart everything
make down && make up

# Reset database (⚠️ deletes data)
make db-reset

# Complete cleanup (⚠️ deletes everything)
make clean-all
```

### Native Issues

```bash
# Verify installation
python setup_and_verify.py

# Check API key
cat .env | grep API_KEY

# Reinitialize database
python -c "from cee_pipeline.database.database import db; db.create_tables()"

# Test imports
python -c "from cee_pipeline.core.pipeline import CEEPipeline; print('OK')"
```

### Common Problems

**"Port already in use"**
```bash
# Find process
lsof -i :8000  # or :80, :5432

# Docker: Change port in docker-compose.yml
# Native: Use different port
```

**"Cannot connect to database" (Docker)**
```bash
# Check PostgreSQL is running
make status

# Wait 30s for initialization
make health

# Check logs
make logs-db
```

**"API key not found"**
```bash
# Verify .env file exists
ls -la .env

# Check content (don't show actual key!)
cat .env | grep -o "OPENAI_API_KEY=sk-.*" | head -c 25
```

## 📚 Documentation

### Quick References

- **This File**: Complete guide (Docker + Native)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Technical deep dive
- **[docs/DOCKER.md](docs/DOCKER.md)**: Advanced Docker guide
- **Examples**: See `examples/` directory

### Comparison: Docker vs Native

| Feature | Docker | Native |
|---------|--------|--------|
| **Setup Time** | 2 min | 5 min |
| **Dependencies** | All included | Manual install |
| **Database** | PostgreSQL | SQLite |
| **Caching** | Redis | None |
| **Scaling** | Easy (`--scale api=3`) | Manual |
| **Isolation** | Complete | None |
| **Production** | ✅ Ready | Needs setup |
| **Development** | Live reload | Direct access |

**Recommendation:**
- Use **Docker** for production, team collaboration, deployment
- Use **Native** for learning, debugging, quick experiments

## 🔒 Security Best Practices

### Before Production

- [ ] Change default PostgreSQL password
- [ ] Use Docker secrets for API keys
- [ ] Enable SSL/TLS (HTTPS)
- [ ] Remove exposed ports
- [ ] Set up firewall rules
- [ ] Use managed PostgreSQL
- [ ] Enable API authentication
- [ ] Set up rate limiting
- [ ] Configure log aggregation
- [ ] Set up monitoring alerts

## 📈 Performance & Scaling

### Resource Requirements

**Minimum:**
- 2GB RAM
- 2 CPU cores
- 5GB disk

**Recommended (Production):**
- 4GB+ RAM
- 4+ CPU cores
- 20GB+ disk

### Scaling

**Docker:**
```bash
# Horizontal scaling
docker-compose up -d --scale api=3
```

**Native:**
```bash
# Use Gunicorn with multiple workers
gunicorn cee_pipeline.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker
```

## 🎓 Learning Path

### Beginners
1. Read this README
2. Run `python run_pipeline.py` (native) or `make up` (Docker)
3. Try `examples/basic_usage.py`
4. Explore dashboard
5. Read API docs at `/docs`

### Developers
1. Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. Use `make dev` for live reload
3. Modify code and test
4. Run `make test`
5. Explore database with `make db-shell`

### DevOps
1. Review `docker-compose.yml`
2. Test scaling
3. Set up monitoring
4. Configure production deployment
5. Set up CI/CD pipeline

## 🆘 Getting Help

1. **Check documentation**: This README covers both Docker and Native
2. **Run diagnostics**: `make health` (Docker) or `python setup_and_verify.py` (Native)
3. **View logs**: `make logs` (Docker) or check console output
4. **Check examples**: See `examples/` directory
5. **Review architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 📦 Project Structure

```
pmpproj1/
├── cee_pipeline/              # Main package
│   ├── api/                   # FastAPI application
│   ├── core/                  # Evaluation logic (T1, T2, T3)
│   ├── database/              # Data persistence
│   ├── dashboard/             # Web dashboard
│   └── models/                # Data schemas
├── examples/                  # Usage examples
├── docs/                      # Additional documentation
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Container definition
├── Makefile                   # Docker commands
├── requirements.txt           # Python dependencies
├── .env.example              # Configuration template
└── README.md                 # This file
```

## 📄 License

MIT License

## 🙏 Acknowledgments

Built with:
- FastAPI - Modern Python web framework
- SQLAlchemy - Database ORM
- OpenAI & Anthropic - LLM providers
- Docker - Containerization
- PostgreSQL - Production database

---

**Quick Start (Docker):** `make setup && make up`

**Quick Start (Native):** `python run_pipeline.py`

**Need Help?** `make help` or `python setup_and_verify.py`

---

Built with ❤️ for reliable AI evaluation
