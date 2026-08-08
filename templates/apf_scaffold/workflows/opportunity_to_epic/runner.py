from src.agents.product_owner import get_product_owner_agent  # type: ignore[import-not-found]
from src.agents.business_analyst import get_business_analyst_agent  # type: ignore[import-not-found]
from src.agents.tech_lead import get_tech_lead_agent  # type: ignore[import-not-found]
from src.agents.planner import get_planner_agent  # type: ignore[import-not-found]

from workflows.opportunity_to_epic.envelopes import (  # type: ignore[import-not-found]
    OpportunityAnalysisEnvelope,
    BusinessMetricsEnvelope,
    TechSanityCheckEnvelope,
    EpicFormattingEnvelope,
)

from apf_core.assert_gates import run_shell_command
from apf_core.workflow import ApfWorkflow

def run(opportunity_description: str, domain_context: str, issue_id: str = "") -> None:
    """
    Executes the Opportunity to Epic workflow: PO Refinement -> BA Metrics -> Tech Lead Check -> Scrum Master Formatting.
    """
    workflow = ApfWorkflow(name="opportunity_to_epic")

    product_owner = get_product_owner_agent(
        domain_context,
        "Act as the Product Owner. Review the approved opportunity and define its core scope, epic title, and lifecycle phase.",
        OpportunityAnalysisEnvelope,
    )

    business_analyst = get_business_analyst_agent(
        domain_context,
        "Act as the Business Analyst. Define 1-3 KPIs and tracking requirements for this Epic.",
        BusinessMetricsEnvelope,
    )

    tech_lead = get_tech_lead_agent(
        domain_context,
        "Act as the Tech Lead. Evaluate the feasibility of the MVP scope and provide high-level guardrails.",
        TechSanityCheckEnvelope,
    )

    scrum_master = get_planner_agent(
        domain_context,
        "Act as a Scrum Master. Compile the business scope, KPIs, and tech guardrails into a single, highly readable Epic Markdown document using the `save_artifact` tool. Do NOT generate the file content in the JSON.",
        EpicFormattingEnvelope,
    )

    # 1. PRODUCT ANALYSIS PHASE
    with workflow.lane("agent"):
        print("Running Product Owner Analysis...")
        po_envelope: OpportunityAnalysisEnvelope = workflow.run_agent(
            product_owner, f"Approved Opportunity:\n{opportunity_description}"
        )

    # 2. BUSINESS METRICS PHASE
    with workflow.lane("agent"):
        print("Running Business Analyst Metrics Definition...")
        ba_task = f"""
        [APPROVED OPPORTUNITY]
        {opportunity_description}
        
        [MVP SCOPE DECREED BY PO]
        {po_envelope.recommended_mvp_scope}
        
        Define measurable KPIs and data tracking requirements for this scope.
        """
        ba_envelope: BusinessMetricsEnvelope = workflow.run_agent(business_analyst, ba_task)

    # 3. TECH LEAD SANITY CHECK
    with workflow.lane("agent"):
        print("Running Tech Lead Sanity Check...")
        tl_task = f"""
        [APPROVED OPPORTUNITY]
        {opportunity_description}
        
        [MVP SCOPE DECREED BY PO]
        {po_envelope.recommended_mvp_scope}
        
        [LIFECYCLE PHASE]
        {po_envelope.target_lifecycle_phase}
        
        Evaluate technical feasibility against architectural invariants and outline high-level guardrails.
        """
        tl_envelope: TechSanityCheckEnvelope = workflow.run_agent(tech_lead, tl_task)

        if not tl_envelope.is_feasible:
            print("❌ Tech Lead rejected the Epic as unfeasible. Halting workflow.")
            return

    # 4. EPIC FORMATTING (Scrum Master)
    with workflow.lane("agent"):
        print("Running Scrum Master Epic Formatting...")
        sm_task = f"""
        Compile the following components into a cohesive Epic document.
        Save the document to `docs/epics/EPIC-[Feature_Name].md` using the `save_artifact` tool.
        
        [TITLE]
        {po_envelope.epic_title}
        
        [LIFECYCLE PHASE]
        {po_envelope.target_lifecycle_phase}
        
        [MVP SCOPE]
        {po_envelope.recommended_mvp_scope}
        
        [KPIs]
        {", ".join(ba_envelope.kpis)}
        [DATA REQUIREMENTS]
        {", ".join(ba_envelope.data_requirements)}
        
        [TECH GUARDRAILS]
        {", ".join(tl_envelope.architectural_guardrails)}
        [SECURITY RISKS]
        {", ".join(tl_envelope.security_risks)}
        """
        sm_envelope: EpicFormattingEnvelope = workflow.run_agent(scrum_master, sm_task, skills=["spec_driven"])

    # 5. EXECUTION PHASE (GitHub API Injection)
    with workflow.lane("code"):
        print(f"Epic document saved to {sm_envelope.epic_markdown_path}")
        
        run_shell_command(f"git add {sm_envelope.epic_markdown_path}")
        run_shell_command(f'git commit -m "docs: add Epic for {po_envelope.epic_title}"')

        # Determine repository name
        _, repo_name_raw, _ = run_shell_command("gh repo view --json nameWithOwner --jq .nameWithOwner")
        repo_name = repo_name_raw.strip() if repo_name_raw else ""
        
        epic_milestone_title = f"[Epic] [{po_envelope.target_lifecycle_phase}] {po_envelope.epic_title}"
        milestone_id_new = ""
        
        if repo_name:
            print(f"Creating Epic Milestone '{epic_milestone_title}' in GitHub...")
            # We inject the epic markdown content directly into the milestone description using a temp file
            import tempfile
            from pathlib import Path
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as f_desc:
                # We can also just read the written file
                f_desc.write(Path(sm_envelope.epic_markdown_path).read_text(encoding="utf-8"))
                temp_desc_path = f_desc.name

            _milestone_ok, milestone_number_raw, _milestone_err = run_shell_command(
                f'gh api repos/{repo_name}/milestones -f title="{epic_milestone_title}" -F description=@{temp_desc_path} --jq ".number"'
            )
            milestone_id_new = milestone_number_raw.strip() if milestone_number_raw else ""
            print(f"Created Epic Milestone ID: {milestone_id_new}")
            
            import os
            os.remove(temp_desc_path)

        if issue_id:
            # We transform the original opportunity issue into a milestone/epic anchor
            # Or we simply close it/add it to the milestone and change labels.
            print(f"Updating Original Opportunity Issue #{issue_id}...")
            # Remove apf:opportunity and apf:approved, add apf:epic_ready
            run_shell_command(f"gh issue edit {issue_id} --remove-label 'apf:opportunity,apf:approved' --add-label 'apf:epic_ready'")
            run_shell_command(f'gh issue edit {issue_id} --title "{epic_milestone_title}"')
            if milestone_id_new:
                run_shell_command(f'gh issue edit {issue_id} -m "{epic_milestone_title}"')
            
            print(f"Closing Original Opportunity Issue #{issue_id} as it is now converted into an Epic...")
            run_shell_command(f"gh issue close {issue_id} --reason completed")
        
    with workflow.lane("engineer"):
        print("Strategic distillation complete. The Opportunity is now an Epic ready for breakdown.")


if __name__ == "__main__":
    run("We need an AI agent to read repos.", "AI Platform")
