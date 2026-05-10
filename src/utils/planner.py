from langchain_core.prompts import ChatPromptTemplate

from src.utils.model import model
from src.schema.state import Sections
from src.utils.prompts.planner_prompt import PLANNER_PROMPT


planner_prompt = ChatPromptTemplate.from_messages(
    [
    ("system",PLANNER_PROMPT),
        ("human","{topic}")])


planner = planner_prompt | model.with_structured_output(
    Sections
)