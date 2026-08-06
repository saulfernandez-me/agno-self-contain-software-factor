from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]
from src.agents.scout import get_scout_agent  # type: ignore[import-not-found]

from apf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from apf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from apf_core.workflow import ApfWorkflow  # type: ignore[import-not-found]


class ScoutEnvelope(EnvelopeBase):
    pass


def run(bug_description: str, domain_context: str) -> None:
    workflow = ApfWorkflow(name="bug_fix_loop")

    scout = get_scout_agent(
        domain_context, "Reproduce the bug and gather logs.", ScoutEnvelope
    )
    builder = get_builder_agent(
        domain_context, "Fix the bug based on logs.", EnvelopeBase
    )

    with workflow.lane("agent"):
        print("Running Scout to gather bug context...")
        scout_envelope = workflow.run_agent(scout, bug_description)

    with workflow.lane("agent"):
        print("Running Builder to apply fix...")
        build_task = f"""
        [ORIGINAL BUG REPORT]
        {bug_description}
        
        [SCOUT DIAGNOSTICS & LOGS]
        {scout_envelope.summary}
        
        Apply the exact fix to resolve this bug.
        """
        workflow.run_agent(builder, build_task)

    max_attempts = 3
    for attempt in range(max_attempts):
        with workflow.lane("code"):
            print(f"Running Regression Tests (Attempt {attempt + 1})...")
            success, _stdout, stderr = run_shell_command("pytest tests/test_bug.py")

        if success:
            print("Gate passed! Bug fixed.")
            break
        else:
            if attempt == max_attempts - 1:
                with workflow.lane("engineer"):
                    print("Escalating to engineer. Unfixable Bug.")
                return

            with workflow.lane("agent"):
                correction_prompt = f"""
                [ORIGINAL BUG REPORT]
                {bug_description}
                
                [TEST FAILURE (ATTEMPT {attempt + 1})]
                {stderr}
                
                The previous fix failed the regression test. Adjust the code.
                """
                workflow.run_agent(builder, correction_prompt)
