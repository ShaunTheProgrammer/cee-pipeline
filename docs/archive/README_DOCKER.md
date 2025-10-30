# 🐳 CEE Pipeline - Docker Edition

> **Complete three-tier AI evaluation system, now fully Dockerized!**

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

## Two Ways to Run

### 🐳 **Option 1: Docker (Recommended)**

**Fastest way to get started!** Everything runs in containers.

```bash
# 3 commands to run everything
make setup        # Setup environment
# Edit .env and add API key
make up          # Start all services
```

**✅ Advantages:**
- ⚡ Start in under 60 seconds
- 🔒 Isolated from your system
- 📦 Includes PostgreSQL, Redis, Nginx
- 🚀 Production-ready
- 🌍 Works on Mac, Windows, Linux
- 🔄 Easy updates and scaling

→ **[Docker Quick Start Guide](DOCKER_QUICKSTART.md)**

### 💻 **Option 2: Native Python**

Run directly on your system (no Docker required).

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add API key
python run_pipeline.py
```

**✅ Advantages:**
- 🎯 Direct access to code
- 🔧 Easier debugging
- 💡 Better for learning
- 📝 Simpler for small tests

→ **[Native Setup Guide](QUICKSTART.md)**

## 📚 Documentation Map

Choose your path:

### 🚀 Quick Starts
- **[GET_STARTED.md](GET_STARTED.md)** - Absolute beginner guide (native)
- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Docker quick start (5 min)
- **[QUICKSTART.md](QUICKSTART.md)** - Detailed native setup

### 📖 Complete Guides
- **[README.md](README.md)** - Full native documentation
- **[DOCKER.md](DOCKER.md)** - Complete Docker guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep dive

### 📋 Summaries
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - What's built
- **[DOCKER_DEPLOYMENT_SUMMARY.md](DOCKER_DEPLOYMENT_SUMMARY.md)** - Docker summary

## 🎯 What is CEE Pipeline?

A **Contextual Evaluation Engine** that evaluates AI model outputs through three tiers:

```
Input → Tier 1 (Rules) → Tier 2 (AI Judge) → Tier 3 (Human) → Trust Score
```

**Tier 1**: Fast safety checks (PII, profanity, length)
**Tier 2**: AI-powered quality assessment (5 dimensions)
**Tier 3**: Human review for critical cases

**Output**: Single Trust Score (0-100) + detailed breakdown

## 🌟 Key Features

✨ **Flexible Model Selection**
- OpenAI: GPT-4, GPT-3.5-turbo
- Anthropic: Claude 3 (Opus, Sonnet, Haiku)
- Easy to switch providers

✨ **Multiple Interfaces**
- 📱 Web Dashboard
- 🔌 REST API
- 🐍 Python Library
- 💻 Interactive CLI

✨ **Production Ready**
- 🐳 Docker deployment
- 🗄️ PostgreSQL database
- 📊 Drift monitoring
- ⚠️ Alerting system
- 📈 Analytics dashboard

✨ **Developer Friendly**
- 📚 Comprehensive docs
- 🧪 Example scripts
- 🔍 Easy debugging
- 🎯 Clear API

## 🐳 Docker Features

The Docker deployment includes:

- **API Server** (FastAPI + Uvicorn)
- **PostgreSQL** (production database)
- **Redis** (caching + task queue)
- **Nginx** (reverse proxy + dashboard)
- **Health Checks** (automatic monitoring)
- **Auto-Restart** (resilient services)
- **Resource Limits** (controlled usage)
- **Easy Commands** (Makefile with 30+ shortcuts)

### Docker Services

```
┌──────────┐
│  Nginx   │  Port 80 → Dashboard + Proxy
└────┬─────┘
     │
     ▼
┌──────────┐
│   API    │  Port 8000 → CEE Pipeline
└─┬──────┬─┘
  │      │
  ▼      ▼
┌────┐ ┌────┐
│ DB │ │Redis│
└────┘ └────┘
```

## 🚀 Quick Start Comparison

| Feature | Docker | Native |
|---------|--------|--------|
| **Setup Time** | 2 min | 5 min |
| **Dependencies** | All included | Manual install |
| **Database** | PostgreSQL | SQLite |
| **Caching** | Redis | None |
| **Dashboard** | Nginx hosted | Manual serve |
| **Scaling** | Easy | Manual |
| **Production** | ✅ Ready | ⚠️ Needs setup |

## 📦 Installation

### Docker Installation

```bash
# Prerequisites: Docker Desktop or Docker Engine 20.10+

# Clone and setup
cd pmpproj1
make setup

