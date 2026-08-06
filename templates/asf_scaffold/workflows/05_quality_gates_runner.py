from asf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from asf_core.workflow import AsfWorkflow  # type: ignore[import-not-found]


def run():
    wf = AsfWorkflow(name="05_quality_gates")
    with wf.lane("code"):
        run_shell_command("ruff check .")
        run_shell_command("pytest")
