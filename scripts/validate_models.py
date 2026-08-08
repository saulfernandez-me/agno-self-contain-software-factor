import os
import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from agno.agent import Agent

# Update the import to use APF's own resolve_model
# Ensure src is in PYTHONPATH if not running via module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from apf_core.models import resolve_model

# Model candidate lists to test per provider
CANDIDATES = {
    "google": [
        "gemini-2.5-flash",
        "gemini-3.5-flash",
        "gemini-2.5-pro",
        "gemini-3.1-pro-preview",
    ],
    "deepseek": [
        "deepseek-chat",     # DeepSeek-V3
        "deepseek-reasoner", # DeepSeek-R1
    ],
    "anthropic": [
        "claude-haiku-4-5-20251001",
        "claude-fable-5",
        "claude-sonnet-5",
        "claude-opus-5",
    ],
    "github": [
        "gpt-4o",
        "gpt-4o-mini",
        "o1-mini",
        "o3-mini"
    ]
}

def get_model_instance(provider: str, model_id: str):
    # Use APF's native resolver to faithfully replicate production execution
    return resolve_model(f"{provider}:{model_id}")

# Pydantic model for Structured Output test
class ValidationResult(BaseModel):
    is_valid: bool = Field(description="Whether the data provided is valid")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Explanation of the validation")

# Dummy tool for Tool Calling test
TEST_STATUS = f"status_{uuid.uuid4().hex[:8]}"

def get_system_status(service_name: str) -> str:
    """Returns the current status of a given system service."""
    if service_name.lower() == "database":
        return TEST_STATUS
    return "unknown"

def test_structured_outputs(provider: str, model_id: str) -> bool:
    try:
        agent = Agent(
            model=get_model_instance(provider, model_id),
            output_schema=ValidationResult,
            structured_outputs=True
        )
        response = agent.run("Please validate this text: 'The sky is blue'. Provide a high confidence score.")
        
        # DEBUG output
        print(f"    [DEBUG SO] {type(response.content)} - {response.content}")
        
        # Check if the output is successfully parsed into the Pydantic model
        if isinstance(response.content, ValidationResult):
            return True
        else:
            print(f"  [!] {model_id} failed Structured Outputs. Output: {response.content}")
            return False
        return False
    except Exception as e:
        print(f"  [!] Structured Output failed for {model_id}: {e}")
        return False

def test_tool_calling(provider: str, model_id: str) -> bool:
    try:
        agent = Agent(
            model=get_model_instance(provider, model_id),
            tools=[get_system_status]
        )
        # Ask something that explicitly requires the tool and is completely unambiguous
        response = agent.run("Tell me ONLY the status of the 'database' service using the available tool. Do not ask for clarifications.")
        
        # DEBUG output
        print(f"    [DEBUG TC] Content: {type(response.content)} - {response.content}")
        if hasattr(response, "tools") and response.tools:
            print(f"    [DEBUG TC] Tools executed: {[t.tool_name for t in response.tools]}")
        else:
            print("    [DEBUG TC] No tools were executed.")
        
        tool_called = hasattr(response, "tools") and response.tools and any(t.tool_name == "get_system_status" for t in response.tools)
        
        if tool_called and response.content and TEST_STATUS in str(response.content):
            return True
        else:
            print(f"  [!] {model_id} failed tool calling check. tool_called={tool_called}, content={response.content}")
            return False
        
        # Alternatively, check for tool calls in the run metrics or history if available,
        # but content having 'online' implies the tool was invoked and processed.
        return False
    except Exception as e:
        print(f"  [!] Tool Calling failed for {model_id}: {e}")
        return False

def generate_report(results: Dict[str, Dict[str, bool]]) -> str:
    md = "# Model Compatibility Matrix\n\n"
    md += "This document tracks the validation status of various LLMs against required Agno features.\n\n"
    md += "## Validation Methodology\n"
    md += "Models are validated via an automated probing script (`scripts/validate_models.py`) that executes real requests against the provider's API. "
    md += "The validation uses valid API Keys (injected securely via CI/CD environments) and connects to the official provider endpoints (Google Gemini, DeepSeek, Anthropic, and GitHub Models) through the Agno framework.\n\n"
    md += "The prober evaluates two critical capabilities:\n"
    md += "- **Structured Outputs:** The model is forced to return a response conforming strictly to a predefined Pydantic schema. If the model hallucinations or fails to use the API's native JSON mode, the test fails.\n"
    md += "- **Tool Calling:** The model is provided with a dummy tool and prompted with strict, unambiguous instructions to invoke it. This verifies its determinism for non-interactive execution (avoiding models that pause workflows to ask conversational questions).\n\n"
    md += "## Supported Models\n"
    md += "| Provider | Model ID | Structured Outputs | Tool Calling | Overall Status |\n"
    md += "|----------|----------|--------------------|--------------|----------------|\n"
    
    for provider, models in results.items():
        for model, tests in models.items():
            so_mark = "✅" if tests.get("structured_outputs") else "❌"
            tc_mark = "✅" if tests.get("tool_calling") else "❌"
            
            overall = "🟢 VALIDATED" if (tests.get("structured_outputs") and tests.get("tool_calling")) else "🔴 FAILED"
            
            md += f"| `{provider}` | `{model}` | {so_mark} | {tc_mark} | {overall} |\n"
        
    return md

def main():
    if not os.environ.get("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY environment variable not set. Gemini tests may fail.")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("WARNING: DEEPSEEK_API_KEY environment variable not set. DeepSeek tests may fail.")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set. Anthropic tests may fail.")
    if not os.environ.get("GITHUB_TOKEN"):
        print("WARNING: GITHUB_TOKEN environment variable not set. GitHub Models tests may fail.")
        
    results = {}
    
    print("Starting Model Validation Suite...\n")
    
    for provider, models in CANDIDATES.items():
        results[provider] = {}
        for model in models:
            print(f"Testing provider '{provider}', model '{model}':")
            
            print("  -> Testing Structured Outputs...")
            so_result = test_structured_outputs(provider, model)
            
            print("  -> Testing Tool Calling...")
            tc_result = test_tool_calling(provider, model)
            
            results[provider][model] = {
                "structured_outputs": so_result,
                "tool_calling": tc_result
            }
            print(f"  Result: SO={so_result}, TC={tc_result}\n")
        
    # Generate and save report
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    report_path = docs_dir / "model_compatibility_matrix.md"
    
    report_content = generate_report(results)
    report_path.write_text(report_content)
    
    print(f"Validation complete. Report generated at: {report_path}")

if __name__ == "__main__":
    main()
