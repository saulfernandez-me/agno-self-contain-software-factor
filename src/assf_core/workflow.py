import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Literal

from agno.workflow import Workflow

from assf_core.telemetry import TelemetryDB

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
        self.session_id = str(uuid.uuid4())
        # We assign TelemetryDB to self.telemetry (type ignored because parent workflow might have a bool var of the same name or similar)
        self._telemetry = TelemetryDB()
        self._telemetry.start_session(self.session_id, self.name or "unknown")

    @contextmanager
    def lane(self, lane_type: LaneType) -> Generator[None, None, None]:
        """
        Context manager to enforce and track execution lanes.
        """
        phase_id = str(uuid.uuid4())
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            self.lane_metrics[lane_type]["count"] += 1
            self.lane_metrics[lane_type]["total_time_ms"] += duration_ms
            if self.session_id:
                self._telemetry.log_phase(
                    phase_id, self.session_id, lane_type, start_time, end_time
                )

    def finish(self, status: str = "completed") -> None:
        """Marks the workflow session as finished in the telemetry DB."""
        if self.session_id:
            self._telemetry.end_session(self.session_id, status)
