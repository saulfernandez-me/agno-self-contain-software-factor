from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]

from asf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from asf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from asf_core.workflow import AsfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AsfWorkflow(name="07_build_test")
    builder = get_builder_agent(domain, task, EnvelopeBase)

    with wf.lane("agent"):
        wf.run_agent(builder, task)

    for _ in range(3):
        with wf.lane("code"):
            ok, _, err = run_shell_command("pytest")
        if ok:
            break
        with wf.lane("agent"):
            wf.run_agent(builder, f"Fix tests: {err}")
