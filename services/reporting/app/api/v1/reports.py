"""Report endpoints."""
from fastapi import APIRouter, HTTPException, status

from app.services.allure import AllureService

router = APIRouter()


@router.post("/{run_id}/generate")
async def generate_report(run_id: int):
    """Generate Allure report for a run."""
    try:
        service = AllureService()
        results_dir = service.download_results(run_id)
        report_dir = service.generate_report(results_dir, f"run-{run_id}")
        service.upload_report(report_dir, run_id)
        return {"status": "generated", "report_url": service.get_report_url(run_id)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("/{run_id}/allure")
async def get_allure_report(run_id: int):
    """Get Allure report URL."""
    service = AllureService()
    return {"report_url": service.get_report_url(run_id)}