# Edit .env and add API key
nano .env

# Start everything
make up

# Access
open http://localhost/dashboard/dashboard.html
```

### Native Installation

```bash
# Prerequisites: Python 3.8+

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Add API key

# Initialize database
python -c "from cee_pipeline.database.database import db; db.create_tables()"

# Run
python run_pipeline.py
```

## 🎓 Usage Examples

### Using Docker

```bash
# Start services
make up

# Run evaluation via API
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "test-001",
    "prompt": "What is AI?",
    "model_output": "AI is artificial intelligence...",
    "model_name": "gpt-4",
    "model_provider": "openai"
  }'

# Or access container
make shell
python examples/basic_usage.py

# View logs
make logs

# Stop services
make down
```

### Using Native Python

```python
from cee_pipeline.database.database import db
from cee_pipeline.core.pipeline import CEEPipeline
from cee_pipeline.models.schemas import EvaluationRequest, ModelProvider

db.create_tables()

pipeline = CEEPipeline(
    judge_provider=ModelProvider.OPENAI,
    judge_model="gpt-4-turbo-preview"
)

request = EvaluationRequest(
    run_id="test-001",
    prompt="What is AI?",
    model_output="AI is artificial intelligence...",
    model_name="gpt-4",
    model_provider=ModelProvider.OPENAI
)

with db.get_session() as session:
    result = pipeline.evaluate(db=session, request=request)
    print(f"Trust Score: {result.trust_score.overall}/100")
```

## 🔧 Configuration

Both methods use the same `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional (with defaults)
TIER_1_WEIGHT=0.25
TIER_2_WEIGHT=0.55
TIER_3_WEIGHT=0.20
DRIFT_THRESHOLD_ABSOLUTE=5.0
DRIFT_THRESHOLD_RELATIVE=0.10
```

Docker adds:
```bash
POSTGRES_PASSWORD=your_secure_password
```

## 📊 Accessing Services

### Docker
- **Dashboard**: http://localhost/dashboard/dashboard.html
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

### Native
- **Dashboard**: Open `cee_pipeline/dashboard/dashboard.html`
- **API**: `python -m cee_pipeline.api.main` → http://localhost:8000

## 🛠️ Common Commands

### Docker (via Makefile)

```bash
make help          # Show all commands
make up            # Start services
make down          # Stop services
make restart       # Restart
make logs          # View logs
make logs-api      # API logs only
make shell         # Access container
make db-shell      # Database shell
make db-backup     # Backup database
make health        # Health check
make status        # Service status
make stats         # Resource usage
make rebuild       # Rebuild + restart
make clean         # Cleanup
```

### Native Python

```bash
# Start API
python -m cee_pipeline.api.main

# Run examples
python examples/basic_usage.py
python examples/batch_evaluation.py

# Interactive mode
python run_pipeline.py

# Run tests
pytest cee_pipeline/tests/

# Setup verification
python setup_and_verify.py
```

## 🔍 Monitoring

### Docker Dashboard

Visit http://localhost/dashboard/dashboard.html

Includes:
- Real-time Trust Scores
- Tier performance breakdown
- Evaluation trends
- Drift alerts
- System health

### Native Dashboard

```bash
# Start API first
python -m cee_pipeline.api.main

# In another terminal, serve dashboard
cd cee_pipeline/dashboard
python -m http.server 8080

# Open browser
open http://localhost:8080/dashboard.html
```

## 🐛 Troubleshooting

### Docker Issues

```bash
# Check service status
make status

# View logs
make logs

# Health check
make health

# Complete restart
make down
make up

# Nuclear option (deletes data!)
make clean-all
make build
make up
```

### Native Issues

```bash
# Verify installation
python setup_and_verify.py

# Check database
python -c "from cee_pipeline.database.database import db; db.create_tables()"

# Test imports
python -c "from cee_pipeline.core.pipeline import CEEPipeline; print('OK')"

# Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
```

## 📈 Performance

### Docker
- **Startup**: ~30-60 seconds (all services)
- **API Response**: 2-5 seconds (depends on LLM)
- **Database**: PostgreSQL (production-grade)
- **Scaling**: `docker-compose up --scale api=3`

### Native
- **Startup**: Instant
- **API Response**: 2-5 seconds (depends on LLM)
- **Database**: SQLite (simple, file-based)
- **Scaling**: Manual (multiple processes)

## 🔒 Security

### Docker
- ✅ Network isolation
- ✅ Container sandboxing
- ✅ Resource limits
- ✅ Health checks
- ⚠️ Change default passwords!
- ⚠️ Use secrets in production

### Native
- ✅ Local execution only
- ✅ No exposed ports (unless API started)
- ⚠️ Protect .env file
- ⚠️ Don't commit API keys

## 🌍 Deployment

### Development

**Docker:**
```bash
make dev  # Live reload, debug ports, verbose logs
```

**Native:**
```bash
python run_pipeline.py  # Interactive development
```

### Production

**Docker:**
```bash
make prod  # Optimized, resource-limited, secure
```

**Native:**
```bash
# Use production WSGI server
gunicorn cee_pipeline.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 📚 Learning Path

