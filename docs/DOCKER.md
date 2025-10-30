# Docker Deployment Guide for CEE Pipeline

Complete guide to running the CEE Pipeline in Docker containers.

## 🐳 What's Included

The Docker setup includes:

- **CEE API**: Main application server (FastAPI + Uvicorn)
- **PostgreSQL**: Production-ready database
- **Redis**: Task queue and caching (for future Celery integration)
- **Nginx**: Reverse proxy and dashboard hosting

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- OpenAI or Anthropic API key

## 🚀 Quick Start

### 1. Configure Environment

```bash
# Copy the Docker environment template
cp .env.docker .env

# Edit .env and add your API key(s)
nano .env  # or use your preferred editor
```

**Required:** Add at least one API key:
```bash
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

**Important:** Change the default PostgreSQL password:
```bash
POSTGRES_PASSWORD=your_secure_password_here
```

### 2. Build and Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Access the Application

Once all services are healthy (takes ~30-60 seconds):

- **Dashboard**: http://localhost/dashboard/dashboard.html
- **API Docs**: http://localhost:8000/docs
- **API Base**: http://localhost:8000
- **Health Check**: http://localhost/health

## 📦 Docker Services

### Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Nginx :80                         │
│            (Reverse Proxy + Dashboard)                   │
└──────────────────┬──────────────────────────────────────┘
                   │
     ┌─────────────┴─────────────┐
     │                           │
     ▼                           ▼
┌─────────┐                 ┌──────────┐
│   API   │◄────────────────┤   Redis  │
│  :8000  │                 │  :6379   │
└────┬────┘                 └──────────┘
     │
     │
     ▼
┌──────────────┐
│  PostgreSQL  │
│    :5432     │
└──────────────┘
```

### Service Details

**cee-api** (Main Application)
- Port: 8000
- Image: Built from Dockerfile
- Dependencies: PostgreSQL, Redis
- Auto-restarts on failure

**cee-postgres** (Database)
- Port: 5432
- Image: postgres:15-alpine
- Volume: `postgres_data`
- Credentials from `.env`

**cee-redis** (Cache/Queue)
- Port: 6379
- Image: redis:7-alpine
- Volume: `redis_data`

**cee-nginx** (Web Server)
- Ports: 80, 443
- Image: nginx:alpine
- Serves dashboard + proxies API

## 🔧 Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f api
```

### Build and Rebuild

```bash
# Build images
docker-compose build

# Rebuild and start (after code changes)
docker-compose up -d --build

# Force rebuild without cache
docker-compose build --no-cache
```

### Database Operations

```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U cee_user -d cee_pipeline

# Backup database
docker-compose exec postgres pg_dump -U cee_user cee_pipeline > backup.sql

# Restore database
docker-compose exec -T postgres psql -U cee_user cee_pipeline < backup.sql

# View database tables
docker-compose exec postgres psql -U cee_user -d cee_pipeline -c "\dt"
```

### Service Management

```bash
# Scale API service (multiple instances)
docker-compose up -d --scale api=3

# View service status
docker-compose ps

# Check resource usage
docker stats

# Execute command in container
docker-compose exec api python run_pipeline.py
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers + volumes (⚠️ deletes all data)
docker-compose down -v

# Remove unused images
docker image prune -a

# Full cleanup
docker-compose down -v
docker system prune -a
```

## 🔍 Health Checks

All services include health checks:

```bash
# Check all services
docker-compose ps

# API health
curl http://localhost:8000/

# Nginx health
curl http://localhost/health

# PostgreSQL health
docker-compose exec postgres pg_isready -U cee_user

# Redis health
docker-compose exec redis redis-cli ping
```

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f nginx
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Service resource limits (edit docker-compose.yml)
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 🔒 Security Best Practices

### 1. Change Default Credentials

```bash
# .env file
POSTGRES_PASSWORD=your_very_secure_password_here
```

### 2. Use Secrets (Production)

```yaml
# docker-compose.yml
services:
  api:
    secrets:
      - openai_api_key

secrets:
  openai_api_key:
    file: ./secrets/openai_key.txt
```

### 3. Enable SSL/TLS

```bash
# Generate self-signed certificate (development)
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt
```

Update nginx.conf for HTTPS (see nginx-ssl.conf example)

### 4. Network Isolation

The compose file uses a dedicated network (`cee-network`). Services can only communicate within this network.

## 🌍 Production Deployment

### Environment-Specific Configs

```bash
# Development
docker-compose -f docker-compose.yml up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Production Checklist

