# 🐳 Docker Quick Start - CEE Pipeline

Get the CEE Pipeline running in Docker in under 5 minutes!

## ⚡ Super Quick Start (3 Commands)

```bash
# 1. Setup environment
make setup

# 2. Edit .env and add your API key
nano .env  # Add OPENAI_API_KEY or ANTHROPIC_API_KEY

# 3. Start everything
make up
```

**That's it!** 🎉

Visit:
- **Dashboard**: http://localhost/dashboard/dashboard.html
- **API Docs**: http://localhost:8000/docs

## 📋 Prerequisites

- Docker Desktop or Docker Engine (20.10+)
- Docker Compose (2.0+)
- OpenAI or Anthropic API key

### Install Docker

**Mac:**
```bash
# Download Docker Desktop from:
https://www.docker.com/products/docker-desktop
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Windows:**
Download Docker Desktop from https://www.docker.com/products/docker-desktop

## 🚀 Detailed Setup

### Step 1: Clone/Navigate to Project

```bash
cd /Users/shaundeshpande/Documents/pmpproj1
```

### Step 2: Configure Environment

```bash
# Copy template
cp .env.docker .env

# Edit configuration
nano .env
```

**Required changes:**
```bash
# Add at least one API key
OPENAI_API_KEY=sk-your-actual-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Change default password (important!)
POSTGRES_PASSWORD=your_secure_password_here
```

### Step 3: Start Services

**Option A: Using Make (Recommended)**
```bash
make up
```

**Option B: Using Docker Compose**
```bash
docker-compose up -d
```

### Step 4: Verify Everything Works

```bash
# Check service status
make status

# Or manually
docker-compose ps
```

All services should show "healthy" status.

### Step 5: Access the Application

- **Dashboard**: http://localhost/dashboard/dashboard.html
- **API Documentation**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

## 📦 What Gets Started

The Docker setup runs 4 services:

1. **CEE API** (Port 8000) - Main application
2. **PostgreSQL** (Port 5432) - Database
3. **Redis** (Port 6379) - Cache/Queue
4. **Nginx** (Port 80) - Web server + reverse proxy

## 🎯 Common Commands

### Using Makefile (Easy!)

```bash
make help          # Show all commands
make up            # Start services
make down          # Stop services
make restart       # Restart services
make logs          # View logs
make status        # Check status
make shell         # Access API container
make db-shell      # Access database
make health        # Health check all services
```

### Using Docker Compose

```bash
docker-compose up -d              # Start
docker-compose down               # Stop
docker-compose restart            # Restart
docker-compose logs -f            # Logs
docker-compose ps                 # Status
docker-compose exec api bash      # Shell
```

## 📊 Using the Pipeline

### 1. Via Web Dashboard

Navigate to http://localhost/dashboard/dashboard.html

### 2. Via API (Interactive Docs)

Visit http://localhost:8000/docs

Try the `/evaluate` endpoint:
```json
{
  "run_id": "docker-test-001",
  "prompt": "What is machine learning?",
  "model_output": "Machine learning is a type of AI...",
  "model_name": "gpt-4-turbo-preview",
  "model_provider": "openai"
}
```

### 3. Via Python (From Host)

```python
import requests

response = requests.post("http://localhost:8000/evaluate", json={
    "run_id": "test-001",
    "prompt": "Explain AI",
    "model_output": "AI is artificial intelligence...",
    "model_name": "gpt-4",
    "model_provider": "openai"
})

result = response.json()
print(f"Trust Score: {result['trust_score']['overall']}/100")
```

### 4. Via Container Shell

```bash
# Access container
make shell

# Run Python script
python examples/basic_usage.py

# Or run interactive
python run_pipeline.py
```

## 🔍 Viewing Logs

```bash
# All services
make logs

# Specific service
make logs-api        # API logs
make logs-db         # Database logs
make logs-nginx      # Nginx logs

# Or with Docker Compose
docker-compose logs -f api
```

## 💾 Database Operations

### Backup Database

```bash
make db-backup
# Creates backup in backups/ directory
```

### Restore Database

```bash
make db-restore FILE=backups/backup_20240101.sql
```

### Access Database Shell

```bash
make db-shell

# Then run SQL
SELECT COUNT(*) FROM evaluations;
\dt  -- List tables
\q   -- Quit
```

## 🔄 Updating Code

If you modify the Python code:

```bash
# Rebuild and restart
make rebuild

# Or manually
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs
make logs

# Check status
make status

# Try clean restart
make down
make up
```

### "Port already in use"

```bash
# Check what's using the port
lsof -i :8000  # or :80, :5432

# Kill the process or change port in docker-compose.yml
```

### "Cannot connect to database"

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
make logs-db

# Restart database
docker-compose restart postgres
```

### "API is unhealthy"

```bash
# Check API logs
make logs-api

# Common issues:
# 1. Missing API key in .env
# 2. Database not ready (wait 30s)
# 3. Port conflict

# Check health
make health
```

### Clear Everything and Start Fresh

```bash
# Stop and remove all data (⚠️  deletes everything!)
docker-compose down -v

# Rebuild from scratch
make build
make up
```

## 🌍 Development vs Production

### Development Mode

```bash
# Start in dev mode with live reload
make dev

# Code changes auto-reload
# Ports exposed for debugging
# Verbose logging
```

### Production Mode

```bash
# Start in production mode
make prod

# Optimized for performance
# Resource limits enforced
# Security hardened
# Ports not exposed externally
```

## 📈 Monitoring

### Check Service Health

```bash
make health
```

### Monitor Resources

```bash
make stats

# Shows CPU, memory usage for each container
```

### View Metrics Dashboard

Visit http://localhost/dashboard/dashboard.html

## 🔒 Security Notes

### Before Production:

1. **Change default passwords** in `.env`
2. **Don't commit `.env`** to version control
3. **Use Docker secrets** for sensitive data
4. **Enable SSL/TLS** for HTTPS
5. **Limit exposed ports** (remove port mappings)
6. **Set resource limits** (already in prod config)

### Quick Security Check

```bash
# Ensure .env is gitignored
cat .gitignore | grep .env

# Check for exposed ports
docker-compose ps
```

## 📚 Next Steps

1. ✅ Run `make up` to start
2. ✅ Visit dashboard at http://localhost
3. ✅ Try API at http://localhost:8000/docs
4. ✅ Read [DOCKER.md](DOCKER.md) for advanced usage
5. ✅ Read [README.md](README.md) for pipeline details

## 🆘 Getting Help

**Check these in order:**

1. `make logs` - View logs
2. `make health` - Check service health
3. `make status` - Check service status
4. [DOCKER.md](DOCKER.md) - Full Docker guide
5. [README.md](README.md) - Main documentation

## 🎓 Quick Reference

```bash
# Lifecycle
make up           # Start
make down         # Stop
make restart      # Restart
make rebuild      # Rebuild & restart

# Monitoring
make logs         # View logs
make status       # Check status
make health       # Health check
make stats        # Resource usage

# Database
make db-backup    # Backup
make db-shell     # SQL shell

# Access
make shell        # Container shell
make url          # Show URLs

# Cleanup
make clean        # Remove stopped containers
make clean-all    # Remove everything (⚠️  DATA LOSS)
```

## 🌟 Success Checklist

- [ ] Docker installed and running
- [ ] `.env` file created with API key
- [ ] `make up` completed successfully
- [ ] `make health` shows all services healthy
- [ ] Dashboard loads at http://localhost
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Test evaluation runs successfully

**All checked?** You're ready to go! 🚀

---

**Quick Start**: `make setup && make up`

**Get Help**: `make help`
