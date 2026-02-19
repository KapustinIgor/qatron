"""Worker HTTP server: accepts execute requests from the orchestrator."""
import json
import logging
import os
import subprocess
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException

logger = logging.getLogger(__name__)

app = FastAPI(title="QAtron Worker", version="0.1.0")


def _post_run_status(run_id: int, status: str) -> None:
    """Post run status to control-plane internal API (best effort)."""
    control_plane_url = os.getenv("CONTROL_PLANE_API_URL", "http://control-plane:8000/api/v1").rstrip("/")
    internal_secret = os.getenv("INTERNAL_API_SECRET")
    url = f"{control_plane_url}/internal/runs/{run_id}/results"
    headers = {}
    if internal_secret:
        headers["X-Internal-Secret"] = internal_secret
    try:
        httpx.put(url, json={"status": status}, headers=headers, timeout=10.0)
    except Exception:
        pass


@app.get("/healthz")
def health():
    return {"status": "healthy"}


@app.post("/execute")
def execute(body: dict):
    """
    Run a test job. Body: { "job": { run_id, shard_index, shard_total }, "context": { ... } }.
    Spawns the executor with env from context and container env (SELENIUM_GRID_URL, S3_*, etc.).
    """
    job = body.get("job") or {}
    context = body.get("context") or {}
    run_id = job.get("run_id")
    shard_index = job.get("shard_index", 0)
    _shard_total = job.get("shard_total", 1)  # reserved for future sharding
    if not run_id:
        raise HTTPException(status_code=400, detail="job.run_id required")

    repo_url = (context.get("repo_url") or "").strip()
    if not repo_url:
        _post_run_status(run_id, "failed")
        raise HTTPException(
            status_code=400,
            detail="Project has no repo_url. Set a cloneable Git URL in the project settings.",
        )

    # So the UI shows "Running" while the job executes
    _post_run_status(run_id, "running")

    workspace_dir = f"/workspace/run_{run_id}_shard_{shard_index}"
    Path(workspace_dir).mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["REPO_URL"] = repo_url
    env["COMMIT"] = context.get("commit", "HEAD")
    env["SUITE_NAME"] = context.get("suite_name", "default")
    env["ENVIRONMENT"] = context.get("environment_name", "default")
    env["LAYER"] = context.get("layer", "e2e")
    env["WORKSPACE_DIR"] = workspace_dir
    env.setdefault("CONTROL_PLANE_API_URL", "http://control-plane:8000/api/v1")
    # SELENIUM_GRID_URL should be set in container (e.g. http://selenium-hub:4444/wd/hub)

    job_json = json.dumps(job)
    try:
        proc = subprocess.run(
            ["python", "-m", "app.executor", job_json],
            env=env,
            capture_output=True,
            text=True,
            timeout=3600,
            cwd="/app",
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Job timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if proc.returncode != 0:
        err = proc.stderr or proc.stdout or f"Executor exited with {proc.returncode}"
        logger.error("Executor failed run_id=%s: %s", run_id, err)
        if proc.stdout:
            logger.error("Executor stdout: %s", proc.stdout[-2000:])  # last 2k chars
        if proc.stderr:
            logger.error("Executor stderr: %s", proc.stderr[-2000:])
        _post_run_status(run_id, "failed")
        raise HTTPException(status_code=502, detail=err)
    return {"status": "completed", "run_id": run_id, "shard_index": shard_index}