- [ ] Change all default passwords
- [ ] Use environment secrets management
- [ ] Enable SSL/TLS
- [ ] Configure backup strategy
- [ ] Set up log aggregation
- [ ] Configure resource limits
- [ ] Enable monitoring (Prometheus/Grafana)
- [ ] Set up alerting
- [ ] Use external PostgreSQL (managed service)
- [ ] Configure auto-restart policies
- [ ] Set up CI/CD pipeline

### Recommended: External Database

For production, use managed PostgreSQL:

```yaml
# docker-compose.prod.yml
services:
  api:
    environment:
      DATABASE_URL: postgresql://user:pass@your-db-host:5432/cee_pipeline
```

Remove the `postgres` service from the compose file.

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs api

# Check container status
docker-compose ps

# Rebuild and start fresh
docker-compose down
docker-compose up -d --build
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U cee_user -d cee_pipeline -c "SELECT 1"

# Check DATABASE_URL
docker-compose exec api env | grep DATABASE_URL
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # or :80, :5432, etc.

# Change ports in docker-compose.yml
services:
  api:
    ports:
      - "8001:8000"  # Use different host port
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory

# Or limit individual services
services:
  api:
    mem_limit: 512m
```

### Slow Performance

```bash
# Check resource usage
docker stats

# Optimize database
docker-compose exec postgres vacuumdb -U cee_user -d cee_pipeline -z

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

## 🔄 Updates and Migrations

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Database Migrations

```bash
# Run migrations (when using Alembic)
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"
```

## 💾 Backup and Restore

### Automated Backups

```bash
# Add to cron (daily backup at 2 AM)
0 2 * * * cd /path/to/project && docker-compose exec -T postgres pg_dump -U cee_user cee_pipeline | gzip > backups/cee_$(date +\%Y\%m\%d).sql.gz
```

### Manual Backup

```bash
# Database backup
docker-compose exec postgres pg_dump -U cee_user cee_pipeline > backup_$(date +%Y%m%d).sql

# Volume backup
docker run --rm -v cee_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_data.tar.gz /data
```

### Restore

```bash
# Restore database
docker-compose exec -T postgres psql -U cee_user cee_pipeline < backup.sql

# Restore volume
docker run --rm -v cee_postgres_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/postgres_data.tar.gz -C /
```

## 📈 Scaling

### Horizontal Scaling

```bash
# Multiple API instances
docker-compose up -d --scale api=3

# Nginx will load balance automatically
```

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml cee

# Scale service
docker service scale cee_api=5

# View services
docker service ls
```

## 🔗 Integration Examples

### Using with Docker from Host

```python
import requests

# Call API
response = requests.post("http://localhost:8000/evaluate", json={
    "run_id": "test-001",
    "prompt": "What is AI?",
    "model_output": "AI is...",
    "model_name": "gpt-4",
    "model_provider": "openai"
})

print(response.json())
```

### Using from Another Container

```yaml
# your-app/docker-compose.yml
services:
  your-app:
    networks:
      - cee_cee-network

networks:
  cee_cee-network:
    external: true
```

```python
# In your app
API_URL = "http://cee-api:8000"
```

## 📝 Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required if using OpenAI) |
| `ANTHROPIC_API_KEY` | - | Anthropic API key (required if using Anthropic) |
| `POSTGRES_PASSWORD` | `cee_password_change_me` | PostgreSQL password |
| `DATABASE_URL` | Auto | Database connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `TIER_1_WEIGHT` | `0.25` | Tier 1 weight in Trust Score |
| `TIER_2_WEIGHT` | `0.55` | Tier 2 weight in Trust Score |
| `TIER_3_WEIGHT` | `0.20` | Tier 3 weight in Trust Score |
| `DRIFT_THRESHOLD_ABSOLUTE` | `5.0` | Absolute drift threshold |
| `DRIFT_THRESHOLD_RELATIVE` | `0.10` | Relative drift threshold (10%) |
| `TIER_3_SAMPLING_RATE` | `0.20` | Human review sampling rate (20%) |
| `LOG_LEVEL` | `INFO` | Logging level |

## 🎯 Next Steps

1. **Start the services**: `docker-compose up -d`
2. **Check health**: `docker-compose ps`
3. **View dashboard**: http://localhost/dashboard/dashboard.html
4. **Try the API**: http://localhost:8000/docs
5. **Read main docs**: [README.md](README.md)

---

For questions or issues, check the logs: `docker-compose logs -f`
