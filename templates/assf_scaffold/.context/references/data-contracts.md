# Reference: ASSF Data Contracts and Gates

> **Purpose:** Detailed technical specification of the `EnvelopeBase` and how Assertion Gates validate the Definition of Done (DoD) of an agentic phase.

## 1. The Pydantic Envelope (`EnvelopeBase`)

In ASSF, conversational chat history is considered noise. The only valid way for Phase A to transfer context to Phase B is by writing a JSON file to disk that strictly conforms to a Pydantic schema.

### The Base Schema Definition
Located in `assf_core.envelopes`. Every domain-specific envelope must inherit from this:

```python
class EnvelopeBase(BaseModel):
    status: Literal["success", "fail"]
    summary: str
    artifacts: List[str]
    notes_for_next_agent: str
    metadata: Dict[str, Any]
```

### Extending the Schema
If your agent needs to pass specific data (e.g., a list of external URLs researched, or a suggested git commit message), you extend the base class:

```python
class ResearchEnvelope(EnvelopeBase):
    sources_consulted: List[str]
    confidence_score: float
```

## 2. Assertion Gates

Gates belong to the **Code Lane** (`lane="code"`). They are pure Python functions that run immediately after an agent completes its phase. They verify factual state, preventing the LLM from hallucinating success.

### Built-in Static Assertions
Located in `assf_core.assert_gates`.
- `assert_file_exists(path: str) -> bool`
- `assert_file_not_empty(path: str) -> bool`
- `assert_schema_valid(json_path: str, model: Type[BaseModel]) -> bool`

### Shell Execution Assertions
The most powerful gate is the test runner. 
Use `run_shell_command("uv run pytest")` or `run_shell_command("ruff check .")`. 
If `success` is `False`, the `stderr` string MUST be captured and fed directly back into the Agent Lane as a correction prompt.
