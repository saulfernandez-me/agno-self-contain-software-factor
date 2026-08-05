from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]

# In the target repository, these imports will resolve to the stamped agents
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]
from src.agents.reviewer import get_reviewer_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


class PlanEnvelope(EnvelopeBase):
    """Specific envelope for the planning phase."""



class ReviewEnvelope(EnvelopeBase):
    """Specific envelope for the review phase."""



def run_standard_sdlc(task_description: str, domain_context: str) -> None:
    """
    Executes the Standard SDLC workflow: Plan -> Build -> Test -> Review.
    """
    workflow = AssfWorkflow(name="standard_sdlc")

    # Instantiate agents
    planner = get_planner_agent(
        domain_context, "Create a technical plan.", PlanEnvelope
    )
    builder = get_builder_agent(domain_context, "Implement the plan.", EnvelopeBase)
    reviewer = get_reviewer_agent(
        domain_context, "Review the implementation.", ReviewEnvelope
    )

    # 1. PLAN PHASE
    with workflow.lane("agent"):
        print("Running Planner...")
        plan_response = planner.run(task_description)
        plan_envelope = plan_response.data

    # 2. BUILD PHASE
    with workflow.lane("agent"):
        print("Running Builder...")
        build_task = f"Plan Summary: {plan_envelope.summary}\nExecute it."
        build_response = builder.run(build_task)
        build_envelope = build_response.data

    # 3. VERIFICATION (GATE) & CORRECTION LOOP
    max_attempts = 3
    for attempt in range(max_attempts):
        with workflow.lane("code"):
            print(f"Running Tests (Attempt {attempt + 1})...")
            # Example gate: run tests
            success, _stdout, stderr = run_shell_command("pytest")

        if success:
            print("Gate passed!")
            break
        else:
            if attempt == max_attempts - 1:
                with workflow.lane("engineer"):
                    print("Escalating to engineer. Max attempts reached.")
                return  # Halt pipeline

            with workflow.lane("agent"):
                print("Tests failed. Triggering in-session correction...")
                # In-session correction: reuse the builder session
                correction_prompt = (
                    f"Tests failed. Please fix the code. Stderr:\n{stderr}"
                )
                build_response = builder.run(correction_prompt)
                build_envelope = build_response.data

    # 4. REVIEW PHASE
    with workflow.lane("agent"):
        print("Running Reviewer...")
        review_task = (
            f"Review the changes made by the builder. Summary: {build_envelope.summary}"
        )
        review_response = reviewer.run(review_task)
        review_envelope = review_response.data

    # 5. HUMAN IN THE LOOP (HITL)
    with workflow.lane("engineer"):
        print(
            f"Workflow complete. Reviewer status: {review_envelope.status}. Ready for manual PR merge."
        )


if __name__ == "__main__":
    # Example execution
    run_standard_sdlc(
        task_description="Create a new authentication endpoint.",
        domain_context="You are in a FastAPI software engineering repository.",
    )
