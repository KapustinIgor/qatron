# Implementation Summary: PRD Gap Fixes

This document summarizes the implementation of critical and medium-priority gaps identified in the PRD review.

## Critical Gaps Implemented

### 1. Service Tokens for CI/CD Integration ✅

**Implementation:**
- Created `ServiceToken` model (`app/models/service_token.py`)
- Added API endpoints (`app/api/v1/service_tokens.py`):
  - `POST /api/v1/auth/service-tokens` - Create service token
  - `GET /api/v1/auth/service-tokens` - List service tokens
  - `DELETE /api/v1/auth/service-tokens/{token_id}` - Revoke token
- Service tokens are hashed using bcrypt (same as passwords)
- Tokens can be scoped to a specific project or organization-wide
- Support for expiration dates
- Last used timestamp tracking
- Integrated with authentication system (`get_current_user` supports both JWT and service tokens)

**Security:**
- Tokens are only shown once on creation
- Tokens are hashed before storage
- Audit logging for token creation/revocation

### 2. Expanded Run Status Model ✅

**Implementation:**
- Updated `Run.status` column documentation to include:
  - `provisioning` - Infrastructure being provisioned
  - `reporting` - Generating reports
  - `partial_failed` - Some shards failed
  - `timed_out` - Run exceeded timeout
  - `infra_failed` - Infrastructure failure
- Existing statuses: `queued`, `running`, `completed`, `failed`, `cancelled`

### 3. Audit Logging ✅

**Implementation:**
- Created audit logging utility (`app/core/audit.py`)
- Integrated audit logging into:
  - User login (`AUDIT_ACTION_LOGIN`)
  - Run triggers (`AUDIT_ACTION_RUN_TRIGGERED`)
  - Project creation/update/deletion
  - Service token creation/revocation
- Audit logs capture:
  - Action type
  - User ID (nullable for system actions)
  - Resource type and ID
  - Additional details (JSON)
  - IP address and user agent
  - Timestamp

### 4. BDD Feature Ingestion ✅

**Implementation:**
- Created Gherkin parser (`app/services/bdd_parser.py`)
- Parses `.feature` files and extracts:
  - Feature name, description, tags
  - Scenarios (regular and outlines)
  - Steps (Given/When/Then/And/But)
  - Examples tables
  - Data tables
- Added API endpoint (`app/api/v1/features.py`):
  - `POST /api/v1/features/projects/{project_id}/ingest-features` - Scan and ingest features
  - `GET /api/v1/features/projects/{project_id}/features` - List ingested features
- Updated Feature/Scenario/Step models:
  - Tags stored as JSON arrays
  - Added `scenario_type` field (scenario vs scenario_outline)
  - Added `examples` field for scenario outlines
  - Added `order` field to steps for proper sequencing
  - Added `data_table` field for step data tables

### 5. Artifact Lifecycle Management ✅

**Implementation:**
- Created Celery cleanup tasks (`app/tasks/cleanup.py`):
  - `cleanup_artifacts` - Removes artifacts older than retention period (default 30 days)
  - `cleanup_expired_tokens` - Deactivates expired service tokens
- Tasks can be scheduled via Celery beat
- Retention policy configurable per run

### 6. Shard Tracking ✅

**Implementation:**
- Shard results stored in `run.run_metadata` JSON field
- Added repository methods:
  - `update_shard_results(run_id, shard_id, shard_result)` - Update individual shard
  - `update_coverage(run_id, coverage_data)` - Update coverage data
- Example metadata structure:
  ```json
  {
    "shards": {
      "1": {"status": "completed", "passed": 10, "failed": 2},
      "2": {"status": "completed", "passed": 8, "failed": 1}
    },
    "coverage": {
      "total": 85.5,
      "files": {...}
    }
  }
  ```

### 7. Dataset Validation Gating ✅

**Implementation:**
- Created dataset validator (`app/services/dataset_validator.py`)
- Integrated Great Expectations for validation
- Added `require_dataset_health` field to Suite model
- Run creation now validates dataset before starting if:
  - Suite has `require_dataset_health=True`
  - Environment has a dataset assigned
