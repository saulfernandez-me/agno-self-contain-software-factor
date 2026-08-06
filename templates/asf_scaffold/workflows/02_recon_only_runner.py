from src.agents.scout import get_scout_agent  # type: ignore[import-not-found]

from asf_core.envelopes import EnvelopeBase  # type: ignore[import-not-found]
from asf_core.workflow import AsfWorkflow  # type: ignore[import-not-found]


def run(task: str, domain: str):
    wf = AsfWorkflow(name="02_recon_only")
    scout = get_scout_agent(domain, task, EnvelopeBase)
    with wf.lane("agent"):
        wf.run_agent(scout, task)
