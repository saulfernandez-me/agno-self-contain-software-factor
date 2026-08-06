from apf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from apf_core.workflow import ApfWorkflow  # type: ignore[import-not-found]


def run():
    wf = ApfWorkflow(name="05_quality_gates")
    with wf.lane("code"):
        run_shell_command("ruff check .")
        run_shell_command("pytest")
