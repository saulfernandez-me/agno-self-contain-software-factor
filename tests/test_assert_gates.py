import json
from pathlib import Path

from pydantic import BaseModel

from asf_core.assert_gates import (
    assert_file_exists,
    assert_file_not_empty,
    assert_schema_valid,
    run_shell_command,
)


class DummyEnvelope(BaseModel):
    status: str
    message: str


def test_assert_file_exists(tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.touch()

    assert assert_file_exists(str(test_file)) is True
    assert assert_file_exists(str(tmp_path / "does_not_exist.txt")) is False


def test_assert_file_not_empty(tmp_path: Path) -> None:
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    empty_file = tmp_path / "empty.txt"
    empty_file.touch()

    assert assert_file_not_empty(str(test_file)) is True
    assert assert_file_not_empty(str(empty_file)) is False
    assert assert_file_not_empty(str(tmp_path / "missing.txt")) is False


def test_assert_schema_valid(tmp_path: Path) -> None:
    valid_json = tmp_path / "valid.json"
    valid_json.write_text(json.dumps({"status": "success", "message": "ok"}))

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text(json.dumps({"status": "success"}))  # Missing 'message'

    broken_json = tmp_path / "broken.json"
    broken_json.write_text("{ broken json")

    assert assert_schema_valid(str(valid_json), DummyEnvelope) is True
    assert assert_schema_valid(str(invalid_json), DummyEnvelope) is False
    assert assert_schema_valid(str(broken_json), DummyEnvelope) is False
    assert assert_schema_valid(str(tmp_path / "missing.json"), DummyEnvelope) is False


def test_run_shell_command() -> None:
    success, stdout, stderr = run_shell_command("echo 'hello world'")
    assert success is True
    assert "hello world" in stdout

    success, stdout, stderr = run_shell_command("ls /path/that/does/not/exist")
    assert success is False
    assert "No such file or directory" in stderr or "cannot access" in stderr
