from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="10_plan_build_test_quality")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    builder = get_builder_agent(domain, "Implement", EnvelopeBase)

    with wf.lane("agent"):
        plan = planner.run(task)
        builder.run(plan.data.summary)

    for _ in range(3):
        with wf.lane("code"):
            lok, _, lerr = run_shell_command("ruff check .")
        if not lok:
            with wf.lane("agent"):
                builder.run(lerr)
            continue

        with wf.lane("code"):
            tok, _, terr = run_shell_command("pytest")
        if tok:
            break
        with wf.lane("agent"):
            builder.run(terr)
