# CEE Pipeline Documentation

## 📚 Documentation Index

### Main Documentation

**[../README.md](../README.md)** - **START HERE!**
- Complete guide covering both Docker and Native setup
- Quick start for both methods
- Usage examples
- Configuration
- Troubleshooting
- Everything you need in one place

### Technical Documentation

**[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical Deep Dive
- System architecture and data flow
- Component details
- Evaluation tiers explained
- Trust Score calculation
- Scaling considerations
- ~15 min read

**[DOCKER.md](DOCKER.md)** - Advanced Docker Guide
- Detailed Docker commands
- Production deployment
- Scaling strategies
- Security best practices
- Backup and restore
- Monitoring setup
- ~30 min read

### Archived Documentation

The `archive/` directory contains previous versions of documentation that have been consolidated into the main README. These are kept for reference but are no longer maintained.

## 🎯 Quick Navigation

**I want to...**

| Goal | Document | Section |
|------|----------|---------|
| Get started quickly | [README.md](../README.md) | Quick Start |
| Use Docker | [README.md](../README.md) | Docker Setup |
| Use native Python | [README.md](../README.md) | Native Setup |
| See code examples | [README.md](../README.md) | Usage Examples |
| Choose a model | [README.md](../README.md) | Model Selection |
| Configure settings | [README.md](../README.md) | Configuration |
| Understand architecture | [ARCHITECTURE.md](ARCHITECTURE.md) | Full document |
| Deploy to production | [DOCKER.md](DOCKER.md) | Production Section |
| Scale the system | [DOCKER.md](DOCKER.md) | Scaling Section |
| Troubleshoot issues | [README.md](../README.md) | Troubleshooting |

## 📖 Reading Order

### For Beginners
1. [README.md](../README.md) - Read Quick Start section
2. Follow setup instructions (Docker or Native)
3. Try examples in `../examples/`
4. Explore dashboard and API docs

### For Developers
1. [README.md](../README.md) - Complete read
2. [ARCHITECTURE.md](ARCHITECTURE.md) - Understand the system
3. Review code in `../cee_pipeline/`
4. Experiment with modifications

### For DevOps
1. [README.md](../README.md) - Quick Start (Docker section)
2. [DOCKER.md](DOCKER.md) - Production deployment
3. [ARCHITECTURE.md](ARCHITECTURE.md) - Scaling section
4. Set up monitoring and CI/CD

## 🔍 Finding Information

### Setup & Installation
- **Docker setup**: [README.md](../README.md#docker-setup)
- **Native setup**: [README.md](../README.md#native-setup)
- **Configuration**: [README.md](../README.md#configuration)

### Usage
- **Python examples**: [README.md](../README.md#usage-examples)
- **API reference**: [README.md](../README.md#api-reference)
- **Dashboard**: [README.md](../README.md#dashboard)

### Technical Details
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Tier 1 evaluator**: [ARCHITECTURE.md](ARCHITECTURE.md#tier-1-evaluator)
- **Tier 2 evaluator**: [ARCHITECTURE.md](ARCHITECTURE.md#tier-2-evaluator)
- **Trust Score formula**: [ARCHITECTURE.md](ARCHITECTURE.md#trust-score-calculator)

### Deployment
- **Docker commands**: [DOCKER.md](DOCKER.md#docker-commands)
- **Production deployment**: [DOCKER.md](DOCKER.md#production-deployment)
- **Scaling**: [DOCKER.md](DOCKER.md#scaling)
- **Security**: [DOCKER.md](DOCKER.md#security-considerations)

### Troubleshooting
- **Common issues**: [README.md](../README.md#troubleshooting)
- **Docker issues**: [DOCKER.md](DOCKER.md#troubleshooting)

## 📂 Documentation Structure

```
docs/
├── README.md              # This file - Documentation index
├── ARCHITECTURE.md        # Technical architecture
├── DOCKER.md             # Advanced Docker guide
└── archive/              # Old documentation (archived)
    ├── README_OLD.md
    ├── QUICKSTART.md
    ├── GET_STARTED.md
    └── ...
```

## 🆕 What Changed?

We consolidated **9 separate markdown files** into a streamlined structure:

### New Structure (3 files)
1. **README.md** - Complete guide (Docker + Native)
2. **docs/ARCHITECTURE.md** - Technical deep dive
3. **docs/DOCKER.md** - Advanced Docker guide

### Old Structure (9 files - now archived)
- README.md (native only)
- QUICKSTART.md
- GET_STARTED.md
- DOCKER_QUICKSTART.md
- DOCKER_DEPLOYMENT_SUMMARY.md
- README_DOCKER.md
- PROJECT_SUMMARY.md
- ARCHITECTURE.md
- DOCKER.md

**Why?** Clearer navigation, less confusion, easier maintenance

## 🎓 Learning Paths

### Path 1: Quick Start (15 minutes)
1. Read [README.md Quick Start](../README.md#quick-start)
2. Choose Docker or Native
3. Follow 3-step setup
4. Run first evaluation
5. Done!

### Path 2: Deep Understanding (1-2 hours)
1. Read [README.md](../README.md) completely
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Study code in `../cee_pipeline/`
4. Try modifying evaluators
5. Read [DOCKER.md](DOCKER.md) for deployment

### Path 3: Production Deployment (2-4 hours)
1. Read [README.md Docker section](../README.md#docker-setup)
2. Study [DOCKER.md](DOCKER.md) completely
3. Review [ARCHITECTURE.md scaling](ARCHITECTURE.md#scalability-considerations)
4. Set up production environment
5. Configure monitoring
6. Deploy!

## ✅ Documentation Status

| Document | Status | Last Updated | Covers |
|----------|--------|--------------|---------|
| README.md | ✅ Current | 2024-10 | Both Docker & Native |
| ARCHITECTURE.md | ✅ Current | 2024-10 | Technical details |
| DOCKER.md | ✅ Current | 2024-10 | Advanced Docker |
| archive/* | 📦 Archived | - | Historical reference |

## 🆘 Still Have Questions?

1. **Check the main README first**: [README.md](../README.md)
2. **Run diagnostics**:
   - Docker: `make health`
   - Native: `python setup_and_verify.py`
3. **Check examples**: `../examples/` directory
4. **Review architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## 🔗 External Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Docker Docs**: https://docs.docker.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **OpenAI API**: https://platform.openai.com/docs
- **Anthropic API**: https://docs.anthropic.com/

---

**Quick Start**: See [README.md](../README.md#quick-start)

**Full Guide**: [README.md](../README.md)

**Technical Details**: [ARCHITECTURE.md](ARCHITECTURE.md)
