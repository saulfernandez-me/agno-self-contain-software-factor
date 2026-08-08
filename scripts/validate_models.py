import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini

# Model candidate lists to test
GEMINI_CANDIDATES = [
    # Workhorse / Lightweight candidates
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    
    # Heavy / Reasoning candidates
    "gemini-2.5-pro",
    "gemini-3.1-pro-preview",
]

# Pydantic model for Structured Output test
class ValidationResult(BaseModel):
    is_valid: bool = Field(description="Whether the data provided is valid")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(description="Explanation of the validation")

# Dummy tool for Tool Calling test
def get_system_status(service_name: str) -> str:
    """Returns the current status of a given system service."""
    if service_name.lower() == "database":
        return "online"
    return "unknown"

def test_structured_outputs(model_id: str) -> bool:
    try:
        agent = Agent(
            model=Gemini(id=model_id),
            output_schema=ValidationResult,
            structured_outputs=True
        )
        response = agent.run("Please validate this text: 'The sky is blue'. Provide a high confidence score.")
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

def test_tool_calling(model_id: str) -> bool:
    try:
        agent = Agent(
            model=Gemini(id=model_id),
            tools=[get_system_status]
        )
        # Ask something that explicitly requires the tool
        response = agent.run("What is the status of the database service? You MUST use the get_system_status tool to find out.")
        
        if response.content and "online" in str(response.content).lower():
            return True
        else:
            print(f"  [!] {model_id} failed to use the tool correctly. Output: {response.content}")
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
    md += "| Model ID | Structured Outputs | Tool Calling | Overall Status |\n"
    md += "|----------|--------------------|--------------|----------------|\n"
    
    for model, tests in results.items():
        so_mark = "✅" if tests.get("structured_outputs") else "❌"
        tc_mark = "✅" if tests.get("tool_calling") else "❌"
        
        overall = "🟢 VALIDATED" if (tests.get("structured_outputs") and tests.get("tool_calling")) else "🔴 FAILED"
        
        md += f"| `{model}` | {so_mark} | {tc_mark} | {overall} |\n"
        
    return md

def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY environment variable not set. Tests may fail.")
        
    results = {}
    
    print("Starting Model Validation Suite...\n")
    
    for model in GEMINI_CANDIDATES:
        print(f"Testing model: {model}")
        
        print("  -> Testing Structured Outputs...")
        so_result = test_structured_outputs(model)
        
        print("  -> Testing Tool Calling...")
        tc_result = test_tool_calling(model)
        
        results[model] = {
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
