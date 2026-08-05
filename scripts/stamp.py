#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "agno>=2.8.6",
#     "pydantic>=2.13.4",
#     "rich>=15.0.0",
#     "pyyaml>=6.0.1",
#     "google-genai>=0.2.0",
#     "openai>=1.0.0",
# ]
# ///

"""
stamp.py - The ASSF Deployment Script and Inception Engine.
Injects the ASSF scaffold into the target repository and generates PROJECT_IDENTITY (AI.md).
"""

import argparse
import os
import shutil
import tarfile
import urllib.request
from pathlib import Path

from agno.agent import Agent
from agno.models.utils import get_model
from pydantic import BaseModel, Field
from rich.console import Console
from rich.prompt import Prompt

console = Console()

REPO_URL = "https://github.com/saulfernandez-me/agno-self-contain-software-factor/archive/refs/heads/main.tar.gz"


class InceptionOutput(BaseModel):
    """Structured output expected from the Inception Agent."""

    catalog_info_content: str = Field(
        description="The Backstage standard catalog-info.yaml content."
    )
    ai_md_content: str = Field(
        description="The complete high-density markdown content for AI.md based on the template."
    )


def fetch_scaffold(target_dir: Path) -> Path:
    """Fetches the scaffold templates. If developing locally, uses local paths. Otherwise downloads from GitHub."""
    # Check if running from within the assf repository itself (local dev)
    local_scaffold = (
        Path(__file__).resolve().parent.parent / "templates" / "assf_scaffold"
    )
    if local_scaffold.exists():
        console.print("[cyan]ℹ Using local templates/assf_scaffold[/cyan]")
        return local_scaffold

    # Otherwise, download the tarball (e.g., if run via `uv run https://...`)
    console.print("[cyan]ℹ Downloading ASSF scaffold from GitHub...[/cyan]")
    tar_path = target_dir / "assf_download.tar.gz"
    extract_dir = target_dir / ".assf_tmp_extract"

    urllib.request.urlretrieve(REPO_URL, tar_path)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=extract_dir)

    os.remove(tar_path)
    # The extracted folder is typically named agno-self-contain-software-factor-main
    extracted_repo = extract_dir / "agno-self-contain-software-factor-main"
    return extracted_repo / "templates" / "assf_scaffold"


def get_ai_template(scaffold_path: Path) -> str:
    template_path = scaffold_path / "AI_TEMPLATE.md"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return "Missing AI_TEMPLATE.md"


def run_inception_engine(target_dir: Path, scaffold_path: Path) -> None:
    """Runs the inception engine to generate AI.md and catalog-info.yaml."""
    console.print("[bold magenta]🚀 Booting ASSF Inception Engine...[/bold magenta]")

    readme_path = target_dir / "README.md"
    existing_catalog = target_dir / "catalog-info.yaml"

    is_brownfield = readme_path.exists() and len(readme_path.read_text()) > 50
    ai_template = get_ai_template(scaffold_path)

    agent = Agent(
        name="InceptionAgent",
        description="You are a Staff Platform Engineer onboarding a new project into the ASSF framework.",
        instructions=f"""
Your task is to generate two critical files:
1. `catalog-info.yaml` (Backstage standard format)
2. `AI.md` (High-density cognitive context for AI agents, following the provided template)

Here is the template for AI.md you MUST follow:
{ai_template}

Output the content matching the Pydantic schema perfectly.
""",
        output_schema=InceptionOutput,  # type: ignore[call-arg]
        model=get_model("google:gemini-2.5-flash"),
    )

    if is_brownfield:
        console.print(
            "[green]🔍 Brownfield repository detected. Reading context...[/green]"
        )
        context = f"README Context:\n{readme_path.read_text(encoding='utf-8')[:3000]}\n"
        if existing_catalog.exists():
            context += f"\nExisting Catalog Info:\n{existing_catalog.read_text(encoding='utf-8')}"

        prompt = f"Analyze this repository context and generate the required files:\n{context}"
    else:
        console.print(
            "[yellow]✨ Greenfield repository detected. Initiating interview...[/yellow]"
        )
        console.print("Please answer a few questions to build the Project Identity.")
        domain_type = Prompt.ask(
            "Domain type (e.g., Software Engineering, Agroforestry, RPG)"
        )
        purpose = Prompt.ask("Core purpose of the repository (1 sentence)")
        tech_stack = Prompt.ask(
            "Primary tech stack, languages, or tools (e.g., Python 3.10, FastAPI, uv)"
        )
        invariants = Prompt.ask(
            "Architectural invariants or hard rules (e.g., No ORMs, Hexagonal architecture)"
        )

        prompt = f"""
        User Interview Answers:
        - Domain: {domain_type}
        - Purpose: {purpose}
        - Tech Stack: {tech_stack}
        - Invariants: {invariants}
        
        Generate the required files based on these answers.
        """

    console.print("[cyan]⏳ Generating identity files...[/cyan]")
    try:
        response = agent.run(prompt)
        if not hasattr(response, 'data') or response.data is None:
            raise ValueError(f"Agent failed to generate structured data. Content: {getattr(response, 'content', 'None')}")
            
        output: InceptionOutput = response.data  # type: ignore

        # Write AI.md
        ai_md_path = target_dir / "AI.md"
        ai_md_path.write_text(output.ai_md_content, encoding="utf-8")
        console.print(f"[green]✓ Wrote {ai_md_path}[/green]")

        # Write catalog-info.yaml
        if not existing_catalog.exists():
            existing_catalog.write_text(output.catalog_info_content, encoding="utf-8")
            console.print(f"[green]✓ Wrote {existing_catalog}[/green]")
    except (OSError, ValueError, AttributeError) as e:
        console.print(f"[red]❌ Inception Engine failed to generate files: {e}[/red]")
        console.print(
            "[yellow]Please create AI.md and catalog-info.yaml manually.[/yellow]"
        )


