from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="07_build_test")
    builder = get_builder_agent(domain, task, EnvelopeBase)

    with wf.lane("agent"):
        builder.run(task)

    for _ in range(3):
        with wf.lane("code"):
            ok, _, err = run_shell_command("pytest")
        if ok:
            break
        with wf.lane("agent"):
            builder.run(f"Fix tests: {err}")
