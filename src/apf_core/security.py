import os
import subprocess


def get_git_snapshot(cwd: str = ".") -> set[str]:
    """
    Returns a set of files that are currently modified, added, or deleted in the working tree.
    Uses 'git status --porcelain'.
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return set()

        changed_files = set()
        for line in result.stdout.splitlines():
            if len(line) > 3:
                # ' M file.txt' or '?? file.txt'
                filepath = line[3:].strip()
                changed_files.add(filepath)
        return changed_files
    except OSError:
        return set()


def enforce_permissions(
    allowed_artifacts: list[str], pre_snapshot: set[str], cwd: str = "."
) -> tuple[bool, list[str]]:
    """
    Checks if any file changed that is NOT in allowed_artifacts or pre_snapshot.
    If unauthorized changes exist, it reverts them (git checkout & git clean) and returns False.
    """
    post_snapshot = get_git_snapshot(cwd)

    # Files changed during the phase that weren't changed before
    new_changes = post_snapshot - pre_snapshot

    if not new_changes:
        return True, []

    # Normalize allowed paths
    allowed_normalized = {
        os.path.normpath(os.path.join(cwd, p)) for p in allowed_artifacts
    }

    unauthorized = []
    for changed_file in new_changes:
        changed_normalized = os.path.normpath(os.path.join(cwd, changed_file))
        if changed_normalized not in allowed_normalized:
            unauthorized.append(changed_file)

    if unauthorized:
        # Revert unauthorized changes
        for f in unauthorized:
            # Revert modifications
            subprocess.run(
                ["git", "checkout", "--", f], cwd=cwd, capture_output=True, check=False
            )
            # Remove untracked files
            subprocess.run(
                ["git", "clean", "-fd", f], cwd=cwd, capture_output=True, check=False
            )

        return False, unauthorized

    return True, []
