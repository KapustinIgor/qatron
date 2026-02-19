"""Run orchestration endpoints."""
from fastapi import APIRouter, HTTPException, status

from app.tasks.run_tasks import enqueue_run

router = APIRouter()


@router.post("/{run_id}/enqueue")
async def trigger_run(run_id: int):
    """Trigger a run to be enqueued for execution."""
    try:
        enqueue_run.delay(run_id)
        return {"status": "enqueued", "run_id": run_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue run: {str(e)}",
        )