### For Beginners
1. Read [GET_STARTED.md](GET_STARTED.md)
2. Use native Python: `python run_pipeline.py`
3. Try examples in `examples/`
4. Explore interactive API docs

### For Developers
1. Start with Docker: `make dev`
2. Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. Modify code (auto-reloads in dev mode)
4. Run tests: `make test`
5. Read full [README.md](README.md)

### For DevOps
1. Read [DOCKER.md](DOCKER.md)
2. Review [docker-compose.yml](docker-compose.yml)
3. Test scaling: `docker-compose up --scale api=3`
4. Set up monitoring
5. Configure production deployment

## 🎯 When to Use What?

**Use Docker When:**
- 🚀 You want fastest setup
- 🏢 Deploying to production
- 🔧 Need PostgreSQL + Redis
- 📦 Want complete isolation
- 🌍 Deploying to cloud
- 👥 Team collaboration

**Use Native When:**
- 📚 Learning the codebase
- 🐛 Debugging in detail
- 💡 Quick experiments
- 🎓 Educational purposes
- 💻 Limited system resources
- ⚡ Need instant startup

**Use Both:**
- Develop natively
- Test in Docker
- Deploy with Docker
- Best of both worlds!

## 🆘 Getting Help

1. **Check documentation:**
   - [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) (Docker)
   - [QUICKSTART.md](QUICKSTART.md) (Native)
   - [DOCKER.md](DOCKER.md) (Docker details)
   - [README.md](README.md) (Native details)

2. **Run diagnostics:**
   - Docker: `make health`
   - Native: `python setup_and_verify.py`

3. **Check logs:**
   - Docker: `make logs`
   - Native: Check console output

4. **Look at examples:**
   - `examples/basic_usage.py`
   - `examples/batch_evaluation.py`
   - `examples/api_client_example.py`

## 📦 What's Included

### Core Features
- ✅ Three-tier evaluation (T1, T2, T3)
- ✅ Trust Score calculation
- ✅ Multiple LLM providers
- ✅ Drift monitoring
- ✅ Human review queue

### Deployment Options
- ✅ Docker (production-ready)
- ✅ Native Python (development)
- ✅ Both fully supported

### Interfaces
- ✅ Web Dashboard
- ✅ REST API
- ✅ Python Library
- ✅ Interactive CLI

### Documentation
- ✅ 8 comprehensive guides
- ✅ 3 example scripts
- ✅ Architecture diagrams
- ✅ Troubleshooting guides

## 🎉 Success Checklist

**Docker Setup:**
- [ ] Docker installed
- [ ] `.env` file created with API key
- [ ] `make up` completed
- [ ] `make health` all green
- [ ] Dashboard loads
- [ ] API docs accessible

**Native Setup:**
- [ ] Python 3.8+ installed
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Database initialized
- [ ] Example runs successfully

## 🚀 Next Steps

1. **Choose your deployment** (Docker or Native)
2. **Follow quick start** guide for your choice
3. **Run first evaluation**
4. **Explore dashboard**
5. **Try API**
6. **Read full documentation**
7. **Customize for your needs**

---

## 📖 Documentation Index

| Guide | Purpose | Time |
|-------|---------|------|
| [GET_STARTED.md](GET_STARTED.md) | Absolute beginner (native) | 5 min |
| [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) | Docker quick start | 5 min |
| [QUICKSTART.md](QUICKSTART.md) | Detailed native setup | 10 min |
| [README.md](README.md) | Full native docs | 30 min |
| [DOCKER.md](DOCKER.md) | Complete Docker guide | 30 min |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical deep dive | 45 min |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Project overview | 10 min |
| [DOCKER_DEPLOYMENT_SUMMARY.md](DOCKER_DEPLOYMENT_SUMMARY.md) | Docker summary | 10 min |

---

**Quick Start (Docker)**: `make setup && make up`

**Quick Start (Native)**: `python run_pipeline.py`

**Need Help?**: `make help` or `python setup_and_verify.py`

---

Built with ❤️ for reliable AI evaluation
