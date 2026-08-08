# Model Compatibility Matrix

This document tracks the validation status of various LLMs against required Agno features.

## Validation Methodology
Models are validated via an automated probing script (`scripts/validate_models.py`) that executes real requests against the provider's API. The validation uses valid API Keys (injected securely via CI/CD environments) and connects to the official provider endpoints (Google Gemini and DeepSeek) through the Agno framework.

The prober evaluates two critical capabilities:
- **Structured Outputs:** The model is forced to return a response conforming strictly to a predefined Pydantic schema. If the model hallucinations or fails to use the API's native JSON mode, the test fails.
- **Tool Calling:** The model is provided with a dummy tool and prompted with strict, unambiguous instructions to invoke it. This verifies its determinism for non-interactive execution (avoiding models that pause workflows to ask conversational questions).

## Supported Models
| Provider | Model ID | Structured Outputs | Tool Calling | Overall Status |
|----------|----------|--------------------|--------------|----------------|
| `google` | `gemini-2.5-flash` | ✅ | ✅ | 🟢 VALIDATED |
| `google` | `gemini-3.5-flash` | ✅ | ✅ | 🟢 VALIDATED |
| `google` | `gemini-2.5-pro` | ✅ | ✅ | 🟢 VALIDATED |
| `google` | `gemini-3.1-pro-preview` | ✅ | ✅ | 🟢 VALIDATED |
| `deepseek` | `deepseek-chat` | ✅ | ✅ | 🟢 VALIDATED |
| `deepseek` | `deepseek-reasoner` | ✅ | ✅ | 🟢 VALIDATED |
