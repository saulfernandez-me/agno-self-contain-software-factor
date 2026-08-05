from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]

# In the target repository, these imports will resolve to the stamped agents
from src.agents.scout import get_scout_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


class ScoutEnvelope(EnvelopeBase):
    """Specific envelope for the scout phase."""


def run_bug_fix_loop(bug_description: str, domain_context: str) -> None:
    """
    Executes the Bug Fix workflow: Reproduce (Scout) -> Fix (Builder) -> Test (Gate).
    """
    workflow = AssfWorkflow(name="bug_fix_loop")

    # Instantiate agents
    scout = get_scout_agent(
        domain_context, "Reproduce the bug and gather logs.", ScoutEnvelope
    )
    builder = get_builder_agent(
        domain_context, "Fix the bug based on logs.", EnvelopeBase
    )

    # 1. SCOUT PHASE (Reproduce)
    with workflow.lane("agent"):
        print("Running Scout to gather bug context...")
        scout_response = scout.run(bug_description)
        scout_envelope = scout_response.data

    # 2. BUILD PHASE (Fix)
    with workflow.lane("agent"):
        print("Running Builder to apply fix...")
        build_task = f"Bug context: {scout_envelope.summary}\nApply the fix."
        builder.run(build_task)

    # 3. VERIFICATION (GATE) & CORRECTION LOOP
    max_attempts = 3
    for attempt in range(max_attempts):
        with workflow.lane("code"):
            print(f"Running Regression Tests (Attempt {attempt + 1})...")
            # Example gate: run the specific test that reproduces the bug
            success, _stdout, stderr = run_shell_command("pytest tests/test_bug.py")

        if success:
            print("Gate passed! Bug fixed.")
            break
        else:
            if attempt == max_attempts - 1:
                with workflow.lane("engineer"):
                    print(
                        "Escalating to engineer. Unfixable Bug (Max attempts reached)."
                    )
                return  # Halt pipeline

            with workflow.lane("agent"):
                print("Regression tests failed. Triggering in-session correction...")
                # In-session correction: reuse the builder session
                correction_prompt = (
                    f"The fix failed the regression test. Stderr:\n{stderr}"
                )
                builder.run(correction_prompt)


if __name__ == "__main__":
    # Example execution
    run_bug_fix_loop(
        bug_description="Users report a 500 error when logging in without a password.",
        domain_context="You are in a FastAPI software engineering repository.",
    )
