# Quick Installation Guide

For detailed installation instructions, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

## Quick Start (Local)

```bash
# Clone repository
git clone https://github.com/qatron/qatron.git
cd qatron

# Run installation script
./deployment/docker-compose/install.sh
```

This will start all QAtron services. Access the UI at http://localhost:3000

## Install CLI

```bash
pipx install qatron
```

## Production (Kubernetes)

```bash
helm install qatron ./deployment/helm/qatron \
  --namespace qatron-system \
  --create-namespace
```

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for complete instructions.
