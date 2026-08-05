from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run():
    wf = AssfWorkflow(name="05_quality_gates")
    with wf.lane("code"):
        run_shell_command("ruff check .")
        run_shell_command("pytest")
