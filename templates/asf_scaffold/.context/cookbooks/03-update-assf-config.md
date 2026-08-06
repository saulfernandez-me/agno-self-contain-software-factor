# Cookbook 03: Updating the ASF Configuration (asf.yaml)

> **Purpose:** Instructs autonomous agents and engineers on how to safely mutate the `asf.yaml` hardware configuration file without breaking the 3-Tier model architecture.

## 1. The 3-Tier Model Architecture
ASF does not map models to specific agents (e.g., "Planner gets GPT-4"). Instead, it maps models to **Complexity Tiers**.

- **Heavy Tier:** Used for cognitively intense, zero-error-tolerance tasks (e.g., `Planner`, `Builder`, `Reviewer`).
- **Workhorse Tier:** Used for continuous, medium-complexity data processing (e.g., `Structurer`).
- **Lightweight Tier:** Used for high-volume, low-complexity reading tasks (e.g., `Scout`, `Documenter`).

## 2. Modifying the YAML safely
When instructed to "change the model" or "add a fallback", you must manipulate the `asf.yaml` file located in `.context/`.

### Rules for Mutation:
1. **Never change the tier names** (`heavy`, `workhorse`, `lightweight`).
2. **Primary is Mandatory**: Every tier MUST have exactly one `primary` model defined as a string.
3. **Fallbacks are Optional**: Every tier MAY have a `fallbacks` list.
4. **Naming Convention**: Always use the Agno provider format: `provider:model-name` (e.g., `google:gemini-2.5-pro`, `anthropic:claude-3-5-sonnet`).

### Example Valid Configuration:
```yaml
model_tiers:
  heavy:
    primary: "anthropic:claude-3-5-sonnet"
    fallbacks:
      - "openai:gpt-4o"
  workhorse:
    primary: "google:gemini-1.5-pro"
  lightweight:
    primary: "google:gemini-1.5-flash"
    fallbacks:
      - "deepseek:deepseek-chat"
```

If you add a new provider (e.g., `anthropic`), ensure you remind the engineer to update the `.env` file with the corresponding API key.
