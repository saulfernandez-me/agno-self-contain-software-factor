# Global Definition of Done (DoD) & Engineering Standards

This document defines the quality rules and global acceptance criteria that every Issue, Pull Request, and line of code in **ASSF** must meet before being considered "Done".

## 1. Global Acceptance Criteria (DoD)

For an Issue to transition from `Implementing` to `Done` (or be merged into `main`), it must meet **all** of the following requirements:

- [ ] **Functionality:** The code strictly complies with the Technical Specification detailed in the Issue.
- [ ] **Tests Passing:** All unit and integration tests pass successfully (`pytest`).
- [ ] **Code Coverage:** The new code maintains or increases the test coverage (minimum required: 80%).
- [ ] **Strict Typing:** Passes static type analysis validation (`mypy --strict`). Unjustified `Any` types are strictly forbidden.
- [ ] **Linting and Formatting:** The code is formatted and free of warnings according to the project standards (`ruff check` and `ruff format`).
- [ ] **Documentation:** New classes and public functions contain docstrings (Google/PEP 257 style). If the architecture is altered, files in `docs/` or `README.md` must be updated.
- [ ] **Pydantic Contracts:** Any structural data exchange is typed and validated using `Pydantic` models.
- [ ] **Peer Review (HITL):** The Pull Request has been reviewed and approved by the Platform Architect (Saúl).

## 2. Repository Standards

### Environment and Dependency Management
- We will use **`uv`** as the sole package and virtual environment manager.
- Production dependencies are strictly separated from development dependencies (`--dev`).

### Python Code Structure
- **Source Directory:** `src/assf_core/` (Installable library).
- **Tests Directory:** `tests/` (Mirroring the `src/` structure).
- **Templates Directory:** `templates/` (Files to be "stamped" into target repositories).

### Git Workflow and Commits
- **Branches:** All development occurs in isolated branches using the format `feat/issue-<number>-<short_description>`, `fix/...`, or `chore/...`.
- **Commits:** Strict adherence to **Conventional Commits** is required (e.g., `feat: implement EnvelopeBase validation`, `fix: correct typo in Gate logic`).
- **Pull Requests:** All code reaches `main` exclusively through a Pull Request linked to its corresponding GitHub Issue.
