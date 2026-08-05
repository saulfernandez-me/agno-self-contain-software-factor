from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]

from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="06_plan_build")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    builder = get_builder_agent(domain, "Implement plan", EnvelopeBase)

    with wf.lane("agent"):
        res = planner.run(task)
        builder.run(f"Plan: {res.data.summary}")
