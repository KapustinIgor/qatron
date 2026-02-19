# Alembic Migration Notes

## New Features Requiring Database Migrations

The following changes require database migrations:

### 1. Service Tokens Table
- New table: `service_tokens`
- Fields: id, name, token_hash, organization_id, project_id, created_by_user_id, is_active, expires_at, last_used_at, description, created_at, updated_at
- Foreign keys: organization_id -> organizations.id, project_id -> projects.id, created_by_user_id -> users.id

### 2. Expanded Run Status
- Updated `runs.status` column comment to include new statuses: provisioning, reporting, partial_failed, timed_out, infra_failed
- No schema change needed, just documentation

### 3. Run Metadata for Shards and Coverage
- `runs.run_metadata` already exists (JSON column)
- New usage: track shard results and coverage data
- Example structure:
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

### 4. Feature/Scenario/Step Model Updates
- `features.tags`: Changed from comma-separated to JSON array
- `scenarios.tags`: Changed to JSON array
- `scenarios.scenario_type`: New field (scenario or scenario_outline)
- `scenarios.examples`: New field (JSON array of arrays)
- `steps.order`: New field (Integer, for ordering steps)
- `steps.data_table`: New field (JSON array of arrays)

### 5. Suite Model Updates
- `suites.require_dataset_health`: New Boolean field (default False)

### 6. DatasetVersion Model Updates
- `dataset_versions.storage_path`: New field (String, path to dataset file)
- `dataset_versions.expectations`: New field (Text, JSON expectation suite)

## Migration Commands

```bash
# Generate migration
cd services/control-plane
alembic revision --autogenerate -m "Add service tokens, expand run statuses, update feature models"

# Review and edit migration file
# Then apply:
alembic upgrade head
```

## Manual SQL (if not using Alembic)

See individual migration files in `alembic/versions/` for SQL statements.
