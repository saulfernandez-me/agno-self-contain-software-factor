from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]

from asf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from asf_core.workflow import AsfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AsfWorkflow(name="03_plan_only")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    with wf.lane("agent"):
        wf.run_agent(planner, task)
