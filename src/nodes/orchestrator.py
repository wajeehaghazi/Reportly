from langchain_core.messages import SystemMessage, HumanMessage

from src.utils.planner import planner
from src.schema.state import State
from src.utils.logger import logger


async def orchestrator(state: State):

    """Generate report sections"""

    try:

        logger.info("Generating report sections")

        report_section = await planner.ainvoke(
            {
                "topic": state["topic"]
            }
        )

        return {
            "sections": report_section.sections
        }

    except Exception as e:

        logger.error(f"Error in orchestrator: {e}")

        return {
            "sections": []
        }