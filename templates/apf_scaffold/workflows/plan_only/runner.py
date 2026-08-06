from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]

from apf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from apf_core.workflow import ApfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = ApfWorkflow(name="03_plan_only")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    with wf.lane("agent"):
        wf.run_agent(planner, task)
