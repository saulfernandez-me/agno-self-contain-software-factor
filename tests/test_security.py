from assf_core.security import enforce_permissions, get_git_snapshot


def test_get_git_snapshot() -> None:
    """Test git status abstraction (requires a git environment or mocks)."""
    # Assuming this runs in a git repo, snapshot should return a set (empty or not)
    snapshot = get_git_snapshot()
    assert isinstance(snapshot, set)


def test_enforce_permissions_clean(tmp_path) -> None:
    """If no new files changed, permissions should pass."""
    pre_snapshot: set[str] = set()
    # Mocking get_git_snapshot to return an empty set
    import assf_core.security

    original = assf_core.security.get_git_snapshot
    assf_core.security.get_git_snapshot = lambda cwd=".": set()  # type: ignore[assignment]

    try:
        success, unauthorized = enforce_permissions(
            ["allowed.txt"], pre_snapshot, str(tmp_path)
        )
        assert success is True
        assert len(unauthorized) == 0
    finally:
        assf_core.security.get_git_snapshot = original


def test_enforce_permissions_unauthorized(tmp_path) -> None:
    """If a file changes that is not in the allowed list, it should fail and report it."""
    pre_snapshot: set[str] = set()
    import assf_core.security

    original = assf_core.security.get_git_snapshot
    assf_core.security.get_git_snapshot = lambda cwd=".": {"hacked_file.py", "allowed.txt"}  # type: ignore[assignment]

    try:
        # Mocking subprocess.run to prevent actual git checkout errors in test env
        import subprocess

        original_run = subprocess.run
        subprocess.run = lambda *args, **kwargs: None  # type: ignore[assignment]

        success, unauthorized = enforce_permissions(
            ["allowed.txt"], pre_snapshot, str(tmp_path)
        )
        assert success is False
        assert "hacked_file.py" in unauthorized
        assert "allowed.txt" not in unauthorized
    finally:
        assf_core.security.get_git_snapshot = original
        subprocess.run = original_run  # type: ignore[assignment]
