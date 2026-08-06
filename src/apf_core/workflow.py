import time
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Literal

from agno.workflow import Workflow

from apf_core.telemetry import TelemetryDB

LaneType = Literal["agent", "code", "engineer"]


class ApfWorkflow(Workflow):
    """
    APF custom workflow extending Agno's Workflow.
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

    def run_agent(
        self, agent: Any, prompt: str, skills: list[str] | None = None
    ) -> Any:
        """
        Executes an agent with the Universal Two-Step Harness (Envelope Wrapper).
        Step 1: The agent executes cognitively without Pydantic constraints, avoiding tool-call hallucinations.
        Step 2: A FormatterAgent extracts the execution logs into the strict Pydantic Envelope.

        Args:
            agent: The Agno agent instance.
            prompt: The specific task instruction (composite prompt).
            skills: Optional list of skill names (e.g., ['python_expert']) to load from `.context/skills/`.
        """
        from pathlib import Path

        from agno.agent import Agent
        from agno.models.utils import get_model
        from pydantic import BaseModel

        from apf_core.config import get_models_for_tier

        # Load skills if requested
        injected_skills = ""
        if skills:
            skill_texts = []
            for skill in skills:
                skill_path = Path(f".context/skills/{skill}.md")
                if skill_path.exists():
                    skill_texts.append(skill_path.read_text(encoding="utf-8"))
                else:
                    print(
                        f"[APF] Warning: Skill '{skill}' requested but not found at {skill_path}."
                    )
            if skill_texts:
                injected_skills = (
                    "\n\n[INJECTED SKILLS & METHODOLOGIES]\n"
                    + "\n\n---\n\n".join(skill_texts)
                )

        # Append skills to the prompt
        final_prompt = prompt + injected_skills

        # Extract the expected schema from the agent's initialization
        expected_schema = getattr(agent, "output_schema", None)

        # Temporarily strip the structured output constraint from the cognitive agent
        agent.output_schema = None

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
                    f"[APF] Cognitive Phase: Running {agent.name} with model {getattr(agent.model, 'id', getattr(agent.model, 'name', str(model)))}..."
                )

                # STEP 1: Cognitive Execution (Free-form text, safe tool usage)
                cognitive_response = agent.run(final_prompt)
                cognitive_content = getattr(
                    cognitive_response, "content", str(cognitive_response)
                )

                # If no schema was expected, just return the raw text
                if not expected_schema:
                    agent.output_schema = expected_schema  # Restore
                    return cognitive_content

                # STEP 2: Formatting Execution (Envelope Wrapper)
                formatter_models = get_models_for_tier("lightweight")
                formatter_model = get_model(formatter_models[0])

                print(
                    f"[APF] Formatting Phase: Extracting Envelope via {getattr(formatter_model, 'id', str(formatter_model))}..."
                )
                formatter = Agent(
                    name="Formatter",
                    model=formatter_model,
                    description="You are a strict data formatter. Your only job is to extract the required fields into the JSON schema.",
                    instructions=f"Analyze the following execution log. Extract the precise status, summary, and artifacts touched. If the execution failed or encountered errors, set status to 'fail'.\n\n[EXECUTION LOG]\n{cognitive_content}",
                    output_schema=expected_schema,
                )

                formatter_response = formatter.run(
                    "Format the execution output into the required JSON envelope."
                )

                # Extract Structured Output
                output = None
                if (
                    hasattr(formatter_response, "data")
                    and formatter_response.data is not None
                ):
                    output = formatter_response.data
                elif hasattr(formatter_response, "content") and isinstance(
                    formatter_response.content, BaseModel
                ):
                    output = formatter_response.content

                if output is not None:
                    agent.output_schema = expected_schema  # Restore
                    return output

                last_error = f"Formatter failed to generate valid structured Pydantic data. Raw content: {getattr(formatter_response, 'content', 'None')}"
                print(
                    f"[APF] Warning: {last_error} Falling back to next cognitive model..."
                )

            except (OSError, ValueError, RuntimeError, ImportError) as e:
                last_error = str(e)
                print(
                    f"[APF] Warning: Model {getattr(agent.model, 'id', getattr(agent.model, 'name', str(model)))} raised exception: {last_error}. Falling back..."
                )

        # Ensure we restore the agent's schema even if it fails completely
        agent.output_schema = expected_schema
        raise RuntimeError(f"All agent models failed. Last error: {last_error}")
