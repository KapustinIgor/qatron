# QAtron Product Requirements Document (PRD)

**Version:** 1.1  
**Last Updated:** February 2025  
**Status:** Active Development (MVP Phase)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Success Criteria](#3-goals--success-criteria)
4. [User Personas](#4-user-personas)
5. [Product Overview](#5-product-overview)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Tenancy Model](#8-tenancy-model)
9. [Data Model](#9-data-model)
10. [System Architecture](#10-system-architecture)
11. [Execution Model](#11-execution-model)
12. [Sharding Model](#12-sharding-model)
13. [Artifact Lifecycle Policy](#13-artifact-lifecycle-policy)
14. [BDD Feature Ingestion](#14-bdd-feature-ingestion)
15. [Coverage Requirements](#15-coverage-requirements)
16. [API Overview](#16-api-overview)
17. [User Flows](#17-user-flows)
18. [User Interface](#18-user-interface)
19. [Technology Stack](#19-technology-stack)
20. [Deployment & Operations](#20-deployment--operations)
21. [MVP Acceptance Criteria](#21-mvp-acceptance-criteria)
22. [Phase 2 Roadmap](#22-phase-2-roadmap)
23. [Out of Scope](#23-out-of-scope)
24. [Appendix](#24-appendix)

---

## 1. Executive Summary

**QAtron** is a cloud-agnostic, open-source QA automation platform that unifies test execution orchestration, BDD-first test specifications, reporting, analytics, and infrastructure visibility. It provides a single platform for teams to manage test projects, execute tests at scale (unit, contract, integration, and E2E), store and validate test data, and gain insights through Allure-based reporting and metrics.

The platform consists of a web-based Board (UI), REST APIs, CLI tools, and a Python-based testing framework. It supports deployment via Docker Compose (local/development) and Kubernetes/Helm (production), and integrates with major CI/CD systems including GitHub Actions, GitLab CI, Jenkins, CircleCI, and Azure DevOps.

---

## 2. Problem Statement

### Current Challenges

- **Fragmented Tools:** QA teams often use disjointed tools for test authoring, execution, reporting, and infrastructure management.
- **Limited Visibility:** Lack of centralized visibility into test runs, pass/fail trends, flaky tests, and infrastructure health.
- **CI/CD Complexity:** Integrating tests with CI/CD pipelines requires custom scripting and maintenance across multiple platforms.
- **Test Data Management:** Test data is frequently hardcoded or scattered, leading to brittle tests and maintenance burden.
- **Scalability:** Running large test suites (e.g., regression) efficiently requires manual sharding and parallelization setup.

### Target Solution

QAtron addresses these challenges by providing:

- A unified platform for projects, runs, environments, and suites
- BDD-first test authoring with Gherkin and pytest-bdd
- Centralized orchestration with Celery and Selenium Grid for parallel execution
- Test data registry with validation via Great Expectations
- Allure-based reporting with metrics aggregation
- REST API and CLI for programmatic and CI/CD integration

---

## 3. Goals & Success Criteria

### Primary Goals

| Goal | Description |
|------|-------------|
| **Unified Orchestration** | Single platform to trigger, monitor, and manage test runs across projects and environments |
| **BDD-First** | Gherkin feature files as the primary specification format with pytest-bdd execution |
| **Multi-Layer Testing** | Support unit, contract, integration, and E2E tests with consistent tooling |
| **Cloud Agnostic** | Deploy on-premises, in any cloud, or hybrid without vendor lock-in |
| **CI/CD Integration** | First-class support for GitHub Actions, GitLab CI, Jenkins, and others via API and CLI |

### Success Criteria

- Teams can create a project and run smoke tests within 30 minutes of installation
- API and CLI support 100% of core workflows (create run, list runs, get status, download artifacts)
- Test execution supports parallel sharding with configurable worker count
- Reporting service produces Allure reports with pass/fail metrics
- Platform runs locally via Docker Compose and in production via Kubernetes/Helm

---

## 4. User Personas

### 4.1 QA Engineer

- Writes and maintains BDD feature files and step definitions
- Runs tests locally and via CI
- Reviews test results and Allure reports
- Manages test data and fixtures

### 4.2 DevOps / Platform Engineer

- Deploys and operates QAtron (Docker Compose or Kubernetes)
- Integrates QAtron with CI/CD pipelines
- Monitors infrastructure (Selenium Grid, workers) via Grafana and Prometheus

### 4.3 Developer

- Runs tests locally via CLI
- Triggers runs via API from local scripts or IDE
- Consumes run status and artifacts in CI pipelines

### 4.4 QA Lead / Manager

- Views dashboards for run history, pass rates, and trends
- Manages projects, environments, and suites
- Configures organization-level settings and roles

---

## 5. Product Overview

### 5.1 Core Components

| Component | Description |
|-----------|-------------|
| **QAtron Board** | React-based web UI for projects, runs, infrastructure, and configuration |
| **Control Plane API** | FastAPI backend for projects, runs, auth, and metadata |
| **Orchestrator** | Celery-based service for job scheduling and sharding |
| **Orchestrator Worker** | Celery workers that execute test jobs |
| **Workers** | Stateless test executors (pytest) in isolated environments |
| **Reporting Service** | Allure report generation and metrics aggregation |
| **Test Data Manager** | Dataset registry and validation (Great Expectations) |
| **CLI** | Command-line tool for auth, init, projects, and runs |
| **Python Framework** | pytest + pytest-bdd + Selenium + Allure for test authoring |

### 5.2 Key Capabilities

- **Project Management:** Create projects with repo URL and auth (token/SSH)
- **Environment Configuration:** Define dev, staging, production with base URLs and datasets
- **Suite Configuration:** Smoke, regression, integration, contract, unit with shards, retries, timeouts
- **Run Execution:** Trigger runs via UI, API, or CLI; support branch, commit, triggered_by
- **Artifacts:** Allure reports, screenshots, logs stored in S3/MinIO with configurable retention
- **Infrastructure:** Selenium Grid for browser automation; worker registration and status
- **Tenancy:** Single-tenant model (one organization per installation) with RBAC

---

## 6. Functional Requirements

### 6.1 Authentication & Authorization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AUTH-01 | Support username/password login with JWT tokens (form-urlencoded for OAuth2PasswordRequestForm compatibility) | Must Have |
| FR-AUTH-02 | Support user registration with email, username, password | Must Have |
| FR-AUTH-03 | Default admin user (admin/admin) on first install (local/dev only) | Must Have |
| FR-AUTH-04 | Role-based access: admin, user, viewer | Must Have |
| FR-AUTH-05 | Service tokens for CI/CD (scoped to organization/project, revocable, long-lived) | Must Have |
| FR-AUTH-06 | Keycloak SSO integration (Phase 2) | Should Have |

### 6.2 Project Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PRJ-01 | Create project with name, description, repo URL, auth method | Must Have |
| FR-PRJ-02 | List projects filtered by organization | Must Have |
| FR-PRJ-03 | Update and delete projects | Must Have |
| FR-PRJ-04 | Associate project with organization | Must Have |

### 6.3 Run Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-RUN-01 | Create run with project_id, suite_id, environment_id, branch, commit | Must Have |
| FR-RUN-02 | List runs with filters (project, suite, environment, status, branch) | Must Have |
| FR-RUN-03 | Get run by ID with status, timestamps, counts | Must Have |
| FR-RUN-04 | Update run status (queued, running, completed, failed, cancelled) | Must Have |
| FR-RUN-05 | Store run artifacts (Allure, screenshots, logs) in S3/MinIO | Must Have |

### 6.4 Test Execution

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TEST-01 | Celery worker executes pytest directly in its container/pod | Must Have |
| FR-TEST-02 | Support unit, contract, integration, e2e layers with tags | Must Have |
| FR-TEST-03 | Parallel execution via sharding (pytest-xdist with --dist=loadfile or --dist=loadscope) | Must Have |
| FR-TEST-04 | Selenium Grid integration for browser tests | Must Have |
| FR-TEST-05 | Retry failed tests (configurable per suite) | Should Have |
| FR-TEST-06 | Flakiness quarantine workflow (Phase 2) | Should Have |
| FR-TEST-07 | Support run statuses: queued, provisioning, running, reporting, completed, failed, partial_failed, timed_out, infra_failed, cancelled | Must Have |
| FR-TEST-08 | Aggregate shard results into run-level counts and status | Must Have |

### 6.5 Reporting

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-RPT-01 | Generate Allure reports from run results (static HTML generated post-run) | Must Have |
| FR-RPT-02 | Aggregate pass/fail/skip counts | Must Have |
| FR-RPT-03 | Serve reports via API and link from Board | Must Have |
| FR-RPT-04 | Metrics endpoint for Prometheus/Grafana | Must Have |
| FR-RPT-05 | Store Cobertura XML and HTML coverage reports | Must Have |
| FR-RPT-06 | Combine coverage from multiple shards using pytest-cov combine | Must Have |
| FR-RPT-07 | Support coverage thresholds per suite/layer (enforced post-run) | Should Have |

### 6.6 Test Data Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-DATA-01 | Register datasets with versioning | Must Have |
| FR-DATA-02 | Validate datasets with Great Expectations | Must Have |
| FR-DATA-03 | Pin dataset version to run (recorded on Run creation) | Must Have |
| FR-DATA-04 | Suites can require dataset validation pass before run begins | Should Have |
| FR-DATA-05 | Run fails fast if required dataset validation fails | Should Have |
| FR-DATA-06 | Automated dataset refresh triggers (Phase 2) | Could Have |

### 6.7 Infrastructure

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-INF-01 | Register infrastructure resources (workers, grids) | Must Have |
| FR-INF-02 | Track status and last heartbeat | Must Have |
| FR-INF-03 | Real-time worker metrics and capacity planning (Phase 2) | Could Have |

### 6.8 CLI

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CLI-01 | Login and store token | Must Have |
| FR-CLI-02 | Initialize project structure (qatron init) | Must Have |
| FR-CLI-03 | Trigger run (qatron run --suite X --env Y) | Must Have |
| FR-CLI-04 | Get run status and download artifacts | Must Have |
| FR-CLI-05 | Manage projects (create, list) | Should Have |

### 6.9 BDD Feature Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-BDD-01 | Index feature files on project registration (scan repo, parse Gherkin) | Must Have |
| FR-BDD-02 | Re-index features on each run (detect changes) | Must Have |
| FR-BDD-03 | Generate stable scenario IDs (path + line range + scenario name hash) | Must Have |
| FR-BDD-04 | Map Allure test results to Feature/Scenario entities | Must Have |
| FR-BDD-05 | Display scenario coverage in Board even without execution | Should Have |

### 6.10 Secrets Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SEC-01 | Repository tokens/SSH keys stored only in K8s Secrets (production) or .env (local) | Must Have |
| FR-SEC-02 | Secrets never stored in database as plaintext | Must Have |
| FR-SEC-03 | Secrets injected into workers at runtime via environment variables | Must Have |
| FR-SEC-04 | Project references secret by name/ref, not value | Must Have |

### 6.11 Audit Logging

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AUD-01 | Log user login/logout events | Must Have |
| FR-AUD-02 | Log run trigger events (who, when, project, suite) | Must Have |
| FR-AUD-03 | Log configuration changes (project create/update/delete, suite changes) | Must Have |
| FR-AUD-04 | Log secret updates (reference changes, not values) | Must Have |
| FR-AUD-05 | Log role assignment changes | Must Have |
| FR-AUD-06 | Audit log queryable via API with filters (user, action, date range) | Should Have |

---

## 7. Non-Functional Requirements

### 7.1 Performance

| ID | Requirement |
|----|-------------|
| NFR-PERF-01 | API health check response < 200ms |
| NFR-PERF-02 | Support at least 4 parallel test shards per run |
| NFR-PERF-03 | Dashboard load < 3 seconds for up to 100 projects |

### 7.2 Scalability

| ID | Requirement |
|----|-------------|
| NFR-SCALE-01 | Horizontal scaling of Celery workers |
| NFR-SCALE-02 | PostgreSQL for metadata; S3/MinIO for artifacts |
| NFR-SCALE-03 | Selenium Grid scales with node count |

### 7.3 Security

| ID | Requirement |
|----|-------------|
| NFR-SEC-01 | Passwords hashed with bcrypt |
| NFR-SEC-02 | JWT tokens with configurable expiry (default 30 minutes) |
| NFR-SEC-03 | CORS configuration for Board origins (localhost:3000, 127.0.0.1:3000) |
| NFR-SEC-04 | Default credentials (admin/admin) MUST be changed in production via install script prompt or manual config |
| NFR-SEC-05 | Service tokens have no expiry (or very long expiry) for CI use |
| NFR-SEC-06 | All API endpoints require authentication except /healthz and /readyz |

### 7.4 Availability

| ID | Requirement |
|----|-------------|
| NFR-AVAIL-01 | Health checks for all services |
| NFR-AVAIL-02 | Graceful degradation if reporting service unavailable |

### 7.5 Observability

| ID | Requirement |
|----|-------------|
| NFR-OBS-01 | Prometheus metrics from Control Plane, Orchestrator |
| NFR-OBS-02 | Grafana dashboards for metrics |
| NFR-OBS-03 | Loki for log aggregation (optional) |

---

## 8. Tenancy Model

### 8.1 Model Definition

**QAtron uses a single-tenant model per installation:**

- **One installation = One Organization**
- Each installation has exactly one "Default Organization" created on first startup
- All users, projects, runs belong to this single organization
- No cross-organization isolation needed (simplifies MVP)

**Rationale:** This is the common pattern for OSS self-hosted tools. Multi-tenant support (multiple orgs per install) is deferred to Phase 2.

### 8.2 Storage Isolation

| Resource | Isolation Strategy |
|----------|-------------------|
| **Database** | Row-level: All queries filter by `organization_id` (enforced in repositories) |
| **S3/MinIO** | Prefix-based: `{organization_id}/projects/{project_id}/runs/{run_id}/` |
| **API Authorization** | Users can only access resources in their organization (enforced in endpoints) |

### 8.3 RBAC Enforcement Points

| Action | Enforcement |
|--------|-------------|
| List projects | Filter by `current_user.organization_id` |
| Create project | Assign to `current_user.organization_id` |
| View runs | Filter by project's `organization_id` |
| Create run | Verify project belongs to user's organization |
| Update/delete project | Require `admin` role AND verify organization match |

### 8.4 Future Multi-Tenancy (Phase 2)

If multi-tenancy is added:
- Multiple organizations per installation
- Optional namespace-per-project in Kubernetes
- Cross-organization visibility for admins
- Organization-level admin boundaries

---

## 9. Data Model

### 9.1 Core Entities

| Entity | Description |
|--------|-------------|
| **Organization** | Top-level tenant; has users and projects |
| **User** | Authenticated user with email, username, roles |
| **Role** | admin, user, viewer |
| **Project** | Test project with repo URL, auth method |
| **Environment** | Deployment target (dev, staging, prod) with base URLs |
| **Suite** | Test suite definition (smoke, regression) with layer, tags, shards |
| **Run** | Single test execution with status, timestamps, counts |
| **RunArtifact** | Reference to S3 object (Allure, screenshot, log) |
| **Feature, Scenario, Step** | BDD feature/scenario/step metadata |
| **Dataset, DatasetVersion** | Test data with versioning |
| **InfrastructureResource** | Worker or grid with status, metadata |
| **AuditLog** | Audit trail for key actions |

### 9.2 Run Status Model

**Status Enum:**
- `queued` - Run created, waiting for worker
- `provisioning` - Worker acquiring resources (container/pod startup)
- `running` - Tests executing
- `reporting` - Tests complete, generating Allure report
- `completed` - All shards passed, report ready
- `failed` - All shards failed
- `partial_failed` - Some shards passed, some failed
- `timed_out` - Run exceeded suite timeout
- `infra_failed` - Infrastructure error (worker crash, grid unavailable)
- `cancelled` - User/admin cancelled run

**Status Flow:**
```
queued → provisioning → running → reporting → completed
                                      ↓
                                   failed / partial_failed / timed_out / infra_failed

(any state) → cancelled
```

**Shard Aggregation Rules:**
- Run status = `completed` if all shards passed
- Run status = `failed` if all shards failed
- Run status = `partial_failed` if mixed results
- Run status = `infra_failed` if worker/grid unavailable
- Run status = `timed_out` if any shard exceeds timeout

---

## 10. System Architecture

### 10.1 High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   QAtron Board  │────▶│ Control Plane    │────▶│   PostgreSQL    │
│   (React/nginx) │     │ (FastAPI)        │     │                 │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
        │                        │
        │                        │ Celery
        │                        ▼
        │               ┌──────────────────┐     ┌─────────────────┐
        │               │   Orchestrator   │────▶│    RabbitMQ     │
        │               │   (FastAPI+      │     │                 │
        │               │    Celery)       │     └─────────────────┘
        │               └────────┬─────────┘
        │                        │
        │                        ▼
        │               ┌──────────────────┐     ┌─────────────────┐
        │               │ Orchestrator     │     │     Redis       │
        │               │ Worker (Celery)  │     │  (result store) │
        │               └────────┬─────────┘     └─────────────────┘
        │                        │
        │                        ▼
        │               ┌──────────────────┐     ┌─────────────────┐
        │               │   Test Workers   │     │  Selenium Grid  │
        │               │   (pytest)       │────▶│                 │
        │               └────────┬─────────┘     └─────────────────┘
        │                        │
        │                        ▼
        │               ┌──────────────────┐
        │               │  Reporting       │     ┌─────────────────┐
        │               │  (Allure)        │────▶│ MinIO (S3)      │
        │               └──────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐     ┌──────────────────┐
│   Prometheus    │────▶│     Grafana      │
│   + Loki        │     │                  │
└─────────────────┘     └──────────────────┘
```

### 10.2 Service Ports

**Note:** Board (3000) and Grafana (3001) use different ports to avoid conflicts. In Docker Compose, all services are accessible on localhost with their respective ports.

| Service | Port |
|---------|------|
| QAtron Board | 3000 |
| Control Plane API | 8000 |
| Orchestrator | 8001 |
| Reporting | 8002 |
| Data Manager | 8003 |
| PostgreSQL | 5432 |
| RabbitMQ | 5672, 15672 (management) |
| Redis | 6379 |
| MinIO | 9000, 9001 (console) |
| Selenium Hub | 4444 |
| Prometheus | 9090 |
| Grafana | 3001 |
| Loki | 3100 |

---

## 11. Execution Model

### 11.1 Model Definition

**QAtron uses Model A: Celery Worker Executes pytest Directly**

- **Orchestrator Worker (Celery)** receives run job from RabbitMQ
- **Celery worker** clones repository, installs dependencies, executes pytest with pytest-xdist
- **pytest-xdist** spawns subprocess workers within the same Celery worker container/pod
- **Results** (Allure XML, coverage, logs) uploaded to S3/MinIO
- **Celery worker** reports completion back to Orchestrator

**Not Model B:** QAtron does NOT schedule separate Kubernetes Jobs/Pods per run or shard in MVP.

### 11.2 Execution Flow

```
1. User/CI triggers run via API
2. Control Plane creates Run record (status: queued)
3. Control Plane enqueues Celery task to Orchestrator
4. Orchestrator Worker picks up task
5. Worker: Clone repo, install deps, run pytest with sharding
6. Worker: Upload artifacts (Allure XML, coverage, logs) to S3
7. Worker: Update Run status (running → reporting → completed/failed)
8. Reporting Service: Generate Allure HTML from XML (async)
9. Run status: completed
```

### 11.3 Worker Isolation

- Each Celery worker runs in its own container/pod
- Workers are stateless (no shared filesystem)
- Repository cloned fresh per run
- Dependencies installed per run (or cached in image)
- Selenium Grid used for browser tests (shared resource)

---

## 12. Sharding Model

### 12.1 Sharding Strategy

**Phase 1 (MVP): Simple File-Based Sharding**

- Use `pytest-xdist` with `--dist=loadfile` (distribute by test file)
- Alternative: `--dist=loadscope` (distribute by pytest scope/class)
- Shard count configured per suite (e.g., `shards: 4`)

**Example:**
```bash
pytest --dist=loadfile -n 4  # 4 shards, distribute by file
```

### 12.2 Shard Representation

**Data Model:**
- `Run` entity stores aggregate counts (total_tests, passed_tests, etc.)
- Shard-level results stored in `run_metadata` JSON field (Phase 1)
- Future: `RunShard` entity for explicit shard tracking (Phase 2)

**Shard Metadata Structure:**
```json
{
  "shards": [
    {"shard_id": 0, "status": "passed", "tests": 25, "duration": 120},
    {"shard_id": 1, "status": "failed", "tests": 23, "duration": 95}
  ],
  "shard_count": 4
}
```

### 12.3 Re-running Failed Tests

- Option 1: Re-run entire suite (current)
- Option 2: Re-run only failed tests via `pytest --lf` (last failed) - Phase 2
- Option 3: Re-run specific shards - Phase 2

### 12.4 Shard Aggregation

- Worker aggregates shard results before updating Run
- Run status determined by shard outcomes (see Run Status Model)
- Test counts summed across shards
- Duration = max(shard durations)

---

## 13. Artifact Lifecycle Policy

### 13.1 Retention Policy

| Environment | Retention Period | Rationale |
|-------------|------------------|-----------|
| **Production** | 180 days | Compliance, historical analysis |
| **Staging** | 90 days | Shorter retention for non-prod |
| **Development** | 30 days | Minimal retention for dev/test |

**Configuration:**
- Retention period configurable per environment
- Defaults applied if not specified
- Retention calculated from `run.completed_at` timestamp

### 13.2 Cleanup Mechanism

- **Cleanup Job:** Scheduled Celery task (daily at 2 AM UTC)
- **Deletion Semantics:**
  - Delete S3 objects older than retention period
  - Delete `RunArtifact` records for deleted objects
  - Update `Run` records (set artifacts_deleted flag)
  - Preserve Run metadata (counts, status, timestamps)

### 13.3 Report Generation

**Allure Reports:**
- **Generation:** Static HTML generated post-run by Reporting Service
- **Storage:** Generated HTML stored in S3 (not regenerated on-demand)
- **Location:** `{org_id}/projects/{project_id}/runs/{run_id}/allure-report/index.html`
- **Regeneration:** Only if Allure XML changes (re-run with same run_id)

**Coverage Reports:**
- **Cobertura XML:** Generated by pytest-cov, stored in S3
- **HTML Coverage:** Generated from XML, stored in S3
- **Combination:** pytest-cov combine merges shard coverage files

### 13.4 Artifact Versioning

- Artifacts are immutable (never overwritten)
- S3 keys include run_id (unique per run)
- No versioning within a run (latest artifact wins if regenerated)

---

## 14. BDD Feature Ingestion

### 14.1 Feature Discovery

**On Project Registration:**
1. Clone repository (using project's auth credentials)
2. Scan for `.feature` files (Gherkin format)
3. Parse features using `gherkin` parser
4. Extract: Feature name, scenarios, steps
5. Store in `Feature`, `Scenario`, `Step` tables
6. Generate stable IDs (see below)

**On Each Run:**
1. Re-scan repository (detect changes)
2. Compare with stored features
3. Update/insert new features/scenarios
4. Mark deleted scenarios as inactive (don't delete)

### 14.2 Stable Scenario Identifiers

**Format:** `{feature_path}:{line_start}:{line_end}:{scenario_name_hash}`

**Example:**
- Path: `features/checkout.feature`
- Lines: 15-25
- Name: "Successful checkout"
- Hash: SHA256("Successful checkout")[:8]
- ID: `features/checkout.feature:15:25:a1b2c3d4`

**Rationale:** Stable across commits (unless scenario moves significantly)

### 14.3 Allure-to-Scenario Mapping

- Allure test names include scenario context
- Match Allure test name to Scenario.name or Scenario.steps
- Store mapping in `run_metadata` JSON
- Display scenario coverage in Board UI

### 14.4 Feature File Changes

- **New scenarios:** Added to database
- **Modified scenarios:** Updated (preserve ID if possible)
- **Deleted scenarios:** Marked inactive (preserve history)
- **Run history:** Links to scenario version at time of run

---

## 15. Coverage Requirements

### 15.1 Coverage Collection

| Requirement | Description |
|-------------|-------------|
| **Tool** | pytest-cov (required dependency) |
| **Format** | Cobertura XML + HTML |
| **Scope** | Unit and integration tests (e2e coverage optional) |
| **Sharding** | Each shard generates coverage; combine post-run |

### 15.2 Coverage Combination

**Process:**
1. Each pytest-xdist worker generates `.coverage` file
2. Worker uploads `.coverage` to S3
3. Reporting Service runs `coverage combine` to merge
4. Generate Cobertura XML: `coverage xml -o coverage.xml`
5. Generate HTML: `coverage html -d htmlcov`
6. Store both in S3

### 15.3 Coverage Thresholds

**Configuration (per suite):**
```yaml
suites:
  regression:
    coverage_threshold: 80  # Fail if coverage < 80%
    coverage_layer: integration  # Only check integration layer
```

**Enforcement:**
- Threshold checked post-run (after combination)
- Run status set to `failed` if threshold not met
- Coverage percentage stored in `run_metadata`

### 15.4 Coverage Display

- Coverage percentage shown in Run detail page
- Coverage trend chart in Dashboard
- Coverage report HTML linked from Run detail
- Per-file coverage drill-down (Phase 2)

---

## 16. API Overview

### 16.1 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (form-urlencoded for OAuth2PasswordRequestForm), returns JWT |
| GET | `/api/v1/auth/me` | Get current authenticated user info |
| POST | `/api/v1/auth/service-tokens` | Create service token for CI (admin only) |
| DELETE | `/api/v1/auth/service-tokens/{id}` | Revoke service token |

### 16.2 Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects` | List projects |
| POST | `/api/v1/projects` | Create project |
| GET | `/api/v1/projects/{id}` | Get project |
| PUT | `/api/v1/projects/{id}` | Update project |
| DELETE | `/api/v1/projects/{id}` | Delete project |

### 16.3 Runs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/runs` | List runs (filterable) |
| POST | `/api/v1/runs` | Create run |
| GET | `/api/v1/runs/{id}` | Get run |
| PUT | `/api/v1/runs/{id}` | Update run |

### 16.4 Audit Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audit-logs` | List audit logs (filterable by user, action, date range) |

### 16.5 Health & Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Liveness |
| GET | `/readyz` | Readiness |
| GET | `/metrics` | Prometheus metrics |

---

## 17. User Flows

### 17.1 First-Time Setup

1. Run `./deployment/docker-compose/install.sh`
2. Access Board at http://localhost:3000
3. Login with admin/admin
4. Install CLI: `pipx install qatron`
5. Initialize project: `qatron init my-project`

### 17.2 Trigger Run via CLI

1. `qatron login --url http://localhost:8000`
2. `qatron run --suite smoke --env staging`
3. CLI triggers run via API, returns run ID
4. Poll or wait for completion

### 17.3 Trigger Run via CI

**Option A: Service Token (Recommended)**
1. Create service token via API: `POST /api/v1/auth/service-tokens` (admin only)
2. Store `QATRON_API_URL`, `QATRON_SERVICE_TOKEN` as CI secrets
3. POST to `/api/v1/runs` with `Authorization: Bearer {service_token}`
4. Poll GET `/api/v1/runs/{id}` until status is completed, failed, or partial_failed
5. Download artifacts if needed

**Option B: User Credentials (Not Recommended)**
1. Store `QATRON_API_URL`, `QATRON_USERNAME`, `QATRON_PASSWORD` as CI secrets
2. Login: `POST /api/v1/auth/login` to get JWT
3. Use JWT for subsequent API calls
4. Poll until completion

### 17.4 View Results in Board

1. Login to Board
2. Navigate to Runs
3. Filter by project, status
4. Open run detail to see status, counts, artifacts
5. Open Allure report link (from Reporting service)

---

## 18. User Interface

### 18.1 Board Pages

| Route | Description |
|-------|-------------|
| `/login` | Sign in |
| `/` | Dashboard |
| `/runs` | List runs, filters |
| `/runs/:runId` | Run detail |
| `/projects` | List/create projects |
| `/infrastructure` | Workers, grids |
| `/configuration` | Settings |

### 18.2 Key UI Features

- Dashboard with run summaries and charts (Recharts)
- Run list with status, project, suite, environment, timestamps
- Project creation with repo URL and auth method
- Infrastructure resource status
- Authentication state via Zustand; token in localStorage

---

## 19. Technology Stack

### 19.1 Backend

- **Python 3.11** with **Poetry**
- **FastAPI** for REST APIs
- **SQLAlchemy 2** + **Alembic**
- **Celery** + **RabbitMQ** + **Redis**
- **PostgreSQL 15**
- **MinIO** (S3-compatible)
- **pytest**, **pytest-bdd**, **Selenium**, **Allure**

### 19.2 Frontend

- **React 18**
- **TypeScript 5**
- **Vite 5**
- **React Router 6**
- **Zustand**, **TanStack React Query**
- **Axios**, **Recharts**

### 19.3 Infrastructure

- **Docker** + **Docker Compose**
- **Kubernetes** + **Helm** (production)
- **Prometheus** + **Grafana** + **Loki**

---

## 20. Deployment & Operations

### 20.1 Local (Docker Compose)

- Single command: `./deployment/docker-compose/install.sh`
- Script checks prerequisites, creates dirs, `.env`, starts services
- Service management: `./manage.sh start|stop|restart|status|logs`

### 20.2 Production (Kubernetes)

- Helm charts in `deployment/helm/`
- Prerequisites: Kubernetes 1.24+, Helm 3.8+
- Storage classes for PostgreSQL, MinIO

### 20.3 Default Credentials

**Local/Development:**
- QAtron Board: `admin` / `admin`
- PostgreSQL: `qatron` / `qatron`
- MinIO: `minioadmin` / `minioadmin`
- Grafana: `admin` / `admin` (change on first login)

**Production Requirements:**
- **MUST change QAtron admin password** via environment variable `DEFAULT_ADMIN_PASSWORD` or manual user update
- Install script should prompt for admin password in production mode
- All service credentials should use strong, randomly generated values
- Never use default credentials in production deployments

---

## 21. MVP Acceptance Criteria

### 21.1 Definition of Done

A QAtron installation is considered MVP-complete when all of the following are verified:

| Criteria | Verification Method |
|----------|---------------------|
| **Installation** | `install.sh` successfully stands up all services (Control Plane, Orchestrator, Board, DB, queues, storage) |
| **Authentication** | User can login with admin/admin and access Board |
| **Project Management** | User can create project via UI with repo URL and auth method |
| **Environment & Suite** | User can configure environments (dev/staging/prod) and suites (smoke/regression) |
| **CLI Integration** | `qatron init` creates working repo template with BDD features |
| **Run Execution** | `qatron run --suite smoke --env staging` triggers run and displays results |
| **API Integration** | CI can trigger run via API, poll status, and download artifacts |
| **Artifacts** | Artifacts (Allure reports, coverage) retrievable from API and accessible from Board |
| **Reporting** | Allure HTML reports viewable from Board with pass/fail metrics |
| **Observability** | Basic Grafana dashboards show run metrics and service health |
| **Audit Trail** | Audit log records run triggers and configuration changes |

### 21.2 End-to-End Test Scenarios

**Scenario 1: Create Project and Run Smoke Tests**
1. Login to Board → Create project → Configure environment → Configure suite
2. Use CLI: `qatron init` → `qatron run --suite smoke`
3. Verify run appears in Board with status and results
4. Open Allure report link

**Scenario 2: CI Integration**
1. Create service token via API
2. Trigger run from GitHub Actions using service token
3. Poll run status until completion
4. Download artifacts and verify Allure report exists

**Scenario 3: Multi-Shard Execution**
1. Configure suite with `shards: 4`
2. Trigger run with large test suite
3. Verify 4 parallel workers execute tests
4. Verify coverage combines correctly from all shards

---

## 22. Phase 2 Roadmap

### Planned Features

| Feature | Description |
|---------|-------------|
| **Keycloak SSO** | Replace basic auth with OIDC; user provisioning from Keycloak |
| **Advanced Test Data** | Scheduled refreshes, webhooks, validation history, alerting |
| **Flakiness Quarantine** | Quarantine status, manual/bulk ops, smart retry policies |
| **Advanced Infrastructure** | Real-time metrics, queue analytics, auto-scaling, capacity planning |
| **Namespace-per-Project** | Optional Kubernetes namespace isolation per project |

See [PHASE2.md](PHASE2.md) for details.

---

## 23. Out of Scope

- Mobile app testing (Selenium Grid focuses on web)
- Performance/load testing (focus is functional QA)
- Test case management as a separate product (tests live in repos)
- Built-in AI/ML for test generation (future consideration)

---

## 24. Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| **BDD** | Behavior-Driven Development |
| **Suite** | Named collection of tests (e.g., smoke, regression) |
| **Shard** | Parallel slice of a suite for faster execution |
| **Run** | Single execution of a suite against an environment |

### B. Related Documents

- [Installation Guide](INSTALLATION.md)
- [User Guide](USER_GUIDE.md)
- [Phase 2 Features](PHASE2.md)

### C. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | Feb 2025 | QAtron Team | Added Tenancy Model, Execution Model, Sharding Model, Artifact Lifecycle, BDD Ingestion, Coverage, Security enhancements, Audit Logging, MVP Acceptance Criteria |
| 1.0 | Feb 2025 | QAtron Team | Initial PRD |
