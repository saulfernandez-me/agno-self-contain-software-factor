from src.agents.market_researcher import get_market_researcher_agent  # type: ignore[import-not-found]
from src.agents.user_advocate import get_user_advocate_agent  # type: ignore[import-not-found]
from src.agents.product_strategist import get_product_strategist_agent  # type: ignore[import-not-found]

from workflows.product_discovery.envelopes import (  # type: ignore[import-not-found]
    MarketResearchEnvelope,
    UXResearchEnvelope,
    ProductDiscoveryEnvelope,
)

from apf_core.assert_gates import run_shell_command
from apf_core.workflow import ApfWorkflow


def run(target_domain: str, domain_context: str, topic: str = "") -> None:
    """
    Executes the Product Discovery workflow: Market Research -> UX Research -> Strategic Synthesis -> Opportunity Issues.
    """
    workflow = ApfWorkflow(name="product_discovery")

    market_researcher = get_market_researcher_agent(
        domain_context,
        "Act as the Market Researcher. Analyze current market trends, competitor features, and state-of-the-art developments to discover new opportunities.",
        MarketResearchEnvelope,
    )

    user_advocate = get_user_advocate_agent(
        domain_context,
        "Act as the User Advocate. Identify UX frictions and unmet user needs in the current landscape.",
        UXResearchEnvelope,
    )

    product_strategist = get_product_strategist_agent(
        domain_context,
        "Act as the Product Strategist. Synthesize market and UX research into 1-3 concrete, high-ROI business opportunities.",
        ProductDiscoveryEnvelope,
    )

    # 1. MARKET RESEARCH PHASE
    with workflow.lane("agent"):
        print("Running Market Researcher Analysis...")
        if topic:
            market_task = f"Analyze the domain: {target_domain} with a specific focus on: '{topic}'. What are the macro opportunities and competitor gaps?"
        else:
            market_task = f"Analyze the domain: {target_domain}. What are the macro opportunities and competitor gaps?"
        market_envelope: MarketResearchEnvelope = workflow.run_agent(market_researcher, market_task, skills=["web_access"])

    # 2. UX RESEARCH PHASE
    with workflow.lane("agent"):
        print("Running User Advocate Translation...")
        ux_task = f"""
        [DOMAIN FOCUS]
        {target_domain}
        
        [MARKET TRENDS & COMPETITOR GAPS]
        Trends: {", ".join(market_envelope.market_trends)}
        Gaps: {", ".join(market_envelope.competitor_gaps)}
        Opportunities: {", ".join(market_envelope.macro_opportunities)}
        
        Given these market dynamics, identify specific user pain points and unmet needs that we can solve.
        """
        ux_envelope: UXResearchEnvelope = workflow.run_agent(user_advocate, ux_task)

    # 3. STRATEGIC SYNTHESIS PHASE
    with workflow.lane("agent"):
        print("Running Product Strategist Synthesis...")
        pm_task = f"""
        [DOMAIN FOCUS]
        {target_domain}
        
        [MARKET OPPORTUNITIES]
        {", ".join(market_envelope.macro_opportunities)}
        
        [USER PAIN POINTS & UNMET NEEDS]
        Pains: {", ".join(ux_envelope.user_pain_points)}
        Needs: {", ".join(ux_envelope.unmet_needs)}
        
        Synthesize these findings into 1 to 3 concrete Opportunity Proposals (Epics). Be sure to assign a realistic T-Shirt size to each.
        """
        discovery_envelope: ProductDiscoveryEnvelope = workflow.run_agent(product_strategist, pm_task)

    # 4. EXECUTION PHASE (GitHub API Injection)
    with workflow.lane("code"):
        milestone_title = "Product Discovery"
        
        print(f"Ensuring Milestone '{milestone_title}' exists in GitHub...")
        
        # Determine repository name
        _, repo_name_raw, _ = run_shell_command(
            "gh repo view --json nameWithOwner --jq .nameWithOwner"
        )
        repo_name = repo_name_raw.strip() if repo_name_raw else ""
        
        milestone_number = ""
        if repo_name:
            # Check if milestone exists
            ok, existing_milestones_raw, _ = run_shell_command(
                f'gh api repos/{repo_name}/milestones --jq ".[] | select(.title == \\"{milestone_title}\\") | .number"'
            )
            existing_milestones = existing_milestones_raw.strip() if existing_milestones_raw else ""
            
            if existing_milestones:
                milestone_number = existing_milestones.split()[0]
                print(f"Found existing Product Discovery milestone ID: {milestone_number}")
            else:
                print("Creating new Product Discovery milestone...")
                _milestone_ok, milestone_number_raw, _milestone_err = run_shell_command(
                    f'gh api repos/{repo_name}/milestones -f title="{milestone_title}" --jq ".number"'
                )
                milestone_number = milestone_number_raw.strip() if milestone_number_raw else ""
                
        milestone_flag = f'--milestone "{milestone_number}"' if milestone_number else ""

        print(f"Creating {len(discovery_envelope.opportunities)} opportunity issues in GitHub...")
        success_count = 0
        for opp in discovery_envelope.opportunities:
            import tempfile

            markdown_body = f"""### 🎯 Opportunity: {opp.title}

#### 🛑 Problem Statement
{opp.problem_statement}

#### 💰 Potential Value / ROI
{opp.potential_value_roi}

#### 👥 Target Audience
{opp.target_audience}

---
*Generated autonomously by the APF Product Discovery workflow.*
*To proceed with this Epic, a human must add the `apf:approved` label.*
"""

            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md") as f:
                f.write(markdown_body)
                temp_path = f.name

            # Labels
            all_labels = ["apf:opportunity", opp.epic_size] + opp.thematic_labels
            for label in all_labels:
                run_shell_command(f'gh label create "{label}"')

            labels_flag = ",".join(all_labels)
            issue_title = f"{opp.title}"

            # Fire the command
            ok, _stdout, stderr = run_shell_command(
                f'gh issue create --title "{issue_title}" --body-file "{temp_path}" --label "{labels_flag}" {milestone_flag}'
            )

            import os
            os.remove(temp_path)

            if ok:
                success_count += 1
                print(f"Created opportunity issue: {issue_title}")
            else:
                print(f"Failed to create issue '{issue_title}': {stderr}")

        if success_count == len(discovery_envelope.opportunities):
            print("Successfully populated the Product Discovery board.")
        else:
            print("Warning: Some opportunity issues failed to create.")

    # 5. HALT
    with workflow.lane("engineer"):
        print(
            "Product Discovery complete. Check your GitHub project board for the new apf:opportunity issues."
        )


if __name__ == "__main__":
    # Example execution
    run("Generative AI for Platform Engineering", "You are in an AI agent platform repository.")
