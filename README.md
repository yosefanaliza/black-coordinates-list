# Black Coordinates List

A microservices infrastructure system for IP geolocation that converts IP addresses to geographic coordinates and stores them in Redis for fast retrieval.

## Overview

**Purpose:** Core infrastructure layer for intelligence, investigative, and operational activities that require mapping IP addresses to physical locations.

**Key Features:**
- REST API for IP address resolution
- Integration with external geolocation service (ip-api.com)
- Fast Redis-based storage with persistence
- Microservices architecture with clear separation of concerns
- Ready for Kubernetes/OpenShift deployment

## System Architecture

The system is built using a microservices architecture with clear separation of responsibilities:

```
┌─────────────────┐
│  External User  │
└────────┬────────┘
         │ POST /resolve
         │ {ip: "8.8.8.8"}
         ▼
┌─────────────────────────┐
│     Service A           │
│  IP Resolution Service  │
│  - Receives IP          │
│  - Calls external API   │
│  - Forwards coordinates │
└──────────┬──────────────┘
           │ HTTP POST /coordinates
           │ {lat, lon, city, country}
           ▼
┌─────────────────────────┐
│     Service B           │
│  Coordinate Storage     │
│  - Stores in Redis      │
│  - Retrieves data       │
└──────────┬──────────────┘
           │
           ▼
     ┌──────────┐
     │  Redis   │
     │ Database │
     └──────────┘
```

### Components

| Component | Port | Role | Technology |
|-----------|------|------|------------|
| **Service A** | 8000 | IP resolution adapter: receives IPs, calls external API, forwards data | Python, FastAPI, httpx |
| **Service B** | 8000 | Storage layer: validates, stores in Redis, provides retrieval | Python, FastAPI, redis-py |
| **Redis** | 6379 | Persistent key-value database with AOF | Redis 7 (StatefulSet) |

**Architecture Principle:** Each service has a single, well-defined responsibility and communicates only via HTTP/TCP.

## Project Structure

```
black-coordinates-list/
├── service-a/          # IP Resolution Service (FastAPI)
├── service-b/          # Coordinate Storage Service (FastAPI + Redis)
├── k8s/               # Kubernetes/OpenShift deployment manifests
├── docker-compose.yml # Local development environment
└── CLAUDE.md          # Developer guide for AI assistants
```

Each service follows a clean architecture: `main.py` (app) → `routes.py` (HTTP) → `services.py`/`storage.py` (logic) → `schemas.py` (validation).

## Quick Start

### Local Development (Docker Compose)

**Prerequisites:** Docker 20.10+, Docker Compose 2.0+

```bash
# Start all services
docker-compose up --build

# Test the system
curl -X POST http://localhost:8000/resolve \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'

# Retrieve all coordinates
curl http://localhost:8001/coordinates

# Stop services
docker-compose down
```

**Service URLs:**
- Service A: http://localhost:8000 (external API)
- Service B: http://localhost:8001 (internal API)
- Interactive docs: http://localhost:8000/docs

### Kubernetes/OpenShift Deployment

**Prerequisites:** Minikube/OpenShift cluster, kubectl/oc CLI

**Deployment order is critical** - services must be deployed in dependency order:

```bash
# 1. Redis (database layer)
kubectl apply -f k8s/redis-statefulset.yaml
kubectl apply -f k8s/redis-service.yaml

# 2. Service B (storage layer - depends on Redis)
kubectl apply -f k8s/service-b-deployment.yaml
kubectl apply -f k8s/service-b-service.yaml

# 3. Service A (API layer - depends on Service B)
kubectl apply -f k8s/service-a-deployment.yaml
kubectl apply -f k8s/service-a-service.yaml

# 4. External access (OpenShift only)
kubectl apply -f k8s/service-a-route.yaml
```

**Access:**
- Minikube: `minikube service service-a --url`
- OpenShift: Route URL from `oc get route blackcoord-external`

See [CLAUDE.md](CLAUDE.md) for detailed deployment commands, debugging, and troubleshooting.

## API Reference

### Service A (External API)

| Endpoint | Method | Purpose | Request Example |
|----------|--------|---------|-----------------|
| `/resolve` | POST | Resolve IP to coordinates | `{"ip": "8.8.8.8"}` |
| `/health` | GET | Health check | - |
| `/` | GET | Service info | - |

**Response codes:** 200 (success), 400 (invalid IP), 502 (external API error), 503 (service unavailable)

**Example:**
```bash
curl -X POST http://localhost:8000/resolve \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'

# Returns:
{
  "success": true,
  "ip": "8.8.8.8",
  "coordinates": {"lat": 37.751, "lon": -97.822}
}
```

### Service B (Internal API)

| Endpoint | Method | Purpose | Access |
|----------|--------|---------|--------|
| `/coordinates` | POST | Store coordinates | Service A only |
| `/coordinates` | GET | Retrieve all data | Internal/admin |
| `/health` | GET | Health check | Internal |

**Interactive API Documentation:**
- Service A: http://localhost:8000/docs (Swagger UI)
- Service B: http://localhost:8001/docs (Swagger UI)

## Configuration

### Environment Variables

**Service A:**
- `SERVICE_B_HOST` - Service B hostname (required)
- `SERVICE_B_PORT` - Service B port (default: 8000 for Docker, 80 for K8s)
- `IP_API_TIMEOUT` - External API timeout in seconds (default: 5)
- `LOG_LEVEL` - Logging level (default: INFO)

**Service B:**
- `REDIS_HOST` - Redis hostname (default: redis / redis-0.redis for K8s)
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_DB` - Redis database number (default: 0)
- `LOG_LEVEL` - Logging level (default: INFO)

See `.env.example` for local development configuration.

### External Dependencies

**ip-api.com Geolocation Service:**
- Free tier: 45 requests/minute
- No API key required
- Endpoint: `http://ip-api.com/json/{ip}`
- Returns: latitude, longitude, city, country, ISP, timezone

**For production:** Consider premium tier, alternative providers, or caching frequent lookups.

## Development

### Git Workflow

```bash
# Branch strategy
main           # Stable production code
dev            # Main development branch
feature/*      # Feature branches

# Commit convention
<type>: <description>
# Types: feat, fix, refactor, docs, chore

# Mandatory code review before merge to dev
```

### Debugging

```bash
# View logs
docker-compose logs -f service-a
kubectl logs -l app=service-a --tail=100

# Health checks
curl http://localhost:8000/health

# Access Redis
docker exec -it blackcoord-redis redis-cli
kubectl exec -it redis-0 -- redis-cli
```

For detailed commands and troubleshooting, see [CLAUDE.md](CLAUDE.md).

## Troubleshooting

### Common Issues

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| Service A returns 503 | Service B unreachable | Check Service B pods: `kubectl get pods -l app=service-b` |
| Service B can't connect to Redis | Redis pod not ready | Verify: `kubectl exec redis-0 -- redis-cli ping` |
| External API rate limit (45/min) | Too many requests | Wait 1 minute, implement caching, or upgrade tier |
| Pods crash on startup | Image/config issues | Check logs: `kubectl logs <pod-name>` and events: `kubectl describe pod <pod-name>` |

**For detailed troubleshooting guides, see [CLAUDE.md](CLAUDE.md).**

## Architecture Notes

- **Service Isolation:** Service A never touches Redis; Service B never calls external APIs
- **Deployment Order:** Redis → Service B → Service A (critical dependency chain)
- **Redis Persistence:** StatefulSet with AOF ensures data survives pod restarts
- **Security:** Service B uses ClusterIP (internal only), all inputs validated via Pydantic

## License

Internal organizational project.
