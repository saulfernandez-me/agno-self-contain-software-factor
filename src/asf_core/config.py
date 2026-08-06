from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ModelTierConfig(BaseModel):
    primary: str
    fallbacks: list[str] = Field(default_factory=list)


class DomainConfig(BaseModel):
    name: str = "unknown_domain"
    description: str = "Generic domain context."


class LimitsConfig(BaseModel):
    correction_loop_max_attempts: int = 3
    inner_tool_call_limit: int = 5


class AsfConfig(BaseModel):
    domain: DomainConfig = Field(default_factory=DomainConfig)
    model_tiers: dict[str, ModelTierConfig] = Field(default_factory=dict)
    limits: LimitsConfig = Field(default_factory=LimitsConfig)


def load_asf_config(config_path: str = "asf.yaml") -> AsfConfig:
    """
    Loads and parses the ASF configuration YAML file.
    Returns a strongly typed Pydantic AsfConfig object.
    Falls back to safe defaults if the file is missing or invalid.
    """
    p = Path(config_path)
    if not p.is_file():
        # Return defaults if not found (e.g., during testing or uninitialized repos)
        return AsfConfig()

    try:
        with p.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                return AsfConfig()
            return AsfConfig.model_validate(data)
    except (OSError, yaml.YAMLError, ValueError):
        # If YAML is corrupted or validation fails, return defaults to prevent crashing
        return AsfConfig()


def get_models_for_tier(tier_name: str, config: AsfConfig | None = None) -> list[str]:
    """
    Retrieves the primary model and any fallbacks for a given tier.
    The primary model is always the first item in the returned list.

    If the tier is not found, returns a safe default based on the tier name.
    """
    if config is None:
        config = load_asf_config()

    tier = config.model_tiers.get(tier_name)
    if tier:
        return [tier.primary] + tier.fallbacks

    # Hardcoded safety nets if the YAML is missing tier definitions
    if tier_name == "heavy":
        return ["openai:gpt-4o", "anthropic:claude-3-5-sonnet"]
    elif tier_name == "workhorse":
        return ["openai:gpt-5.6-terra", "google:gemini-1.5-pro"]
    else:  # lightweight or unknown
        return ["google:gemini-1.5-flash"]
