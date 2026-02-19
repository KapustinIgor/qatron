# QAtron Helm Chart

Helm chart for deploying QAtron QA automation platform on Kubernetes.

## Installation

```bash
# Add dependencies
helm dependency update

# Install QAtron
helm install qatron . --namespace qatron-system --create-namespace

# Or with custom values
helm install qatron . --namespace qatron-system --create-namespace -f my-values.yaml
```

## Configuration

See `values.yaml` for all configurable options.

## Uninstallation

```bash
helm uninstall qatron --namespace qatron-system
```
