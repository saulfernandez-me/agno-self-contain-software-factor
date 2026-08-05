from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]

from assf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from assf_core.workflow import AssfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AssfWorkflow(name="01_generic_prompt")
    agent = get_builder_agent(domain, task, EnvelopeBase)
    with wf.lane("agent"):
        agent.run(task)
