from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.reviewer import get_reviewer_agent  # type: ignore[import-not-found]

from asf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from asf_core.workflow import AsfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AsfWorkflow(name="08_build_review")
    builder = get_builder_agent(domain, task, EnvelopeBase)
    reviewer = get_reviewer_agent(domain, "Review code", EnvelopeBase)

    with wf.lane("agent"):
        wf.run_agent(builder, task)

    for _ in range(3):
        with wf.lane("agent"):
            rev = wf.run_agent(reviewer, "Audit changes")
        if rev.status == "success":
            break
        with wf.lane("agent"):
            wf.run_agent(builder, f"Fix review notes: {rev.notes_for_next_agent}")
