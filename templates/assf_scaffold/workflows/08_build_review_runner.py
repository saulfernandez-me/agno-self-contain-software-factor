from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.reviewer import get_reviewer_agent  # type: ignore[import-not-found]

from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="08_build_review")
    builder = get_builder_agent(domain, task, EnvelopeBase)
    reviewer = get_reviewer_agent(domain, "Review code", EnvelopeBase)

    with wf.lane("agent"):
        builder.run(task)

    for _ in range(3):
        with wf.lane("agent"):
            rev = reviewer.run("Audit changes")
        if rev.content.status == "success":
            break
        with wf.lane("agent"):
            builder.run(f"Fix review notes: {rev.content.notes_for_next_agent}")
