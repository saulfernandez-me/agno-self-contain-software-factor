from src.agents.documenter import get_documenter_agent  # type: ignore[import-not-found]

from apf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from apf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from apf_core.workflow import ApfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = ApfWorkflow(name="11_document_changes")
    doc = get_documenter_agent(domain, task, EnvelopeBase)

    with wf.lane("code"):
        _, diff, _ = run_shell_command("git diff main")

    with wf.lane("agent"):
        wf.run_agent(doc, f"Diff: {diff}")
