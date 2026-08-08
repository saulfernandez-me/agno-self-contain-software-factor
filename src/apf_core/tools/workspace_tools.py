import subprocess
from pathlib import Path

from agno.tools import Toolkit


class WorkspaceTools(Toolkit):
    """
    Agno Toolkit for advanced workspace mapping and context extraction.
    Designed for the Scout agent to navigate massive codebases without blowing up
    the LLM context window.
    """

    def __init__(self, restrict_to_cwd: bool = True) -> None:
        super().__init__(name="workspace_tools")
        self.restrict_to_cwd = restrict_to_cwd
        self.cwd = Path.cwd().resolve()

        self.register(self.list_directory_tree)
        self.register(self.read_file_snippet)
        self.register(self.search_keyword)
        self.register(self.write_file)
        self.register(self.save_artifact)

    def _is_safe_path(self, target_path: str) -> bool:
        if not self.restrict_to_cwd:
            return True
        try:
            resolved = Path(target_path).resolve()
            return self.cwd in resolved.parents or resolved == self.cwd
        except OSError:
            return False

    def list_directory_tree(self, path: str = ".", max_depth: int = 2) -> str:
        """
        Lists files in a directory up to a maximum depth.
        Useful to understand repository structure without reading file contents.

        Args:
            path: Directory to list.
            max_depth: Maximum recursion depth.

        Returns:
            String representation of the directory tree.
        """
        if not self._is_safe_path(path):
            return "Error: Path is outside the restricted working directory."

        target = Path(path)
        if not target.exists() or not target.is_dir():
            return f"Error: Directory {path} does not exist."

        tree_lines: list[str] = []

        def _walk(current_dir: Path, current_depth: int) -> None:
            if current_depth > max_depth:
                return
            try:
                for item in sorted(current_dir.iterdir()):
                    if item.name.startswith("."):
                        continue  # Skip hidden files/dirs like .git or .venv

                    indent = "  " * current_depth
                    if item.is_dir():
                        tree_lines.append(f"{indent}📂 {item.name}/")
                        _walk(item, current_depth + 1)
                    else:
                        tree_lines.append(f"{indent}📄 {item.name}")
            except PermissionError:
                tree_lines.append(f"{'  ' * current_depth}🔒 [Permission Denied]")

        tree_lines.append(f"📂 {target.name or '.'}/")
        _walk(target, 1)
        return "\n".join(tree_lines)

    def read_file_snippet(
        self, path: str, start_line: int = 1, end_line: int = 1000
    ) -> str:
        """
        Reads a specific range of lines from a file.
        Use this instead of reading the entire file to save context window tokens.

        Args:
            path: The file path.
            start_line: Line number to start reading from (1-indexed). Defaults to 1.
            end_line: Line number to end reading at (inclusive). Defaults to 1000.

        Returns:
            The requested lines of code.
        """
        if not self._is_safe_path(path):
            return "Error: Path is outside the restricted working directory."

        target = Path(path)
        if not target.is_file():
            return f"Error: File {path} not found."

        if start_line < 1 or end_line < start_line:
            return "Error: Invalid line range."

        try:
            with target.open("r", encoding="utf-8") as f:
                lines = f.readlines()

            # 1-indexed to 0-indexed
            snippet = lines[start_line - 1 : end_line]
            return "".join(snippet)
        except OSError as e:
            return f"Error reading file snippet: {e!s}"

    def write_file(self, path: str, content: str) -> str:
        """
        Writes content to a specific file. Creates parent directories if they don't exist.

        Args:
            path: The file path to write to.
            content: The text content to write into the file.

        Returns:
            Success or error message.
        """
        if not self._is_safe_path(path):
            return "Error: Path is outside the restricted working directory."

        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Successfully wrote to {path}"
        except OSError as e:
            return f"Error writing file: {e!s}"

    def save_artifact(self, path: str, content: str) -> str:
        """
        Saves a generated artifact (like an RFC or markdown document) to the workspace.
        This must be used instead of returning massive strings in the final response.

        Args:
            path: The file path to save to (e.g. 'docs/rfcs/006-feature.md').
            content: The entire text content of the artifact.

        Returns:
            Success or error message.
        """
        if not self._is_safe_path(path):
            return "Error: Path is outside the restricted working directory."

        target = Path(path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Successfully saved artifact to {path}"
        except OSError as e:
            return f"Error saving artifact: {e!s}"

    def search_keyword(self, keyword: str, path: str = ".") -> str:
        """
        Searches the workspace for a specific keyword or function name.
        Uses 'grep' under the hood.

        Args:
            keyword: The exact string to search for.
            path: Directory to search inside.

        Returns:
            Search results with file paths and line numbers.
        """
        if not self._is_safe_path(path):
            return "Error: Path is outside the restricted working directory."

        try:
            # -r recursive, -n line numbers, -I ignore binary files
            res = subprocess.run(
                ["grep", "-rnI", keyword, path],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0:
                # Truncate if too long to protect context window
                out = res.stdout
                if len(out) > 4000:
                    out = out[:4000] + "\n...[TRUNCATED due to length]..."
                return out
            elif res.returncode == 1:
                return f"No results found for '{keyword}'."
            else:
                return f"Error searching: {res.stderr}"
        except OSError as e:
            return f"Failed to execute search: {e!s}"