def stamp_files(scaffold_path: Path, target_dir: Path) -> None:
    """Copies files from scaffold to target_dir."""
    console.print("[cyan]⏳ Stamping ASSF scaffold into repository...[/cyan]")

    # We want to copy everything EXCEPT AI_TEMPLATE.md (which is handled by Inception)
    for item in scaffold_path.iterdir():
        if item.name == "AI_TEMPLATE.md":
            continue

        dest = target_dir / item.name
        if item.is_dir():
            if dest.exists():
                # Merge directories instead of overwrite to preserve user files if rerunning
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copytree(item, dest)
        else:
            if not dest.exists():
                shutil.copy2(item, dest)

    console.print("[green]✓ Scaffold stamped successfully.[/green]")


def update_gitignore(target_dir: Path) -> None:
    """Ensures .context/data/telemetry.db and .env are gitignored."""
    gitignore = target_dir / ".gitignore"
    entries = ["\n# ASSF", ".env", ".context/data/"]

    if gitignore.exists():
        content = gitignore.read_text()
        for entry in entries:
            if entry.strip() and entry.strip() not in content:
                content += f"\n{entry}"
        gitignore.write_text(content)
    else:
        gitignore.write_text("\n".join(entries) + "\n")
    console.print("[green]✓ Updated .gitignore[/green]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ASSF Deployment Script (Stamper & Inception Engine)"
    )
    parser.add_argument(
        "--target", default=".", help="Target directory to stamp ASSF into."
    )
    args = parser.parse_args()

    target_dir = Path(args.target).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    scaffold_path = fetch_scaffold(target_dir)

    try:
        stamp_files(scaffold_path, target_dir)
        update_gitignore(target_dir)
        run_inception_engine(target_dir, scaffold_path)

        console.print("\n[bold green]🎉 ASSF Installation Complete! 🎉[/bold green]")
        console.print("""
[bold yellow]Next Steps:[/bold yellow]
1. Rename [cyan].env.example[/cyan] to [cyan].env[/cyan] and add your API keys.
2. Review the generated [cyan]AI.md[/cyan] and refine your Architectural Invariants.
3. Start using your ASSF agents via [cyan]uv run assf generate workflow ...[/cyan] or running your predefined workflows!
""")
    finally:
        # Cleanup temporary extraction directory if it was downloaded
        tmp_extract = target_dir / ".assf_tmp_extract"
        if tmp_extract.exists():
            shutil.rmtree(tmp_extract)


if __name__ == "__main__":
    main()
