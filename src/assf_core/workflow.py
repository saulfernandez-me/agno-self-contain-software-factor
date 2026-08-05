import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Literal

from agno.workflow import Workflow

LaneType = Literal["agent", "code", "engineer"]


class AssfWorkflow(Workflow):
    """
    ASSF custom workflow extending Agno's Workflow.
    Enforces deterministic, code-driven steps and tracks strict execution lanes.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Tracking metrics for each lane type
        self.lane_metrics: dict[LaneType, dict[str, Any]] = {
            "agent": {"count": 0, "total_time_ms": 0.0},
            "code": {"count": 0, "total_time_ms": 0.0},
            "engineer": {"count": 0, "total_time_ms": 0.0},
        }

    @contextmanager
    def lane(self, lane_type: LaneType) -> Generator[None, None, None]:
        """
        Context manager to enforce and track execution lanes.

        Args:
            lane_type: The type of execution lane ('agent', 'code', or 'engineer').

        Yields:
            None
        """
        start_time = time.time()
        try:
            # Yield execution back to the block inside the context manager
            yield
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Record the telemetry metrics for the lane
            self.lane_metrics[lane_type]["count"] += 1
            self.lane_metrics[lane_type]["total_time_ms"] += duration_ms
