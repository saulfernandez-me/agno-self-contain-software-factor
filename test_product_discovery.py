import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Mock DuckDuckGoTools and BraveSearchTools before anything imports it
import sys as _sys
_mock_tool = MagicMock()
_sys.modules['agno.tools.duckduckgo'] = _mock_tool
_sys.modules['agno.tools.websearch'] = _mock_tool
_sys.modules['agno.tools.bravesearch'] = _mock_tool

# Setup paths to import apf_core and the apf_scaffold templates
sys.path.insert(0, str(Path.cwd() / "src"))
sys.path.insert(0, str(Path.cwd() / "templates" / "apf_scaffold"))

from workflows.product_discovery.runner import run
from workflows.product_discovery.envelopes import (
    MarketResearchEnvelope,
    UXResearchEnvelope,
    ProductDiscoveryEnvelope,
    OpportunitySchema
)

def test_product_discovery_workflow():
    print("🚀 Starting Product Discovery Workflow Test...")

    call_prompts = {}
    
    # Mocking the workflow agent execution
    def mock_run_agent(self, agent, prompt, skills=None):
        call_prompts[agent.name] = prompt
        
        if agent.name == "Market Researcher":
            print("[TEST] Market Researcher returning simulated trends...")
            return MarketResearchEnvelope(
                status="success", summary="Mock", notes_for_next_agent="Mock",
                market_trends=["AI coding assistants", "Autonomous agents"],
                competitor_gaps=["Lack of deep codebase understanding"],
                macro_opportunities=["Agentic CI/CD pipelines"]
            )
        elif agent.name == "User Advocate":
            print("[TEST] User Advocate returning simulated user pains...")
            return UXResearchEnvelope(
                status="success", summary="Mock", notes_for_next_agent="Mock",
                user_pain_points=["Devs spend too much time reviewing PRs"],
                unmet_needs=["Automated deep semantic PR reviews"],
                ux_opportunities=["AI agent that reads entire repo context for reviews"]
            )
        elif agent.name == "Product Strategist":
            print("[TEST] Product Strategist returning simulated opportunity...")
            return ProductDiscoveryEnvelope(
                status="success", summary="Mock", notes_for_next_agent="Mock",
                strategic_summary="AI agents are the future of PR reviews.",
                opportunities=[
                    OpportunitySchema(
                        title="Autonomous PR Reviewer",
                        problem_statement="Devs waste time on manual PR reviews.",
                        potential_value_roi="Save 10 hours/week per dev.",
                        target_audience="Software Engineers and Tech Leads.",
                        epic_size="size: L",
                        thematic_labels=["ai", "ci-cd"]
                    )
                ]
            )

    # Mocking the shell execution to avoid GitHub API calls
    shell_calls = []
    def mock_run_shell_command(cmd, **kwargs):
        shell_calls.append(cmd)
        if "gh repo view" in cmd:
            return True, "saulfernandez-me/test-repo", ""
        elif "gh api repos/saulfernandez-me/test-repo/milestones --jq" in cmd:
            # Simulate that the milestone does not exist yet
            return True, "", ""
        elif "gh api repos/saulfernandez-me/test-repo/milestones -f title" in cmd:
            # Simulate creating the milestone
            return True, "42", ""
        elif "gh label create" in cmd:
            return True, "", ""
        elif "gh issue create" in cmd:
            return True, "", ""
        return True, "", ""

    with patch("apf_core.workflow.ApfWorkflow.run_agent", new=mock_run_agent):
        with patch("workflows.product_discovery.runner.run_shell_command", side_effect=mock_run_shell_command):
            # Run the workflow
            run("AI Platform Engineering", "Software Engineering Domain", topic="Portfolio management and wallets")

    print("\n🔍 Validating Workflow Execution:")
    
    assert "Market Researcher" in call_prompts, "Market Researcher was not called"
    assert "User Advocate" in call_prompts, "User Advocate was not called"
    assert "Product Strategist" in call_prompts, "Product Strategist was not called"
    print("   ✅ All cognitive agents were executed.")
    
    # Validate that topic was injected
    market_prompt = call_prompts["Market Researcher"]
    assert "Portfolio management and wallets" in market_prompt, "Topic focus was not passed to Market Researcher"
    print("   ✅ Topic focus correctly injected into Market Researcher prompt.")
    
    # Validate that the outputs from previous agents were passed to the next
    ux_prompt = call_prompts["User Advocate"]
    assert "AI coding assistants" in ux_prompt, "Market trends not passed to UX agent"
    print("   ✅ Hand-off from Market Researcher to User Advocate verified.")
    
    pm_prompt = call_prompts["Product Strategist"]
    assert "Devs spend too much time reviewing PRs" in pm_prompt, "User pains not passed to PM agent"
    print("   ✅ Hand-off from User Advocate to Product Strategist verified.")
    
    # Validate GitHub Shell Commands
    issue_created = False
    milestone_checked = False
    for cmd in shell_calls:
        if "gh api repos/saulfernandez-me/test-repo/milestones" in cmd:
            milestone_checked = True
        if "gh issue create --title \"Autonomous PR Reviewer\"" in cmd and "--milestone \"42\"" in cmd and "size: L" in cmd:
            issue_created = True

    assert milestone_checked, "Milestone creation/check was not executed."
    print("   ✅ GitHub Milestone tracking verified.")
    
    assert issue_created, "Opportunity Issue creation command was not constructed correctly."
    print("   ✅ GitHub Opportunity Issue creation with correct labels and milestone verified.")
    
    print("\n🎉 SUCCESS: The product_discovery workflow functions perfectly end-to-end!")
    return True

if __name__ == "__main__":
    try:
        test_product_discovery_workflow()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