- Validation failures block run creation (fail fast)
- Updated DatasetVersion model:
  - Added `storage_path` field
  - Added `expectations` field (JSON expectation suite)

### 8. Coverage Collection ✅

**Implementation:**
- Coverage data stored in `run.run_metadata["coverage"]`
- Repository method `update_coverage()` for storing coverage results
- Integration with pytest-cov handled in worker service (not control plane)
- Coverage can be combined across shards in run metadata

## Medium Priority Gaps Addressed

### Dataset Validation Gating
- Implemented as part of critical gap #7 above

### Shard Aggregation
- Implemented as part of critical gap #6 above

## Database Migrations Required

See `services/control-plane/ALEMBIC_MIGRATION_NOTES.md` for detailed migration requirements.

Key changes:
1. New `service_tokens` table
2. Updated `features`, `scenarios`, `steps` models
3. New fields in `suites` and `dataset_versions`
4. No schema changes needed for run statuses (documentation only)

## API Endpoints Added

### Service Tokens
- `POST /api/v1/auth/service-tokens` - Create token
- `GET /api/v1/auth/service-tokens` - List tokens
- `DELETE /api/v1/auth/service-tokens/{token_id}` - Revoke token

### BDD Features
- `POST /api/v1/features/projects/{project_id}/ingest-features` - Ingest features
- `GET /api/v1/features/projects/{project_id}/features` - List features

## Next Steps (Completed in This Follow-up)

### 1. Run database migrations

From the control-plane service directory, with database available:

```bash
cd services/control-plane
# If using Docker Compose, run migration inside the control-plane container:
docker compose -f deployment/docker-compose/docker-compose.yml exec control-plane alembic upgrade head

# Or with local Python and DATABASE_URL set:
export DATABASE_URL="postgresql://qatron:qatron@localhost:5432/qatron"
alembic upgrade head
```

Migration file: `alembic/versions/20250218000000_add_prd_gaps_schema.py` (adds `service_tokens` table, new columns on `suites`, `scenarios`, `steps`, `dataset_versions`).

### 2. Celery configuration

- **Config:** `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CELERY_ARTIFACT_RETENTION_DAYS` in `app/core/config.py`.
- **App:** `app/celery_app.py` defines the Celery app and Beat schedule.
- **Tasks:** `app/tasks/cleanup.py` — `cleanup_artifacts`, `cleanup_expired_tokens`.
- **Dependency:** `celery[redis]` added to `pyproject.toml`.

To run a worker (optional, for cleanup tasks):

```bash
cd services/control-plane
celery -A app.celery_app worker --loglevel=info
```

To run Beat for scheduled cleanup (optional):

```bash
celery -A app.celery_app beat --loglevel=info
```

### 3. Test new endpoints

```bash
# Login and get JWT
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -d "username=admin&password=admin" | jq -r '.access_token')

# Create a service token (admin only)
curl -s -X POST "http://localhost:8000/api/v1/auth/service-tokens" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"CI","organization_id":1}' | jq

# List service tokens
curl -s "http://localhost:8000/api/v1/auth/service-tokens" -H "Authorization: Bearer $TOKEN" | jq

# List features for a project (replace 1 with project_id)
curl -s "http://localhost:8000/api/v1/features/projects/1/features" -H "Authorization: Bearer $TOKEN" | jq
```

### 4. Further verification

- **Service token auth:** Use the token returned once from create in `Authorization: Bearer <token>` for API calls.
- **BDD ingestion:** Call `POST /api/v1/features/projects/{id}/ingest-features` with a body `{"repo_path": "/path/to/repo"}` (path must be visible to the control-plane process).
- **Dataset gating:** Set a suite’s `require_dataset_health=True` and assign a dataset to the environment; run creation will validate the dataset first.
- **Audit log:** Check `audit_logs` table for `user.login`, `run.triggered`, `project.created`, etc.

## Notes

- Service token authentication is backward compatible with JWT tokens
- BDD parser handles common Gherkin syntax but may need extensions for edge cases
- Dataset validation requires Great Expectations to be installed
- Coverage collection assumes pytest-cov integration in worker service
- Artifact cleanup requires S3/MinIO integration for actual file deletion
