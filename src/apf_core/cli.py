from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="APF Command Line Interface - The Generative Toolkit")
generate_app = typer.Typer(help="Auto-scaffold workflows and agents")
app.add_typer(generate_app, name="generate")

console = Console()


def get_base_dir() -> Path:
    """Determine the base directory. If we are developing the framework, use templates/apf_scaffold."""
    cwd = Path.cwd()
    scaffold_dir = cwd / "templates" / "apf_scaffold"
    return scaffold_dir if scaffold_dir.exists() else cwd


@generate_app.command("workflow")
def generate_workflow(
    name: str = typer.Argument(..., help="Name of the workflow (e.g., deploy_fix)"),
    agents: str = typer.Option(
        ..., help="Comma-separated list of agent names (e.g., scout,builder)"
    ),
) -> None:
    """Autogenerates the .mermaid graph and the _runner.py script for a new workflow."""
    base_dir = get_base_dir()
    workflows_dir = base_dir / "workflows"
    (workflows_dir / name).mkdir(parents=True, exist_ok=True)

    agent_list = [a.strip() for a in agents.split(",")]

    # Generate Mermaid
    mermaid_nodes = "\n        ".join(
        [f'{a.upper()}["{a}: Execute {a} task"]:::agent' for a in agent_list]
    )
    mermaid_connections = "\n    ".join(
        [
            f"{agent_list[i].upper()} --> {agent_list[i + 1].upper()}"
            for i in range(len(agent_list) - 1)
        ]
    )
    if agent_list:
        mermaid_connections += f"\n    {agent_list[-1].upper()} --> GATE"

    mermaid_content = f"""graph TD
    %% APF Visual Standard v2.0 Color Palette
    classDef agent fill:#0f5132,stroke:#0dfd8a,stroke-width:2px,color:#fff,rx:5px,ry:5px
    classDef code fill:#2d1b22,stroke:#ff4d4f,stroke-width:2px,color:#fff,stroke-dasharray:5 5,rx:3px,ry:3px
    classDef human fill:#1a365d,stroke:#3182ce,stroke-width:2px,color:#fff,rx:5px,ry:5px

    %% Workflow: {name}
    
    subgraph "🤖 LANE: AGENT (Cognition)"
        {mermaid_nodes}
    end
    
    subgraph "⚙️ LANE: CODE (Deterministic)"
        GATE{{"✅ assert: validation gate"}}:::code
    end
    
    {mermaid_connections}
"""

    mermaid_path = workflows_dir / name / "graph.mermaid"
    mermaid_path.write_text(mermaid_content)

    # Generate Python Runner
    imports = "\n".join(
        [
            f"from src.agents.{a} import get_{a}_agent  # type: ignore[import-not-found]"
            for a in agent_list
        ]
    )
    instantiations = "\n    ".join(
        [
            f'{a} = get_{a}_agent(domain_context, "Task for {a}", EnvelopeBase)'
            for a in agent_list
        ]
    )

    execution_blocks = ""
    for a in agent_list:
        execution_blocks += f"""
    with workflow.lane("agent"):
        print("Running {a}...")
        {a}_response = {a}_response = workflow.run_agent(, "Execute {a} tasks.")
        {a}_envelope = {a}_response.data
"""

    runner_content = f"""from apf_core.workflow import ApfWorkflow  # type: ignore[import-not-found]
from apf_core.assert_gates import run_shell_command  # type: ignore[import-not-found]
from apf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
{imports}

def run_{name}(task_description: str, domain_context: str) -> None:
    \"\"\"Generated runner for {name} workflow.\"\"\"
    workflow = ApfWorkflow(name="{name}")
    
    # Instantiate agents
    {instantiations}
    
    # Execution Flow{execution_blocks}
    # Verification Gate
    with workflow.lane("code"):
        success, stdout, stderr = run_shell_command("echo 'Validation passed'")
        
    if not success:
        print("Gate failed!")
        # TODO: Implement correction loop here
        
if __name__ == "__main__":
    run_{name}("Do the task", "You are in an APF repository.")
"""

    runner_path = workflows_dir / name / "runner.py"
    runner_path.write_text(runner_content)

    console.print(f"[green]✓ Generated Workflow:[/green] {mermaid_path}")
    console.print(f"[green]✓ Generated Runner:[/green] {runner_path}")


