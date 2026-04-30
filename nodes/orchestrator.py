from langchain_core.messages import SystemMessage, HumanMessage
from langchain_protocol import Annotated
from langgraph.types import Send

from utils.planner import planner
from state.state import State


async def orchestrator(state:State):
  """It will generate the plan for the report"""
  try:
    report_section= await planner.ainvoke(
        [
            SystemMessage(content="Generate the plan for the report"),
            HumanMessage(content=f"Here is the report topic{state['topic']}")
        ]
    )
    return {"sections": report_section.sections}
  except Exception as e:
    print (f"Error in orchestrator: {e}")
  return {"sections": []}
  