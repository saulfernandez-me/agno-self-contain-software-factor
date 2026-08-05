from pathlib import Path

from assf_core.tools.workspace_tools import WorkspaceTools


def test_workspace_tools_tree(tmp_path: Path) -> None:
    # Setup mock dir
    d1 = tmp_path / "dir1"
    d1.mkdir()
    (d1 / "file1.txt").write_text("hello")
    (tmp_path / "root.txt").write_text("root")

    tools = WorkspaceTools(restrict_to_cwd=False)
    tree = tools.list_directory_tree(str(tmp_path))

    assert "📂" in tree
    assert "file1.txt" in tree
    assert "root.txt" in tree


def test_workspace_tools_snippet(tmp_path: Path) -> None:
    f = tmp_path / "code.py"
    f.write_text("line1\nline2\nline3\nline4\n")

    tools = WorkspaceTools(restrict_to_cwd=False)

    snippet = tools.read_file_snippet(str(f), 2, 3)
    assert "line2" in snippet
    assert "line3" in snippet
    assert "line1" not in snippet
    assert "line4" not in snippet


def test_workspace_tools_safety() -> None:
    tools = WorkspaceTools(restrict_to_cwd=True)
    # Trying to access root or parent should fail if restricted
    res = tools.read_file_snippet("/etc/passwd", 1, 10)
    assert "outside the restricted" in res
