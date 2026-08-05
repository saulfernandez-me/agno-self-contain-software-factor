from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.documenter import get_documenter_agent  # type: ignore[import-not-found]
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]
from src.agents.reviewer import get_reviewer_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="12_full_sdlc")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    builder = get_builder_agent(domain, "Build", EnvelopeBase)
    reviewer = get_reviewer_agent(domain, "Review", EnvelopeBase)
    doc = get_documenter_agent(domain, "Document", EnvelopeBase)

    with wf.lane("agent"):
        plan = planner.run(task)

    for _ in range(3):
        with wf.lane("agent"):
            builder.run(plan.content.summary)
        with wf.lane("code"):
            ok, _, err = run_shell_command("pytest")
        if not ok:
            plan.content.summary = f"Fix tests: {err}"
            continue

        with wf.lane("agent"):
            rev = reviewer.run("Audit")
        if rev.content.status == "success":
            break
        plan.content.summary = f"Fix review: {rev.content.notes_for_next_agent}"

    with wf.lane("agent"):
        doc.run("Write PR based on changes")
