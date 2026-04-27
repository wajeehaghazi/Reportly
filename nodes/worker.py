from langchain_core.messages import SystemMessage, HumanMessage
from utils.model import model
from state.state import WorkerState

def llm_call(state:WorkerState):
  """This will write a section of the report"""
  section= model.invoke(
      [
          SystemMessage(content="Write a report section following the provided name and description. Include no preamble for each section. Use markdown formatting."),
          HumanMessage(content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}")
      ]
  )
  
  
  return {"completed_sections": [section.content]}