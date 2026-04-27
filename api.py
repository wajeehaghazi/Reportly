from fastapi import FastAPI
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from nodes.orchestrator import orchestrator
from nodes.worker import llm_call
from nodes.synthesizer import synthesizer
from state.state import State


# -------------------------
# Build workflow once
# -------------------------

def assign_workers(state: State):
    return [
        Send("llm_call", {"section": s})
        for s in state["sections"]
    ]


builder = StateGraph(State)

builder.add_node("orchestrator", orchestrator)
builder.add_node("llm_call", llm_call)
builder.add_node("synthesizer", synthesizer)

builder.add_edge(START, "orchestrator")

builder.add_conditional_edges(
    "orchestrator",
    assign_workers,
    {"llm_call": "llm_call"},
)

builder.add_edge("llm_call", "synthesizer")
builder.add_edge("synthesizer", END)

workflow = builder.compile()


# -------------------------
# FastAPI app
# -------------------------

app = FastAPI(
    title="Report Generator API",
    description="LangGraph Orchestrator-Worker Workflow",
    version="1.0"
)


# Request schema
class ReportRequest(BaseModel):
    topic: str


# Health check
@app.get("/")
def health():
    return {
        "status": "running"
    }


# Main endpoint
@app.post("/generate-report")
def generate_report(request: ReportRequest):

    result = workflow.invoke(
        {
            "topic": request.topic
        }
    )

    return {
        "final_report": result["final_report"]
    }