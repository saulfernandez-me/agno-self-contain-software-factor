# Reference: Pydantic Envelopes and Validation Errors

> **Purpose:** Deep dive into how Pydantic validates Envelopes. This manual teaches agents how to interpret `ValidationError` exceptions and auto-correct their JSON schemas.

## 1. The Pydantic Engine in APF
APF uses Pydantic V2 to enforce data contracts between nodes. When you (the Agent) are instantiated, your Agno wrapper is configured with a `response_model` (e.g., `BuildEnvelope`).

Under the hood, Agno leverages the LLM provider's "Structured Outputs" API to force your response into JSON. However, if you attempt to bypass this or emit invalid types, Pydantic will raise a `ValidationError`.

## 2. Common Validation Errors & How to Fix Them

If your output is rejected, the Python orchestrator will catch the `ValidationError` and feed the stack trace back to you. Here is how you read it:

### A. Missing Required Fields
**Error Trace Example:**
```text
1 validation error for BuildEnvelope
summary
  Field required [type=missing, input_value={'status': 'success'}, input_type=dict]
```
**How to Fix:** You forgot to include a mandatory key in your JSON. Look at the missing field (`summary`) and ensure your next JSON payload includes it. All Envelopes require at least `status`, `summary`, `artifacts`, and `notes_for_next_agent`.

### B. Invalid Literal Values
**Error Trace Example:**
```text
1 validation error for EnvelopeBase
status
  Input should be 'success' or 'fail' [type=literal_error, input_value='done', input_type=str]
```
**How to Fix:** You used a value that is not allowed. The `status` field is a `Literal["success", "fail"]`. You cannot use "done", "ok", or "error". Fix your spelling.

### C. Type Mismatches
**Error Trace Example:**
```text
1 validation error for EnvelopeBase
artifacts
  Input should be a valid list [type=list_type, input_value='src/main.py', input_type=str]
```
**How to Fix:** You provided a String where a List (Array) was expected. Wrap the value in brackets: `["src/main.py"]`.

## 3. The `metadata` Field
The `metadata` field is a `Dict[str, Any]`. It is an escape hatch. If you absolutely must pass custom data to the next agent that doesn't fit the strict schema, put it inside the `metadata` dictionary. However, rely on the strongly-typed fields whenever possible.
