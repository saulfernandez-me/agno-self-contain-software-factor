from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="09_plan_build_test")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    builder = get_builder_agent(domain, "Implement", EnvelopeBase)

    with wf.lane("agent"):
        plan = wf.run_agent(planner, task)
        wf.run_agent(builder, plan.summary)

    for _ in range(3):
        with wf.lane("code"):
            ok, _, err = run_shell_command("pytest")
        if ok:
            break
        with wf.lane("agent"):
            wf.run_agent(builder, err)
