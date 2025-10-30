# 🚀 Getting Started with CEE Pipeline

**Welcome!** Get the CEE Pipeline running in under 5 minutes.

## What You Need

- Computer with Docker OR Python 3.8+
- OpenAI OR Anthropic API key
- 5 minutes

## Choose Your Path

### 🐳 Path 1: Docker (Easiest)

**Recommended if you have Docker installed**

```bash
# Step 1: Setup
make setup

# Step 2: Edit .env file and add your API key
nano .env
# Add: OPENAI_API_KEY=sk-your-actual-key
# Or:  ANTHROPIC_API_KEY=sk-ant-your-actual-key

# Step 3: Start everything
make up

# Step 4: Open dashboard
open http://localhost/dashboard/dashboard.html
```

**That's it!** 🎉

### 💻 Path 2: Python (Alternative)

**If you don't have Docker**

```bash
# Step 1: Install
pip install -r requirements.txt

# Step 2: Setup environment
cp .env.example .env
nano .env  # Add your API key

# Step 3: Initialize
python -c "from cee_pipeline.database.database import db; db.create_tables()"

# Step 4: Run
python run_pipeline.py
```

## What Can You Do?

### 1. Use the Dashboard

- **Docker**: http://localhost/dashboard/dashboard.html
- **Native**: Open `cee_pipeline/dashboard/dashboard.html` in browser

See real-time metrics, trust scores, and evaluation results!

### 2. Try the API

```bash
# Visit interactive docs
open http://localhost:8000/docs

# Or make a request
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "test-001",
    "prompt": "What is AI?",
    "model_output": "AI is artificial intelligence...",
    "model_name": "gpt-4",
    "model_provider": "openai"
  }'
```

### 3. Run Examples

```bash
# Docker
make shell
python examples/basic_usage.py

# Native
python examples/basic_usage.py
```

### 4. Interactive Mode

```bash
python run_pipeline.py
```

Choose your model, enter text to evaluate, see results!

## Quick Commands (Docker)

```bash
make up         # Start
make down       # Stop
make logs       # View logs
make status     # Check status
make help       # Show all commands
```

## Quick Commands (Native)

```bash
python run_pipeline.py              # Interactive
python -m cee_pipeline.api.main     # Start API
python examples/basic_usage.py      # Run example
pytest cee_pipeline/tests/          # Run tests
```

## Need Help?

**Something not working?**

1. **Docker users**: Run `make health`
2. **Native users**: Run `python setup_and_verify.py`
3. **Check logs**: `make logs` (Docker) or see console output

**Want to learn more?**

- Full guide: [README.md](README.md)
- Technical details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Docker guide: [docs/DOCKER.md](docs/DOCKER.md)

## Understanding Results

When you run an evaluation, you get a **Trust Score** (0-100):

- **90-100**: Excellent ✅
- **80-89**: Good 👍
- **70-79**: Acceptable ⚠️
- **60-69**: Poor ❌
- **<60**: Failing 🚫

The score combines:
- **Tier 1** (25%): Safety checks (PII, profanity, length)
- **Tier 2** (55%): AI quality assessment (5 dimensions)
- **Tier 3** (20%): Human review (if needed)

## What's Next?

1. ✅ **Evaluate your first output** (using any method above)
2. ✅ **Explore the dashboard** (see metrics and trends)
3. ✅ **Try different models** (GPT-4, GPT-3.5, Claude)
4. ✅ **Read the full guide** ([README.md](README.md))
5. ✅ **Customize configuration** (edit `.env` file)

## Common First-Time Issues

**"Port already in use"**
```bash
# Docker: Change port in docker-compose.yml
# Native: API runs on 8000, dashboard on 8080
```

**"API key not found"**
```bash
# Make sure .env file exists and has your key
cat .env | grep API_KEY
```

**"Module not found"**
```bash
# Native: Reinstall dependencies
pip install -r requirements.txt
```

**"Database error"**
```bash
# Native: Reinitialize
python -c "from cee_pipeline.database.database import db; db.create_tables()"
```

## Documentation Overview

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - This file (absolute basics)
- **[README.md](README.md)** - Complete guide (start here after this)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - How it works
- **[docs/DOCKER.md](docs/DOCKER.md)** - Advanced Docker usage
- **[docs/](docs/)** - All documentation

## Quick Reference Card

| I want to... | Command |
|--------------|---------|
| Start (Docker) | `make up` |
| Start (Native) | `python run_pipeline.py` |
| Stop (Docker) | `make down` |
| View logs (Docker) | `make logs` |
| Access dashboard (Docker) | http://localhost |
| Access API docs | http://localhost:8000/docs |
| Run example | `python examples/basic_usage.py` |
| Get help (Docker) | `make help` |
| Check health (Docker) | `make health` |
| Verify (Native) | `python setup_and_verify.py` |

## Success Checklist

Setup is complete when:

- [ ] Services started without errors
- [ ] Dashboard loads in browser
- [ ] API docs accessible
- [ ] First evaluation runs successfully
- [ ] Results appear in dashboard

**All checked?** You're ready! 🎉

## Support

- 📖 **Documentation**: See links above
- 💬 **Questions**: Check [README.md](README.md) troubleshooting section
- 🐛 **Issues**: Review examples in `examples/` directory

---

**Quick Start**: Choose Docker or Native path above

**Full Documentation**: [README.md](README.md)

**Need Help**: `make help` or `python setup_and_verify.py`

---

Welcome to CEE Pipeline! 🚀
