# 🛠️ Tool Management & The Principle of Least Privilege

In **Agno Product Factory (APF)**, the cognitive ability of an agent (its prompt and context) is completely separated from its physical capabilities. 

An agent's physical capabilities are defined by its **Tools**. This document demystifies how tools work under the hood via the Agno SDK, why they are strictly hardcoded into the Archetypes, and how you can extend them.

---

## 1. How Tools Work Under the Hood (The Agno Bridge)

When you assign a tool to an agent in APF, you are passing a Python class (a `Toolkit`). 

**The Mechanics:**
1. **Introspection:** Agno reads the Python functions inside the Toolkit (e.g., `def write_file(path, content):`).
2. **Translation:** Agno parses your Python type hints (`str`, `int`) and your Docstrings. It translates them into a strict **JSON Schema**.
3. **LLM Injection:** This JSON Schema is sent to the LLM (Gemini, Claude, DeepSeek) via the provider's "Function Calling" API.
4. **Execution:** The LLM decides it needs to use a tool and replies with a JSON payload: `{"name": "write_file", "arguments": {"path": "src/main.py", "content": "..."}}`.
5. **The Bridge:** Agno intercepts this response, executes your local Python function with those arguments, and feeds the output (`"Successfully wrote file"`) back to the LLM.

Because of this bridge, **the LLM never has raw shell access**. It can only call the specific Python functions you expose to it.

---

## 2. The Principle of Least Privilege (APF Archetypes)

In APF, tools are **hardcoded** in the factory functions located in `src/agents/*.py`. 
We do not pass tools dynamically based on the project. Why? To enforce the **Principle of Least Privilege**.

If an LLM hallucinates, the damage it can do is mathematically bounded by its tools:

- **Planner (`planner.py`)**: `tools=[]`
  - *Why?* The Planner is an architect. It should only think and output a JSON plan. By giving it zero tools, it is physically impossible for the Planner to accidentally overwrite a file or delete a database.
- **Scout (`scout.py`)**: `tools=[WorkspaceTools(restrict_to_cwd=True), DuckDuckGoTools()]`
  - *Why?* The Scout needs to map the codebase and read the web. We use our custom `WorkspaceTools` which has `read_file_snippet` and `search_keyword`, but lacks `write_file`. The Scout cannot mutate the repo.
- **Builder (`builder.py`)**: `tools=[WorkspaceTools(restrict_to_cwd=True)]`
  - *Why?* The Builder is the only agent authorized to mutate the codebase. Its `WorkspaceTools` includes the `write_file` method.

By hardcoding tools to the Archetype, APF ensures that a runaway model cannot break your system.

---

## 3. How to Extend the Factory (Creating Custom Tools)

As a Platform Engineer, you will eventually need your agents to interact with proprietary systems (e.g., an internal AWS deployment pipeline, a Jira instance, or a production Database).

Here is how you add a new tool to APF:

### Step 1: Create the Toolkit
Create a new file in `src/apf_core/tools/` (e.g., `database_tools.py`):

```python
from agno.tools import Toolkit
import sqlite3


class DatabaseTools(Toolkit):
    def __init__(self, db_path: str):
        super().__init__(name="database_tools")
        self.db_path = db_path
        # Register the function so Agno translates it to JSON Schema
        self.register(self.execute_read_query)

    def execute_read_query(self, query: str) -> str:
        """
        Executes a READ-ONLY SQL query against the database.

        Args:
            query: The SELECT SQL query to execute.

        Returns:
            The stringified rows returned by the database, or an error message.
        """
        if (
            "DROP" in query.upper()
            or "UPDATE" in query.upper()
            or "INSERT" in query.upper()
        ):
            return "Error: Only SELECT queries are allowed."

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return str(rows)
        except Exception as e:
            return f"Database error: {str(e)}"
```

### Step 2: Assign it to an Archetype
Open the agent factory (e.g., `src/agents/scout.py`) and add it to the `tools` array:

```python
from apf_core.tools.database_tools import DatabaseTools


def get_scout_agent(
    domain_context: str,
    task_instructions: str,
    response_model: Type[BaseModel],
    model_tier: str = "lightweight",
) -> Agent:
    # ...
    return Agent(
        name="Scout",
        # ...
        tools=[
            WorkspaceTools(restrict_to_cwd=True),
            DuckDuckGoTools(),
            DatabaseTools(db_path="production.db"),  # <-- Your new tool
        ],
        # ...
    )
```

Now, whenever the Scout operates, the LLM will automatically know it has the power to query that database safely!
