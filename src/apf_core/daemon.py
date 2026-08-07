import argparse
import subprocess
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def run_cmd(cmd: list[str], cwd: str = ".") -> tuple[bool, str, str]:
    """Execute a shell command and return success status and output."""
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
        return res.returncode == 0, res.stdout.strip(), res.stderr.strip()
    except (OSError, ValueError, TypeError, KeyError) as e:
        return False, "", str(e)


def process_target(target_id: int, is_milestone: bool = False) -> None:
    """End-to-end processing of a GitHub Issue or Milestone autonomously."""
    target_type = "Milestone" if is_milestone else "Issue"
    console.print(
        f"[bold magenta]🚀 Starting APF Daemon for {target_type} #{target_id}...[/bold magenta]"
    )

    # 1. Fetch Target Data
    console.print(f"[cyan]📥 Fetching {target_type.lower()} data from GitHub...[/cyan]")
    import json

    if is_milestone:
        _, repo_name, _ = run_cmd(
            ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"]
        )
        if not repo_name:
            console.print("[red]❌ Failed to fetch repository name.[/red]")
            sys.exit(1)

        ok, stdout, stderr = run_cmd(
            ["gh", "api", f"repos/{repo_name}/milestones/{target_id}"]
        )
        if not ok:
            console.print(
                f"[red]❌ Failed to fetch milestone #{target_id}: {stderr}[/red]"
            )
            sys.exit(1)

        target_data = json.loads(stdout)
        title = target_data.get("title", "")
        # The title contains "[Epic] Epic Name", we'll strip "[Epic] " if present
        title = title.removeprefix("[Epic] ")
        body = target_data.get("description", "")
        labels = []  # Milestones don't use issues' labels
    else:
        ok, stdout, stderr = run_cmd(
            ["gh", "issue", "view", str(target_id), "--json", "title,body,labels"]
        )
        if not ok:
            console.print(f"[red]❌ Failed to fetch issue #{target_id}: {stderr}[/red]")
            sys.exit(1)

        target_data = json.loads(stdout)
        title = target_data.get("title", "")
        body = target_data.get("body", "")
        labels = [l.get("name") for l in target_data.get("labels", [])]

    # Handle Issue-specific logic (Labels & Branching)
    if not is_milestone:
        if "apf:backlog" in labels:
            run_cmd(
                [
                    "gh",
                    "issue",
                    "edit",
                    str(target_id),
                    "--remove-label",
                    "apf:backlog",
                    "--add-label",
                    "apf:planning",
                ]
            )
        else:
            console.print(
                "[yellow]⚠ Issue is not in apf:backlog. Proceeding anyway...[/yellow]"
            )
            run_cmd(
                ["gh", "issue", "edit", str(target_id), "--add-label", "apf:planning"]
            )

        # 2. Git Automation (Create Branch)
        import re

        clean_title = re.sub(r"[^a-zA-Z0-9]", "-", title.lower())
        clean_title = re.sub(r"-+", "-", clean_title).strip("-")
        branch_name = f"feat/issue-{target_id}-{clean_title}"

        console.print(
            f"[cyan]🌿 Creating and checking out branch: {branch_name}[/cyan]"
        )
        ok, _, stderr = run_cmd(["git", "checkout", "-b", branch_name])
        if not ok:
            run_cmd(["git", "checkout", branch_name])
    else:
        branch_name = "main"  # Milestones don't branch

    # 3. Execution
    console.print(f"[cyan]⚙️ Executing workflow for {target_type}...[/cyan]")

    if not is_milestone:
        # Change label to implementing
        run_cmd(
            [
                "gh",
                "issue",
                "edit",
                str(target_id),
                "--remove-label",
                "apf:planning",
                "--add-label",
                "apf:implementing",
            ]
        )

    # We call the python runner. We assume the workflows folder exists in the target repo.
    runner_script = Path("workflows/full_pdlc/runner.py")
    if not runner_script.exists():
        console.print(
            f"[red]❌ Workflow script not found at {runner_script}. Are you in an APF-stamped repository?[/red]"
        )
        sys.exit(1)

    # We pass the issue body to the runner via an environment variable or temp file
    # To keep it simple, we modify the runner or just pass it as an argument if supported.
    # Since our standard runners are hardcoded at the bottom in if __name__ == "__main__",
    # we might need to import it and call it directly.
    try:
        # Dynamically import the runner module
        import importlib.util

        spec = importlib.util.spec_from_file_location("runner", str(runner_script))
        if spec and spec.loader:
            runner_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(runner_module)

            # Read AI.md for context
            ai_md_path = Path("AI.md")
            domain_context = (
                ai_md_path.read_text(encoding="utf-8")
                if ai_md_path.exists()
                else "Standard context"
            )

            # Change label to testing during execution? The workflow itself could do this,
            # but we'll let the daemon handle the macro states for now.
            # Run the workflow
            task_instruction = f"Issue Title: {title}\nIssue Body:\n{body}"

            # Since the component-based refactor, the entrypoint is simply 'run'
            if hasattr(runner_module, "run"):
                run_func = runner_module.run
                run_func(task_instruction, domain_context)
            else:
                # Fallback for older flat scripts
                run_func = None
                for attr_name in dir(runner_module):
                    if (
                        attr_name.startswith("run_")
                        and attr_name != "run_shell_command"
                    ):
                        run_func = getattr(runner_module, attr_name)
                        break

                if run_func:
                    run_func(task_instruction, domain_context)
                else:
                    console.print(
                        "[red]❌ Could not find an entrypoint ('run' function) in the workflow script.[/red]"
                    )
                    sys.exit(1)

    except (OSError, ValueError, TypeError, KeyError) as e:
        console.print(f"[red]❌ Workflow execution failed: {e}[/red]")
        run_cmd(
            ["gh", "issue", "edit", str(target_id), "--add-label", "apf:blocked"]
        )
        sys.exit(1)

    # 4. Delivery (Commit, Push, PR)
    console.print("[cyan]📦 Workflow completed. Preparing delivery...[/cyan]")
    run_cmd(
        [
            "gh",
            "issue",
            "edit",
            str(target_id),
            "--remove-label",
            "apf:implementing",
            "--add-label",
            "apf:reviewing",
        ]
    )

    ok, status_out, _ = run_cmd(["git", "status", "--porcelain"])
    if not status_out:
        console.print("[yellow]⚠ No changes were made by the agents.[/yellow]")
        sys.exit(0)

    run_cmd(["git", "add", "."])
    run_cmd(
        [
            "git",
            "commit",
            "-m",
            f"feat: implement issue #{target_id} autonomous resolution",
        ]
    )

    console.print("[cyan]☁️ Pushing to remote...[/cyan]")
    run_cmd(["git", "push", "-u", "origin", branch_name])

    _, repo_view_out, _ = run_cmd(
        [
            "gh",
            "repo",
            "view",
            "--json",
            "defaultBranchRef",
            "--jq",
            ".defaultBranchRef.name",
        ]
    )
    if repo_view_out:
        repo_view_out.strip()

    console.print("[cyan]🔗 Creating Pull Request...[/cyan]")
    ok, pr_url, stderr = run_cmd(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"feat: Resolve Issue #{target_id} ({title})",
            "--body",
            f"Autonomous resolution of #{target_id} by APF agents.\n\nCloses #{target_id}",
            "--base",
            "main",
        ]
    )

    if ok:
        console.print(
            f"[bold green]🎉 Success! Pull Request created: {pr_url}[/bold green]"
        )
    else:
        console.print(f"[red]❌ Failed to create PR: {stderr}[/red]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="APF GitOps Daemon - Autonomous Issue Processor"
    )
    parser.add_argument(
        "target_id", type=int, help="The GitHub Issue number to process."
    )
    args = parser.parse_args()

    process_target(args.target_id)


if __name__ == "__main__":
    main()
