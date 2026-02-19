"""Metrics aggregation service."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import SessionLocal


class MetricsService:
    """Service for aggregating run metrics."""

    def get_run_metrics(
        self, project_id: Optional[int] = None, days: int = 30
    ) -> Dict:
        """Get aggregated run metrics."""
        db: Session = SessionLocal()
        try:
            # This would query the Run model from control-plane
            # For now, return placeholder structure
            return {
                "total_runs": 0,
                "passed_runs": 0,
                "failed_runs": 0,
                "pass_rate": 0.0,
                "avg_duration": 0.0,
                "p50_duration": 0.0,
                "p95_duration": 0.0,
            }
        finally:
            db.close()

    def get_flakiness_scores(self, scenario_id: Optional[int] = None) -> List[Dict]:
        """Calculate flakiness scores for scenarios."""
        # Flakiness calculation:
        # A test is flaky if within last 20 executions it has:
        # - ≥ 2 transitions between pass/fail AND
        # - failure rate between 5% and 50%
        return []

    def get_coverage_metrics(self, run_id: int) -> Dict:
        """Get coverage metrics for a run."""
        # This would merge coverage from multiple shards
        return {
            "total_coverage": 0.0,
            "by_layer": {},
        }
