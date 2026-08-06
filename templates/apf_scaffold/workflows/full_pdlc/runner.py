from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.documenter import get_documenter_agent  # type: ignore[import-not-found]
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]
from src.agents.reviewer import get_reviewer_agent  # type: ignore[import-not-found]

from apf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from apf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from apf_core.workflow import ApfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = ApfWorkflow(name="12_full_pdlc")
    planner = get_planner_agent(domain, task, EnvelopeBase)
    builder = get_builder_agent(domain, "Build", EnvelopeBase)
    reviewer = get_reviewer_agent(domain, "Review", EnvelopeBase)
    doc = get_documenter_agent(domain, "Document", EnvelopeBase)

    with wf.lane("agent"):
        plan = wf.run_agent(planner, task)

    for _ in range(3):
        with wf.lane("agent"):
            handoff_prompt = f"""
            [PLAN SUMMARY]
            {plan.summary}
            
            [TECHNICAL INSTRUCTIONS FROM PLANNER]
            {plan.notes_for_next_agent}
            
            [FILES TO TOUCH]
            {", ".join(plan.artifacts)}
            
            Execute the plan strictly.
            """
            wf.run_agent(builder, handoff_prompt)
        with wf.lane("code"):
            ok, _, err = run_shell_command("pytest")
        if not ok:
            plan.summary = f"Fix tests: {err}"
            continue

        with wf.lane("agent"):
            rev = wf.run_agent(reviewer, "Audit")
        if rev.status == "success":
            break
        plan.summary = f"Fix review: {rev.notes_for_next_agent}"

    with wf.lane("agent"):
        wf.run_agent(doc, "Write PR based on changes")
