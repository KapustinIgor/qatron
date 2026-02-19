# Phase 2 Features

This document outlines Phase 2 features for QAtron, including Keycloak SSO integration and advanced features.

## Keycloak SSO Integration

### Overview

Phase 2 introduces Keycloak as the default authentication provider, replacing basic username/password authentication.

### Implementation

1. **Keycloak Deployment**
   - Deploy Keycloak via Helm chart
   - Configure realm and clients
   - Set up OIDC provider

2. **Authentication Integration**
   - Replace basic auth with OIDC
   - JWT token validation
   - User provisioning from Keycloak
   - Session management

3. **Migration Path**
   - Support both auth methods during transition
   - Migrate existing users to Keycloak
   - Update all services to use OIDC

## Advanced Test Data Management

### Features

- Automated dataset refresh triggers
- Scheduled dataset refreshes
- Webhook-based triggers
- CI integration for data updates
- Enhanced validation with multiple rule types
- Validation history tracking
- Alerting on validation failures

## Flakiness Quarantine Workflow

### Features

- Quarantine status display in UI
- Manual quarantine/unquarantine
- Bulk operations
- Quarantine history
- Smart retry logic:
  - Automatic retry for flaky candidates
  - Infrastructure error retries
  - Configurable retry policies per suite

## Advanced Infrastructure Management

### Features

- Real-time worker metrics
- Grid session management
- Queue analytics
- Capacity planning
- UI-based worker pool scaling
- Auto-scaling policies
- Resource optimization recommendations

## Namespace-per-Project (Optional)

### Features

- Project-to-namespace mapping
- Resource isolation
- Cross-namespace visibility (for admins)

## Implementation Status

Phase 2 features are planned but not yet implemented. This document serves as a roadmap for future development.