@app.command("process")
def process(
    issue_number: int = typer.Argument(..., help="The GitHub Issue number to process."),
) -> None:
    """End-to-end processing of a GitHub Issue autonomously."""
    from apf_core.daemon import process_target

    process_target(issue_number)


@app.command("discover")
def discover(
    domain: str = typer.Argument(..., help="The target domain or area to research for new opportunities."),
    topic: str = typer.Option("", help="Optional specific topic or focus area to direct the research."),
) -> None:
    """Run the Product Discovery workflow to find new opportunities."""
    from pathlib import Path
    import sys
    import importlib.util

    console.print(f"[bold magenta]🚀 Starting APF Discovery for domain: {domain}...[/bold magenta]")
    
    runner_script = Path("workflows/product_discovery/runner.py")
    if not runner_script.exists():
        console.print(f"[red]❌ Workflow script not found at {runner_script}. Are you in an APF-stamped repository?[/red]")
        sys.exit(1)

    try:
        cwd = str(Path.cwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)

        spec = importlib.util.spec_from_file_location("runner", str(runner_script))
        if spec and spec.loader:
            runner_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(runner_module)

            ai_md_path = Path("AI.md")
            domain_context = (
                ai_md_path.read_text(encoding="utf-8")
                if ai_md_path.exists()
                else "Standard context"
            )

            if hasattr(runner_module, "run"):
                run_func = runner_module.run
                # Check if the run function accepts the topic argument
                import inspect
                sig = inspect.signature(run_func)
                if "topic" in sig.parameters:
                    run_func(target_domain=domain, domain_context=domain_context, topic=topic)
                else:
                    run_func(domain, domain_context)
            else:
                console.print("[red]❌ Could not find an entrypoint ('run' function) in the workflow script.[/red]")
                sys.exit(1)

    except Exception as e:
        console.print(f"[red]❌ Discovery workflow execution failed: {e}[/red]")
        sys.exit(1)


@app.command("process-epic")
def process_epic(
    milestone_id: int = typer.Argument(..., help="The GitHub Milestone ID to process as an Epic."),
) -> None:
    """End-to-end processing of a GitHub Milestone (Epic) autonomously."""
    from apf_core.daemon import process_target

    process_target(milestone_id, is_milestone=True)


@generate_app.command("agent")
def generate_agent(
    name: str = typer.Argument(..., help="Name of the agent (e.g., translator)"),
) -> None:
    """Autogenerates a new src/agents/<name>.py file with Agno boilerplate and an EnvelopeBase class."""
    base_dir = get_base_dir()
    agents_dir = base_dir / "src" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    class_name = name.title().replace("_", "")

    agent_content = f"""from typing import Type
from pydantic import BaseModel, Field
from agno.agent import Agent

from apf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]


class {class_name}Envelope(EnvelopeBase):
    \"\"\"Specific envelope for the {class_name} phase.\"\"\"
    # TODO: Add specific fields for this agent's contract
    pass


def get_{name.lower()}_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: Type[BaseModel] = {class_name}Envelope,
    model_tier: str = "workhorse",
) -> Agent:
    \"\"\"
    Factory for the {class_name} Agent.
    
    Role:
        TODO: Describe the agent's role here.
        
    Capabilities:
        TODO: List the tools given to this agent.
    \"\"\"
    return Agent(
        name="{class_name}",
        model=model_tier,  # type: ignore[arg-type]
        description="You are a {class_name}. TODO: Add description.",
        instructions=f"[DOMAIN CONTEXT]\\n{{domain_context}}\\n\\n[TASK]\\n{{task_instructions}}",
        tools=[],  # TODO: Add specific tools
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
    )
"""

    agent_path = agents_dir / f"{name.lower()}.py"
    if agent_path.exists():
        console.print(
            f"[yellow]⚠ Agent {agent_path} already exists. Skipping.[/yellow]"
        )
        return

    agent_path.write_text(agent_content)
    console.print(f"[green]✓ Generated Agent:[/green] {agent_path}")


if __name__ == "__main__":
    app()
