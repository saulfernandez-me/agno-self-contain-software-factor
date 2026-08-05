import json
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError


def assert_file_exists(path: str) -> bool:
    """Assert that a physical file exists at the given path."""
    return Path(path).is_file()


def assert_file_not_empty(path: str) -> bool:
    """Assert that a physical file exists and is not empty."""
    p = Path(path)
    if not p.is_file():
        return False
    return p.stat().st_size > 0


def assert_schema_valid(json_path: str, pydantic_model: type[BaseModel]) -> bool:
    """
    Assert that the JSON file at json_path exists and parses correctly
    into the given pydantic_model.
    """
    p = Path(json_path)
    if not p.is_file():
        return False

    try:
        data: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
        pydantic_model.model_validate(data)
        return True
    except (json.JSONDecodeError, ValidationError):
        return False


def run_shell_command(command: str, cwd: str = ".") -> tuple[bool, str, str]:
    """
    Execute a shell command locally.
    Returns a tuple of (success_boolean, stdout, stderr).
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except OSError as e:
        return (False, "", str(e))
