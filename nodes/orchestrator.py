from langchain_core.messages import SystemMessage, HumanMessage
from langchain_protocol import Annotated
from langgraph.types import Send

from utils.planner import planner
from state.state import State


def orchestrator(state:State):
  """It will generate the plan for the report"""
  report_section= planner.invoke(
      [
          SystemMessage(content="Generate the plan for the report"),
          HumanMessage(content=f"Here is the report topic{state['topic']}")
      ]
  )
  return {"sections": report_section.sections}
