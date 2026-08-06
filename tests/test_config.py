from pathlib import Path

from asf_core.config import AsfConfig, get_models_for_tier, load_asf_config


def test_load_asf_config_defaults(tmp_path: Path) -> None:
    """Test that missing config returns safe defaults."""
    missing_path = tmp_path / "does_not_exist.yaml"
    config = load_asf_config(str(missing_path))
    assert isinstance(config, AsfConfig)
    assert config.domain.name == "unknown_domain"
    assert config.limits.correction_loop_max_attempts == 3


def test_load_asf_config_valid(tmp_path: Path) -> None:
    """Test loading a valid YAML config."""
    yaml_content = """
domain:
  name: "test_domain"
  description: "Test description"
model_tiers:
  heavy:
    primary: "test:heavy-primary"
    fallbacks: ["test:heavy-fallback"]
limits:
  correction_loop_max_attempts: 5
    """
    config_file = tmp_path / "asf.yaml"
    config_file.write_text(yaml_content)

    config = load_asf_config(str(config_file))

    assert config.domain.name == "test_domain"
    assert config.limits.correction_loop_max_attempts == 5
    assert "heavy" in config.model_tiers
    assert config.model_tiers["heavy"].primary == "test:heavy-primary"
    assert config.model_tiers["heavy"].fallbacks == ["test:heavy-fallback"]


def test_get_models_for_tier(tmp_path: Path) -> None:
    """Test the retrieval of models for Agno consumption."""
    yaml_content = """
model_tiers:
  workhorse:
    primary: "test:workhorse"
    fallbacks: ["test:workhorse-fb1", "test:workhorse-fb2"]
    """
    config_file = tmp_path / "asf.yaml"
    config_file.write_text(yaml_content)

    config = load_asf_config(str(config_file))

    # Existing tier
    models = get_models_for_tier("workhorse", config)
    assert len(models) == 3
    assert models[0] == "test:workhorse"
    assert models[1] == "test:workhorse-fb1"

    # Missing tier should return safety net defaults
    heavy_models = get_models_for_tier("heavy", config)
    assert len(heavy_models) > 0
    assert "openai:gpt-4o" in heavy_models
