from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.types import Send

from src.nodes.orchestrator import orchestrator
from src.nodes.worker import llm_call
from src.nodes.synthesizer import synthesizer

from src.schema.state import State


# -----------------------------------------
# Assign Workers
# -----------------------------------------

def assign_workers(state: State):

    return [
        Send(
            "llm_call",
            {
                "section": s
            }
        )
        for s in state["sections"]
    ]


# -----------------------------------------
# Build Graph
# -----------------------------------------

orchestrator_worker_builder = StateGraph(
    State
)

orchestrator_worker_builder.add_node(
    "orchestrator",
    orchestrator
)

orchestrator_worker_builder.add_node(
    "llm_call",
    llm_call
)

orchestrator_worker_builder.add_node(
    "synthesizer",
    synthesizer
)

orchestrator_worker_builder.add_edge(
    START,
    "orchestrator"
)

orchestrator_worker_builder.add_conditional_edges(
    "orchestrator",
    assign_workers,
    {
        "llm_call": "llm_call"
    }
)

orchestrator_worker_builder.add_edge(
    "llm_call",
    "synthesizer"
)

orchestrator_worker_builder.add_edge(
    "synthesizer",
    END
)

orchestrator_worker = (
    orchestrator_worker_builder.compile()
)