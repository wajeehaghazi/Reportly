from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from state.state import Sections

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")
planner= model.with_structured_output(Sections)