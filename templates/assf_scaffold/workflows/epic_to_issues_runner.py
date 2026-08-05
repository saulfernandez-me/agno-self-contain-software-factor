from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]
from src.agents.reviewer import get_reviewer_agent  # type: ignore[import-not-found]

from assf_core.assert_gates import run_shell_command
from assf_core.epic_envelopes import BacklogEnvelope, ProductAnalysisEnvelope
from assf_core.workflow import AssfWorkflow


def run_epic_breakdown(epic_description: str, domain_context: str) -> None:
    """
    Executes the Product Management workflow: Epic Ideation -> Product Analysis -> Atomic Issue Generation.
    """
    workflow = AssfWorkflow(name="epic_breakdown")

    # 1. Instantiate agents with specific PM roles injected
    product_owner = get_reviewer_agent(
        domain_context,
        "Act as a Product Owner / Devil's Advocate. Analyze this Epic for edge cases, validity, and define an MVP scope.",
        ProductAnalysisEnvelope,
    )

    scrum_master = get_planner_agent(
        domain_context,
        "Act as a Technical Scrum Master. Take the PO's MVP scope and break it down into atomic, highly technical GitHub issues.",
        BacklogEnvelope,
    )

    # 2. PRODUCT ANALYSIS PHASE (Reviewer acting as PO)
    with workflow.lane("agent"):
        print("Running Product Owner Analysis...")
        po_response = workflow.run_agent(
            product_owner, f"Epic Request: {epic_description}"
        )
        po_envelope = po_response.data

    # Note: In ASSF, schema validation happens natively via Pydantic in the agent call,
    # but a formal code gate could check constraints (e.g. no more than 5 edge cases).

    # 3. BREAKDOWN PHASE (Planner acting as Scrum Master)
    with workflow.lane("agent"):
        print("Running Scrum Master Breakdown...")
        sm_task = f"""
        Epic Context: {epic_description}
        MVP Scope from PO: {po_envelope.recommended_mvp_scope}
        Edge Cases to handle: {", ".join(po_envelope.edge_cases)}
        
        Generate the atomic issues.
        """
        sm_response = workflow.run_agent(scrum_master, sm_task)
        backlog_envelope: BacklogEnvelope = sm_response.data

    # 4. EXECUTION PHASE (GitHub API Injection)
    with workflow.lane("code"):
        print(f"Creating {len(backlog_envelope.issues)} issues in GitHub...")
        success_count = 0
        for issue in backlog_envelope.issues:
            # Construct the gh cli command
            # Note: We save the body to a temp file to avoid bash escaping issues
            import tempfile

            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as f:
                f.write(issue.description)
                temp_path = f.name

            labels_flag = ",".join(issue.labels)

            # Fire the command
            ok, _stdout, stderr = run_shell_command(
                f'gh issue create --title "{issue.title}" --body-file "{temp_path}" --label "{labels_flag}"'
            )

            # Clean up
            import os

            os.remove(temp_path)

            if ok:
                success_count += 1
                print(f"Created issue: {issue.title}")
            else:
                print(f"Failed to create issue '{issue.title}': {stderr}")

        if success_count == len(backlog_envelope.issues):
            print("Successfully populated the backlog.")
        else:
            print("Warning: Some issues failed to create.")

    # 5. HALT
    with workflow.lane("engineer"):
        print(
            "Epic breakdown complete. Check your GitHub project board for the new assf:backlog issues."
        )


if __name__ == "__main__":
    # Example execution
    run_epic_breakdown(
        epic_description="We need a new user authentication system that supports magic links via email and JWT tokens. It must be highly secure.",
        domain_context="You are in a FastAPI software engineering repository with a PostgreSQL database.",
    )
