# Cookbook 04: Debugging Gates and the Correction Loop

> **Purpose:** A rigorous manual teaching `Builder` and `Reviewer` agents how to handle Validation Gate failures and Correction Loops without panicking or creating destructive loops.

## 1. The Mindset of a Correction Loop
When you (the Agent) emit a JSON Envelope, your task pauses. The Python Orchestrator (`AssfWorkflow`) takes over and runs deterministic code (Linters, Tests, Security Snapshots) in the `Code Lane`.

If that code fails, the Orchestrator will re-prompt you **in the same session** with the error output (`stderr`). 
**DO NOT APOLOGIZE. DO NOT EXPLAIN.** Your job is to read the error, fix the code, and emit a new, corrected Envelope.

## 2. Debugging Strategy (The 3-Step Protocol)

If you receive a prompt starting with "Tests failed. Please fix the code. Stderr:", you must follow this exact protocol:

### Step 1: Isolate the Failure
Do not rewrite the entire file. Look at the `stderr` provided. 
- Did a specific test fail? (e.g., `AssertionError: Expected 200, got 404`).
- Did the Linter catch a syntax error? (e.g., `F821 Undefined name`).
- Did the Security Gate block you? (e.g., `Unauthorized modification detected in tests/`).

### Step 2: Use Your Tools (If Needed)
If the error trace is insufficient, use your `WorkspaceTools` or `FileTools` to read the specific failing test file (`read_file_snippet`) to understand the context. Do not guess.

### Step 3: Emit the Fix
Write the corrected code using your `FileTools`. Once the code is physically saved to disk, emit your Pydantic JSON Envelope again.

## 3. The `max_attempts` Bailout
You have a limited number of tries (usually 3). If you cannot fix the bug on the final attempt, **emit an Envelope that cleanly summarizes why the fix is impossible**. 
The Python orchestrator will catch the loop exhaustion and escalate the issue to the `Engineer Lane` (Human). Do not try to hack around the framework.
