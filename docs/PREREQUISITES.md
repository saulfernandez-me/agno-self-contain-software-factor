# 📋 APF Prerequisites & System Dependencies

To maintain a "Zero-Trust" security posture for LLMs and guarantee lightning-fast environment isolation, the **Agno Product Factory (APF)** delegates critical operations to native host binaries rather than using pure Python HTTP clients.

Before stamping or running APF on a new machine, VM, or CI/CD container, the following dependencies **MUST** be installed and configured.

---

## 1. Astral `uv` (The Package Manager)
APF bypasses traditional `pip` and `virtualenv` bottlenecks by using [uv](https://github.com/astral-sh/uv), an extremely fast Python package and project manager written in Rust.

*   **Why it's required:** The APF Stamper script, the Daemon, and all workflow runners are executed via `uv run`. This guarantees that dependencies (like Agno or Pydantic) are isolated and version-locked without manual environment setup.
*   **Installation:**
    ```bash
    # macOS / Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

## 2. GitHub CLI `gh` (The Control Plane)
APF does not manage GitHub API tokens directly in `.env` files for repository operations. Instead, it acts as a wrapper around the official [GitHub CLI](https://cli.github.com/).

*   **Why it's required:** The `GitHubTools` and the `daemon.py` script execute shell commands (e.g., `gh issue view`, `gh pr create`) to transition states, fetch task context, and deliver code. This ensures the LLM never has access to your raw GitHub token, and all commits/PRs are signed with your true developer identity.
*   **Installation:**
    ```bash
    # macOS
    brew install gh
    
    # Debian/Ubuntu
    sudo apt install gh
    ```
*   **Crucial Authentication Step:** APF will silently fail if `gh` is installed but not authenticated. You MUST run:
    ```bash
    gh auth login
    ```
    Ensure you select `HTTPS` or `SSH` according to your Git configuration, and grant permissions for "repositories" and "workflow".

## 3. Python 3.10+
APF's underlying Agno SDK and the Pydantic type-hinting engine require modern Python features.

---

## 🛑 Troubleshooting 

If you encounter errors like `Function execute_shell_command not found` or `Error fetching issue: gh command not found`, it strictly means the executing environment lacks the `gh` binary in its `$PATH` or the user has not executed `gh auth login`.
