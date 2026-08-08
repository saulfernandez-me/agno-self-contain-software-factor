import subprocess
import sys
from typing import Any

from agno.models.utils import get_model


def resolve_model(model_ref: Any) -> Any:
    """
    Resolves a model reference into an instantiated Agno Model object.
    Supports native Agno strings (e.g., 'openai:gpt-4o') and our custom Zero-Config
    providers (e.g., 'github:gpt-4o').
    """
    if not isinstance(model_ref, str):
        return model_ref

    if model_ref.startswith("github:"):
        model_id = model_ref.split(":", 1)[1]

        # Zero-Config Authentication: Extract the gh auth token
        try:
            res = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True, check=False
            )
            if res.returncode != 0:
                print(
                    f"[red]❌ GitHub Models Authentication Failed: {res.stderr}[/red]"
                )
                print(
                    "[yellow]Please run `gh auth login` to use the 'github:' provider.[/yellow]"
                )
                sys.exit(1)

            gh_token = res.stdout.strip()

            from agno.models.openai import OpenAIChat

            return OpenAIChat(
                id=model_id,
                api_key=gh_token,
                base_url="https://models.inference.ai.azure.com",
            )
        except OSError:
            print(
                "[red]❌ 'gh' CLI not found. Cannot use 'github:' models without it.[/red]"
            )
            sys.exit(1)

    # Fallback to standard Agno model resolution
    return get_model(model_ref)
