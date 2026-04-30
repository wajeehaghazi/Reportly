from langgraph.graph import StateGraph, START, END
from nodes.orchestrator import orchestrator
from nodes.worker import llm_call
from nodes.synthesizer import synthesizer
from state.state import State
from langgraph.types import Send

def assign_workers(state: State):
    """
    Create one worker per section
    """
    return [
        Send("llm_call", {"section": s})
        for s in state["sections"]
    ]

from langgraph.graph import StateGraph

orchestrator_worker_builder=StateGraph(State)

orchestrator_worker_builder.add_node("orchestrator", orchestrator)
orchestrator_worker_builder.add_node("llm_call", llm_call)
orchestrator_worker_builder.add_node("synthesizer",synthesizer)

orchestrator_worker_builder.add_edge(START, "orchestrator")
orchestrator_worker_builder.add_conditional_edges(
    "orchestrator", assign_workers, {"llm_call": "llm_call"}
)
orchestrator_worker_builder.add_edge("llm_call", "synthesizer")
orchestrator_worker_builder.add_edge("synthesizer", END)

orchestrator_worker = orchestrator_worker_builder.compile()

if __name__ == "__main__":

    print("\nRunning Orchestrator Workflow...\n")

    result = orchestrator_worker.invoke(
        {
            "topic": "Create a report on LLM scaling laws"
        }
    )

    print("\nFINAL REPORT:\n")
    print(result["final_report"])