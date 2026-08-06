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


def process_issue(issue_number: int) -> None:
    """End-to-end processing of a GitHub Issue autonomously."""
    console.print(
        f"[bold magenta]🚀 Starting APF Daemon for Issue #{issue_number}...[/bold magenta]"
    )

    # 1. Fetch Issue Data
    console.print("[cyan]📥 Fetching issue data from GitHub...[/cyan]")
    ok, stdout, stderr = run_cmd(
        ["gh", "issue", "view", str(issue_number), "--json", "title,body,labels"]
    )
    if not ok:
        console.print(f"[red]❌ Failed to fetch issue #{issue_number}: {stderr}[/red]")
        sys.exit(1)

    import json

    issue_data = json.loads(stdout)
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")

    # Check if it's already in the backlog or if we just want to force run it
    labels = [l.get("name") for l in issue_data.get("labels", [])]
    if "apf:backlog" in labels:
        run_cmd(
            [
                "gh",
                "issue",
                "edit",
                str(issue_number),
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
            ["gh", "issue", "edit", str(issue_number), "--add-label", "apf:planning"]
        )

    # 2. Git Automation (Create Branch)
    # Sanitize title for branch name
    import re

    clean_title = re.sub(r"[^a-zA-Z0-9]", "-", title.lower())
    clean_title = re.sub(r"-+", "-", clean_title).strip("-")
    branch_name = f"feat/issue-{issue_number}-{clean_title}"

    console.print(f"[cyan]🌿 Creating and checking out branch: {branch_name}[/cyan]")
    ok, _, stderr = run_cmd(["git", "checkout", "-b", branch_name])
    if not ok:
        # Might already exist
        run_cmd(["git", "checkout", branch_name])

    # 3. Execution (Running the standard PDLC workflow)
    console.print("[cyan]⚙️ Executing standard PDLC workflow...[/cyan]")

    # Change label to implementing
    run_cmd(
        [
            "gh",
            "issue",
            "edit",
            str(issue_number),
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

            # Assuming the runner has a function named run_full_pdlc or run_workflow
            # We standardize calling convention. Let's look for a function that starts with 'run_'
            run_func = None
            for attr_name in dir(runner_module):
                if attr_name.startswith("run_"):
                    run_func = getattr(runner_module, attr_name)
                    break

            if run_func:
                run_func(task_instruction, domain_context)
            else:
                console.print(
                    "[red]❌ Could not find a run_* function in the workflow script.[/red]"
                )
                sys.exit(1)

    except (OSError, ValueError, TypeError, KeyError) as e:
        console.print(f"[red]❌ Workflow execution failed: {e}[/red]")
        run_cmd(
            ["gh", "issue", "edit", str(issue_number), "--add-label", "apf:blocked"]
        )
        sys.exit(1)

    # 4. Delivery (Commit, Push, PR)
    console.print("[cyan]📦 Workflow completed. Preparing delivery...[/cyan]")
    run_cmd(
        [
            "gh",
            "issue",
            "edit",
            str(issue_number),
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
            f"feat: implement issue #{issue_number} autonomous resolution",
        ]
    )

    console.print("[cyan]☁️ Pushing to remote...[/cyan]")
    run_cmd(["git", "push", "-u", "origin", branch_name])

    console.print("[cyan]🔗 Creating Pull Request...[/cyan]")
    ok, pr_url, stderr = run_cmd(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"feat: Resolve Issue #{issue_number} ({title})",
            "--body",
            f"Autonomous resolution of #{issue_number} by APF agents.\n\nCloses #{issue_number}",
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
        "issue_number", type=int, help="The GitHub Issue number to process."
    )
    args = parser.parse_args()

    process_issue(args.issue_number)


if __name__ == "__main__":
    main()
