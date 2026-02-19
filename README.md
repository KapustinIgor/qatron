# QAtron

A cloud-agnostic, open-source QA automation platform that unifies test execution orchestration, BDD-first test specifications, reporting, analytics, and infrastructure visibility.

## Architecture

QAtron consists of:

- **QAtron Board**: React-based UI for managing tests, runs, and infrastructure
- **Control Plane API**: FastAPI backend for managing projects, runs, and metadata
- **Orchestrator**: Celery-based service for job orchestration and sharding
- **Workers**: Stateless test executors that run tests in isolated containers
- **Python Framework**: pytest + pytest-bdd based automation framework
- **Reporting**: Allure-based reporting with metrics aggregation
- **Test Data Manager**: Dataset registry and validation integration

## Quick Start

### First-time setup (required)

After cloning, run the install script **once**. It starts the Control Plane API and Board so http://localhost:8000 and http://localhost:3000 work. Without this, you’ll see “connection refused” or “invalid response.”

```bash
# From repo root
./scripts/install.sh
# or
./deployment/docker-compose/install.sh
```

This will start the full stack including:
- Control Plane API (http://localhost:8000)
- Orchestrator (http://localhost:8001)
- QAtron Board (http://localhost:3000)
- PostgreSQL, RabbitMQ, Redis, MinIO
- Selenium Grid
- Prometheus + Grafana + Loki

**Default login:** username `admin`, password `admin`

### CLI Installation

```bash
pipx install qatron
```

### Initialize a Project

```bash
qatron init my-project
cd my-project
qatron run e2e --env staging
```

## Installation

For detailed installation instructions, see:
- **[Installation Guide](docs/INSTALLATION.md)** - Complete installation guide
- **[Quick Install](INSTALL.md)** - Quick reference

## Project Structure

```
qatron/
├── services/          # Microservices
├── framework/         # Python automation framework
├── deployment/        # Docker Compose and Helm charts
├── cli/               # CLI tool
├── shared/            # Shared models and utilities
├── docs/              # Documentation
└── scripts/           # Build and deployment scripts
```

## Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Complete installation instructions
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive guide covering all testing scenarios and integrations
- **[Phase 2 Features](docs/PHASE2.md)** - Roadmap for advanced features

See [docs/](docs/) for all documentation.

## License

Open source (TBD)
