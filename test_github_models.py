import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# You need a GITHUB_TOKEN for this. Let's see if we can instantiate it.
gh_token = os.getenv("GITHUB_TOKEN", "dummy")

model = OpenAIChat(
    id="gpt-4o",
    api_key=gh_token,
    base_url="https://models.inference.ai.azure.com"
)
print("Model initialized successfully!")
