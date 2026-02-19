"""Job sharding logic."""
from typing import List


def create_shard_jobs(run_id: int, shard_count: int) -> List[dict]:
    """
    Create shard job payloads for parallel execution.

    Args:
        run_id: The run ID
        shard_count: Number of shards to create

    Returns:
        List of job payloads, one per shard
    """
    jobs = []
    for shard_index in range(shard_count):
        job = {
            "run_id": run_id,
            "shard_index": shard_index,
            "shard_total": shard_count,
        }
        jobs.append(job)
    return jobs
