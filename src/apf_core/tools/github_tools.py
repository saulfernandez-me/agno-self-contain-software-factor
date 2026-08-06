import subprocess

from agno.tools import Toolkit


class GitHubTools(Toolkit):
    """
    Agno Toolkit for APF Github PDLC integration.
    Allows agents to read issues, apply lifecycle labels, and review PRs.
    Assumes `gh` CLI is installed and authenticated in the host environment.
    """

    def __init__(self) -> None:
        super().__init__(name="github_tools")
        self.register(self.get_issue)
        self.register(self.add_label)
        self.register(self.read_pr_diff)

    def get_issue(self, issue_number: int) -> str:
        """
        Reads the title, body, and current labels of a GitHub issue.

        Args:
            issue_number: The number of the GitHub issue.

        Returns:
            JSON string containing issue details or an error message.
        """
        try:
            res = subprocess.run(
                [
                    "gh",
                    "issue",
                    "view",
                    str(issue_number),
                    "--json",
                    "title,body,labels",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode != 0:
                return f"Error fetching issue {issue_number}: {res.stderr}"
            return res.stdout
        except OSError as e:
            return f"Failed to execute gh cli: {e}"

    def add_label(self, issue_number: int, label: str) -> str:
        """
        Adds a label to a GitHub issue. Useful for APF state transitions (e.g. apf:planning).

        Args:
            issue_number: The number of the GitHub issue.
            label: The label to add (e.g., "apf:planning").

        Returns:
            Success or error message.
        """
        try:
            res = subprocess.run(
                ["gh", "issue", "edit", str(issue_number), "--add-label", label],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode != 0:
                return f"Error adding label {label}: {res.stderr}"
            return f"Successfully added label '{label}' to issue #{issue_number}."
        except OSError as e:
            return f"Failed to execute gh cli: {e}"

    def read_pr_diff(self, pr_number: int) -> str:
        """
        Reads the raw diff of a GitHub Pull Request for adversarial review.

        Args:
            pr_number: The number of the Pull Request.

        Returns:
            The PR diff or an error message.
        """
        try:
            res = subprocess.run(
                ["gh", "pr", "diff", str(pr_number)],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode != 0:
                return f"Error fetching PR diff {pr_number}: {res.stderr}"
            return res.stdout
        except OSError as e:
            return f"Failed to execute gh cli: {e}"
