from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]

from asf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from asf_core.workflow import AsfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AsfWorkflow(name="06_plan_build")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    builder = get_builder_agent(domain, "Implement plan", EnvelopeBase)

    with wf.lane("agent"):
        res = wf.run_agent(planner, task)
        wf.run_agent(builder, f"Plan: {res.data.summary}")
