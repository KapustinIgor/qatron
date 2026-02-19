# QAtron Installation Guide

This guide covers installing and setting up QAtron for local development and production deployment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Installation (Docker Compose)](#local-installation-docker-compose)
- [CLI Installation](#cli-installation)
- [Production Installation (Kubernetes)](#production-installation-kubernetes)
- [Post-Installation Configuration](#post-installation-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### For Local Installation

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning repositories
- **4GB RAM minimum**: Recommended 8GB+
- **10GB free disk space**: For Docker images and data

### For Production Installation

- **Kubernetes**: Version 1.24 or higher
- **Helm**: Version 3.8 or higher
- **kubectl**: Configured to access your cluster
- **Storage Class**: For persistent volumes (PostgreSQL, MinIO)
- **Ingress Controller**: For external access (optional)

### Verify Prerequisites

```bash
# Check Docker
docker --version
docker compose version

# Check Kubernetes (for production)
kubectl version --client
helm version
```

## Local Installation (Docker Compose)

### First-time setup (run this once after cloning)

The API (localhost:8000) and Board (localhost:3000) are **not** started automatically when you clone the repo. You must run the installation script once so they come up. Otherwise you will see “connection refused” or “invalid response” when opening the UI or calling the API.

```bash
# From repo root (recommended)
./scripts/install.sh

# Or from the compose directory
cd deployment/docker-compose
./install.sh
```

The installation script will:
1. Check Docker and Docker Compose availability
2. Create necessary directories and .env
3. Start all services (postgres, redis, control-plane, board, etc.)
4. **Wait until the Control Plane API and Board are healthy** (script fails if they don’t come up)
5. Run migrations and print access URLs and credentials

### Manual Installation

If you prefer to install manually:

```bash
# 1. Create environment file
cp deployment/docker-compose/.env.example deployment/docker-compose/.env

# 2. Edit .env file with your settings (optional)
# nano deployment/docker-compose/.env

# 3. Start services
cd deployment/docker-compose
docker compose up -d

# 4. Wait for services to be ready
docker compose ps

# 5. Check logs
docker compose logs -f
```

### Services Started

The Docker Compose stack includes:

- **Control Plane API**: `http://localhost:8000`
- **Orchestrator**: `http://localhost:8001`
- **QAtron Board (UI)**: `http://localhost:3000`
- **PostgreSQL**: `localhost:5432`
- **RabbitMQ**: `localhost:5672`
- **Redis**: `localhost:6379`
- **MinIO**: `http://localhost:9000` (Console: `http://localhost:9001`)
- **Selenium Grid (E2E)**: `http://localhost:4444` — Hub + Chrome node start automatically; install script waits until the grid reports ready. Use `SELENIUM_GRID_URL=http://localhost:4444/wd/hub` for E2E tests.
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3001`
- **Loki**: `http://localhost:3100`

### Default Credentials

After installation, default credentials are:

- **QAtron Board (UI)**:
  - Username: `admin`
  - Password: `admin`

- **MinIO Console**:
  - Access Key: `minioadmin`
  - Secret Key: `minioadmin`

- **PostgreSQL**:
  - Username: `qatron`
  - Password: `qatron`
  - Database: `qatron`

- **RabbitMQ**:
  - Username: `guest`
  - Password: `guest`

- **Grafana**:
  - Username: `admin`
  - Password: `admin` (change on first login)

### Service Management

Use the `manage.sh` script or Makefile targets for common operations:

```bash
# From project root
make start              # Start all services
make stop               # Start all services
make restart            # Restart all services
make status             # Show service status
make logs               # View logs (make logs SVC=control-plane for one service)
make ps                 # List containers
make down               # Stop and remove containers

# Or from deployment/docker-compose directory
./manage.sh start [service]     # Start all or a specific service
./manage.sh stop [service]      # Stop all or a specific service
./manage.sh restart [service]   # Restart all or a specific service
./manage.sh status              # Show status
./manage.sh logs [-f] [service] # View logs (use -f to follow)
./manage.sh ps                  # List containers
./manage.sh down                # Stop and remove containers
```

### Database migrations

After the Control Plane and PostgreSQL are running, apply schema migrations (e.g. for service tokens, BDD features, suite/dataset fields):

```bash
# From project root, run inside the control-plane container
docker compose -f deployment/docker-compose/docker-compose.yml exec control-plane alembic upgrade head

# Or from deployment/docker-compose
docker compose exec control-plane alembic upgrade head
```

To run migrations with a local Python environment instead of Docker, set `DATABASE_URL` and run from `services/control-plane`:

```bash
cd services/control-plane
export DATABASE_URL="postgresql://qatron:qatron@localhost:5432/qatron"
poetry run alembic upgrade head
```

### Accessing Services

```bash
# View all running services
docker compose ps

# View logs for a specific service
docker compose logs -f control-plane

# Stop all services
docker compose down

# Stop and remove volumes (clean slate)
docker compose down -v
```

## CLI Installation

The QAtron CLI tool allows you to interact with QAtron from the command line.

### Install with pipx (Recommended)

```bash
# Install pipx if not already installed
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install QAtron CLI
pipx install qatron

# Verify installation
qatron --version
```

### Install with pip

```bash
# Install globally
pip install qatron

# Or install in virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install qatron
```

### Install from Source

```bash
# Clone repository
git clone https://github.com/qatron/qatron.git
cd qatron/cli/qatron-cli

# Install in development mode
pip install -e .

# Or use Poetry
poetry install
poetry run qatron --version
```

### Configure CLI

```bash
# Login to QAtron instance
qatron login --url http://localhost:8000

# Enter your credentials when prompted
# Username: admin
# Password: (your password)

# Verify connection
qatron status
```

### CLI Commands

```bash
# Initialize a new project
qatron init my-project

# Run tests locally
qatron run smoke --env staging

# Check run status
qatron status <run-id>

# Download artifacts
qatron artifacts <run-id>

# List projects
qatron projects list

# View help
qatron --help
```

## Production Installation (Kubernetes)

### Prerequisites

1. Kubernetes cluster (1.24+)
2. Helm 3.8+
3. kubectl configured
4. Storage class for persistent volumes
5. Ingress controller (optional, for external access)

### Install with Helm

```bash
# Add QAtron Helm repository (when available)
helm repo add qatron https://charts.qatron.io
helm repo update

# Create namespace
kubectl create namespace qatron-system

# Install QAtron
helm install qatron qatron/qatron \
  --namespace qatron-system \
  --set controlPlane.replicas=2 \
  --set orchestrator.replicas=2 \
  --set board.replicas=2

# Or install from local chart
cd deployment/helm
helm install qatron ./qatron \
  --namespace qatron-system \
  --create-namespace
```

### Configuration

Create a values file for customization:

```yaml
# my-values.yaml
controlPlane:
  replicas: 3
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

orchestrator:
  replicas: 2
  celery:
    workers: 4

board:
  replicas: 2

postgresql:
  persistence:
    size: 50Gi
    storageClass: fast-ssd

minio:
  persistence:
    size: 100Gi
    storageClass: fast-ssd

ingress:
  enabled: true
  host: qatron.example.com
  tls:
    enabled: true
    secretName: qatron-tls
```

Install with custom values:

```bash
helm install qatron qatron/qatron \
  --namespace qatron-system \
  --values my-values.yaml
```

### Air-Gapped Installation

For air-gapped environments:

```bash
# 1. Export images (on machine with internet)
docker save qatron/control-plane:latest | gzip > control-plane.tar.gz
docker save qatron/orchestrator:latest | gzip > orchestrator.tar.gz
docker save qatron/worker:latest | gzip > worker.tar.gz
docker save qatron/board:latest | gzip > board.tar.gz

# 2. Transfer to air-gapped environment
# (use your preferred method)

# 3. Load images
docker load < control-plane.tar.gz
docker load < orchestrator.tar.gz
docker load < worker.tar.gz
docker load < board.tar.gz

# 4. Install with image overrides
helm install qatron ./qatron \
  --namespace qatron-system \
  --set imageRegistry=your-registry.local \
  --set controlPlane.image.repository=your-registry.local/qatron/control-plane
```

### Verify Installation

```bash
# Check pods
kubectl get pods -n qatron-system

# Check services
kubectl get svc -n qatron-system

# Check ingress
kubectl get ingress -n qatron-system

# View logs
kubectl logs -f deployment/control-plane -n qatron-system
```

## Post-Installation Configuration

### 1. Create Initial Organization

```bash
# Using API
curl -X POST http://localhost:8000/api/v1/organizations \
  -H "Content-Type: application/json" \
  -d '{"name": "My Organization"}'
```

### 2. Create Admin User

```bash
# Register admin user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecurePassword123!",
    "organization_id": 1
  }'
```

### 3. Assign Admin Role

```bash
# Login to get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=SecurePassword123!" \
  | jq -r '.access_token')

# Assign admin role (using API or database)
# This typically requires direct database access or admin API
```

### 4. Configure S3/MinIO Bucket

```bash
# Access MinIO console
open http://localhost:9001

# Login with minioadmin/minioadmin
# Create bucket: qatron-artifacts
# Set retention policy: 90 days
```

### 5. Configure Selenium Grid

The Selenium Grid is automatically configured. To add more nodes:

```bash
# For Docker Compose, scale selenium nodes
docker compose up -d --scale selenium-node=3

# For Kubernetes, update deployment
kubectl scale deployment selenium-node --replicas=3 -n qatron-system
```

## Verification

### 1. Health Checks

```bash
# Control Plane
curl http://localhost:8000/healthz

# Orchestrator
curl http://localhost:8001/healthz

# Board
curl http://localhost:3000/healthz
```

### 2. API Access

```bash
# Test API (should return 401 without auth)
curl http://localhost:8000/api/v1/projects

# Login and test
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=SecurePassword123!" \
  | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/projects
```

### 3. UI Access

Open browser and navigate to:
- **QAtron Board**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001

### 4. Create Test Project

```bash
# Using CLI
qatron init demo-project
cd demo-project

# Or using API
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Project",
    "repo_url": "https://github.com/example/demo-repo",
    "repo_auth_method": "token",
    "organization_id": 1
  }'
```

## Troubleshooting

### Connection Refused / Invalid Response (API & Board)

**localhost:8000 — "This page isn't working" or "Invalid response" / ERR_CONNECTION_REFUSED**  
The Control Plane API is not running or not reachable. Start it (and its dependencies):

```bash
cd deployment/docker-compose
docker compose up -d postgres redis control-plane board
```

Then verify:

```bash
curl -s http://localhost:8000/healthz
# Should return: {"status":"healthy"}
```

**localhost:5173 — ERR_CONNECTION_REFUSED**  
Port 5173 is the Board’s **dev server**. Either:

- **Use the Docker Board** (no dev server): open **http://localhost:3000** after starting the stack above, or  
- **Run the Board in dev**: from the repo root, `cd services/board && npm install && npm run dev`, then open http://localhost:5173 (ensure the API is running on port 8000 so the UI can log in and trigger runs).

**Summary**

| What you need | URL | How to get it |
|---------------|-----|----------------|
| Board (UI)    | http://localhost:3000 | `docker compose up -d postgres redis control-plane board` then open 3000 |
| Control Plane API | http://localhost:8000 | Same as above; health: http://localhost:8000/healthz |
| Board in dev  | http://localhost:5173 | `cd services/board && npm run dev` (API on 8000 must be running) |

### Services Not Starting

```bash
# Check Docker Compose logs
docker compose logs

# Check specific service
docker compose logs control-plane

# Restart service
docker compose restart control-plane
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check connection
docker compose exec postgres psql -U qatron -d qatron -c "SELECT 1;"

# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d postgres
# Run migrations
docker compose exec control-plane alembic upgrade head
```

### Port Conflicts

If ports are already in use:

```bash
# Edit docker-compose.yml to change ports
# Or stop conflicting services
lsof -i :8000  # Find process using port 8000
kill <PID>     # Kill the process
```

### Worker Not Executing Tests

```bash
# Check worker logs
docker compose logs worker

# Check RabbitMQ queue
docker compose exec rabbitmq rabbitmqctl list_queues

# Check orchestrator logs
docker compose logs orchestrator
```

### Selenium Grid Not Ready

The stack starts both the Selenium Hub and a Chrome node; the install script waits until the grid reports ready. If E2E tests fail with "connection refused" or "grid not ready":

```bash
# Check grid status (ready should be true when a node is registered)
curl -s http://localhost:4444/status | head -20

# Ensure both hub and node are running
docker compose ps selenium-hub selenium-node

# Restart Selenium services (node waits for hub to be healthy)
docker compose restart selenium-hub
docker compose up -d selenium-node

# View node logs if the node exits
docker compose logs selenium-node
```

Use `SELENIUM_GRID_URL=http://localhost:4444/wd/hub` when running E2E tests from the host.

### MinIO Access Issues

```bash
# Check MinIO is running
docker compose ps minio

# Verify bucket exists
docker compose exec minio mc ls minio/qatron-artifacts

# Reset MinIO (WARNING: deletes all data)
docker compose down -v minio
docker compose up -d minio
```

### Kubernetes Issues

```bash
# Check pod status
kubectl describe pod <pod-name> -n qatron-system

# Check events
kubectl get events -n qatron-system --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n qatron-system

# Restart deployment
kubectl rollout restart deployment/control-plane -n qatron-system
```

### Getting Help

- **Documentation**: https://docs.qatron.io
- **GitHub Issues**: https://github.com/qatron/qatron/issues
- **Community Forum**: https://forum.qatron.io
- **Slack**: https://qatron.slack.com

## Next Steps

After installation:

1. **Read the User Guide**: [docs/USER_GUIDE.md](USER_GUIDE.md)
2. **Set up your first project**: [docs/GETTING_STARTED.md](GETTING_STARTED.md)
3. **Configure CI/CD integration**: [docs/CI_CD.md](CI_CD.md)
4. **Explore the API**: http://localhost:8000/docs

## Uninstallation

### Docker Compose

```bash
# Stop and remove containers
docker compose down

# Remove volumes (WARNING: deletes all data)
docker compose down -v

# Remove images
docker compose down --rmi all
```

### Kubernetes

```bash
# Uninstall Helm release
helm uninstall qatron -n qatron-system

# Remove namespace (WARNING: deletes all data)
kubectl delete namespace qatron-system

# Remove persistent volumes (if not using storage class retention)
kubectl delete pvc -n qatron-system --all
```
