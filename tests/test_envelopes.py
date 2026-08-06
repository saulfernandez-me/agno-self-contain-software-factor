import pytest
from pydantic import ValidationError

from asf_core.envelopes import BuildEnvelope, EnvelopeBase, ResearchEnvelope


def test_envelope_base_success() -> None:
    """Test that EnvelopeBase successfully validates correct data."""
    envelope = EnvelopeBase(
        status="success",
        summary="Completed initial planning.",
        artifacts=["plan.md"],
        notes_for_next_agent="Proceed with building the auth module.",
        metadata={"tokens": 1500, "duration_ms": 1200},
    )
    assert envelope.status == "success"
    assert envelope.summary == "Completed initial planning."
    assert "plan.md" in envelope.artifacts
    assert envelope.metadata["tokens"] == 1500


def test_envelope_base_fail_invalid_status() -> None:
    """Test that EnvelopeBase rejects invalid status literals."""
    with pytest.raises(ValidationError) as exc_info:
        EnvelopeBase(
            status="pending",  # type: ignore[arg-type] # Invalid, must be success or fail
            summary="In progress.",
            artifacts=[],
            notes_for_next_agent="Wait.",
            metadata={},
        )
    assert "status" in str(exc_info.value)


def test_envelope_base_missing_required_fields() -> None:
    """Test that EnvelopeBase requires mandatory fields."""
    with pytest.raises(ValidationError) as exc_info:
        EnvelopeBase(
            status="success"
            # Missing summary and notes_for_next_agent
        )  # type: ignore[call-arg]
    assert "summary" in str(exc_info.value)
    assert "notes_for_next_agent" in str(exc_info.value)


def test_build_envelope_serialization() -> None:
    """Test serialization of a domain-specific BuildEnvelope."""
    envelope = BuildEnvelope(
        status="success",
        summary="Built auth module.",
        artifacts=["src/api/auth.py"],
        notes_for_next_agent="Run tests.",
        commit_message="feat: add auth module",
    )
    json_data = envelope.model_dump_json()
    assert "feat: add auth module" in json_data

    # Deserialization test
    parsed = BuildEnvelope.model_validate_json(json_data)
    assert parsed.commit_message == "feat: add auth module"


def test_research_envelope() -> None:
    """Test ResearchEnvelope default factories."""
    envelope = ResearchEnvelope(
        status="fail",
        summary="Could not find docs.",
        notes_for_next_agent="Ask human for links.",
    )
    # Check default factories kicked in
    assert envelope.artifacts == []
    assert envelope.metadata == {}
    assert envelope.sources_consulted == []
