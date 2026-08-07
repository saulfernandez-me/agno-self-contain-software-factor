from src.agents.functional_analyst import (  # type: ignore[import-not-found]
    get_functional_analyst_agent,  # type: ignore[import-not-found]
)
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]
from src.agents.product_owner import (  # type: ignore[import-not-found]
    get_product_owner_agent,  # type: ignore[import-not-found]
)

from apf_core.assert_gates import run_shell_command
from apf_core.workflow import ApfWorkflow

from .envelopes import (
    BacklogEnvelope,
    FunctionalRequirementsEnvelope,
    ProductAnalysisEnvelope,
)


def run(epic_description: str, domain_context: str) -> None:
    """
    Executes the Product Management workflow: Epic Ideation -> Product Analysis -> Functional Specs -> Atomic Issue Generation.
    """
    workflow = ApfWorkflow(name="epic_to_issues")

    product_owner = get_product_owner_agent(
        domain_context,
        "Act as the Product Owner. Analyze this Epic for edge cases, validity, and define an MVP scope.",
        ProductAnalysisEnvelope,
    )

    functional_analyst = get_functional_analyst_agent(
        domain_context,
        "Act as the Functional Analyst. Translate the PO's MVP into precise system behaviors (BDD) without dictating technical architecture.",
        FunctionalRequirementsEnvelope,
    )

    scrum_master = get_planner_agent(
        domain_context,
        "Act as a Technical Scrum Master / Architect. Take the Functional Analyst's behavioral requirements and break them down into atomic, highly technical GitHub issues.",
        BacklogEnvelope,
    )

    # 1. PRODUCT ANALYSIS PHASE
    with workflow.lane("agent"):
        print("Running Product Owner Analysis...")
        po_envelope = workflow.run_agent(
            product_owner, f"Epic Request: {epic_description}"
        )

    # 2. FUNCTIONAL ANALYSIS PHASE
    with workflow.lane("agent"):
        print("Running Functional Analyst Translation...")
        fa_task = f"""
        [ORIGINAL EPIC]
        {epic_description}
        
        [MVP SCOPE FROM PO]
        {po_envelope.recommended_mvp_scope}
        
        [IDENTIFIED EDGE CASES]
        {", ".join(po_envelope.edge_cases)}
        
        Translate these business constraints into functional system behaviors.
        """
        fa_envelope = workflow.run_agent(functional_analyst, fa_task)

    # 3. BREAKDOWN PHASE
    with workflow.lane("agent"):
        print("Running Scrum Master Breakdown...")
        sm_task = f"""
        [ORIGINAL EPIC]
        {epic_description}
        
        [FUNCTIONAL BEHAVIORS TO IMPLEMENT]
        User Flows: {", ".join(fa_envelope.user_flows)}
        Error States: {", ".join(fa_envelope.error_states)}
        Acceptance Criteria: {", ".join(fa_envelope.acceptance_criteria)}
        
        Generate the atomic issues necessary to build these behaviors.
        """
        backlog_envelope: BacklogEnvelope = workflow.run_agent(
            scrum_master, sm_task, skills=["epic_breakdown"]
        )

    # 4. EXECUTION PHASE (GitHub API Injection)
    with workflow.lane("code"):
        # Create GitHub Milestone
        print(f"Creating Milestone '{backlog_envelope.epic_title}' in GitHub...")
        _milestone_ok, _milestone_out, _milestone_err = run_shell_command(
            f'gh api repos/{{owner}}/{{repo}}/milestones -f title="[Epic] {backlog_envelope.epic_title}" --jq ".number"'
        )
        # Note: In a real environment, we'd extract the actual owner/repo, but `gh` often resolves this automatically
        # if we use `gh api repos/@owner/@repo/milestones`. Wait, `gh api` doesn't support @owner/@repo natively in all versions.
        # It's safer to parse `gh repo view --json nameWithOwner --jq .nameWithOwner`.
        _, repo_name, _ = run_shell_command(
            "gh repo view --json nameWithOwner --jq .nameWithOwner"
        )
        if repo_name:
            _milestone_ok, milestone_number, _milestone_err = run_shell_command(
                f'gh api repos/{repo_name}/milestones -f title="[Epic] {backlog_envelope.epic_title}" --jq ".number"'
            )
        else:
            milestone_number = ""

        milestone_flag = f'--milestone "{milestone_number}"' if milestone_number else ""

        print(f"Creating {len(backlog_envelope.issues)} issues in GitHub...")
        success_count = 0
        for issue in backlog_envelope.issues:
            # Construct the gh cli command
            # Note: We save the body to a temp file to avoid bash escaping issues
            import tempfile

            markdown_body = f"""### 📝 Context & Rationale
{issue.context_and_rationale}

### 🧬 Technical Scope
{chr(10).join(f"- {f}" for f in issue.technical_scope)}

### 🛠️ Implementation Steps
{chr(10).join(f"- {step}" for step in issue.implementation_steps)}

### ✅ Definition of Done
{chr(10).join(f"- [ ] {dod}" for dod in issue.definition_of_done)}

### 🧪 Verification Commands
```bash
{issue.verification_command}
```
"""

            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as f:
                f.write(markdown_body)
                temp_path = f.name

            # Create labels gracefully if they don't exist
            all_labels = [
                issue.lifecycle_label,
                issue.size_label,
                issue.scope_label,
            ] + issue.thematic_labels
            for label in all_labels:
                # We ignore the error if it already exists
                run_shell_command(f'gh label create "{label}"')

            labels_flag = ",".join(all_labels)
            issue_title = f"{issue.issue_type}: {issue.title}"

            # Fire the command
            ok, _stdout, stderr = run_shell_command(
                f'gh issue create --title "{issue_title}" --body-file "{temp_path}" --label "{labels_flag}" {milestone_flag}'
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
            "Epic breakdown complete. Check your GitHub project board for the new apf:backlog issues."
        )


if __name__ == "__main__":
    # Example execution
    run(
        epic_description="We need a new user authentication system that supports magic links via email and JWT tokens. It must be highly secure.",
        domain_context="You are in a FastAPI software engineering repository with a PostgreSQL database.",
    )
