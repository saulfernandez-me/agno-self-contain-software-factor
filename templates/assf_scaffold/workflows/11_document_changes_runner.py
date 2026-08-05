from src.agents.documenter import get_documenter_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="11_document_changes")
    doc = get_documenter_agent(domain, task, EnvelopeBase)

    with wf.lane("code"):
        _, diff, _ = run_shell_command("git diff main")

    with wf.lane("agent"):
        doc.run(f"Diff: {diff}")
