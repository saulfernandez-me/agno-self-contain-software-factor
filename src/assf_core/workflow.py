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

    def run_agent(self, agent: Any, prompt: str) -> Any:
        """
        Executes an agent and extracts its structured output.
        Implements a robust fallback mechanism that catches ALL model-related errors
        (including 404s, Auth errors, etc.) and tries the next model in the fallback pool.
        """
        from agno.models.utils import get_model
        from pydantic import BaseModel

        # Collect all models to try (primary + fallbacks)
        models_to_try = [agent.model]
        if hasattr(agent, "fallback_models") and agent.fallback_models:
            models_to_try.extend(agent.fallback_models)

        last_error = None
        for model in models_to_try:
            try:
                # Force the agent to use this specific model for this attempt
                agent.model = get_model(model) if isinstance(model, str) else model

                print(
                    f"[ASSF] Attempting execution with model: {getattr(agent.model, 'id', getattr(agent.model, 'name', str(model)))}"
                )
                response = agent.run(prompt)

                # Agno 2.8.7 structured output extraction
                output = None
                if hasattr(response, "data") and response.data is not None:
                    output = response.data
                elif hasattr(response, "content") and isinstance(
                    response.content, BaseModel
                ):
                    output = response.content

                if output is not None:
                    return output

                last_error = f"Model {getattr(agent.model, 'id', str(agent.model))} failed to generate valid structured Pydantic data. Raw content: {getattr(response, 'content', 'None')}"
                print(f"[ASSF] Warning: {last_error} Falling back...")

            except Exception as e:
                last_error = str(e)
                print(
                    f"[ASSF] Warning: Model {getattr(agent.model, 'id', getattr(agent.model, 'name', str(model)))} raised exception: {last_error}. Falling back..."
                )

        raise RuntimeError(f"All agent models failed. Last error: {last_error}")
