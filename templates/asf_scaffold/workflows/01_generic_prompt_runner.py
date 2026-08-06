from src.agents.builder import get_builder_agent  # type: ignore[import-not-found]

from asf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from asf_core.workflow import AsfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AsfWorkflow(name="01_generic_prompt")
    agent = get_builder_agent(domain, task, EnvelopeBase)
    with wf.lane("agent"):
        wf.run_agent(agent, task)
