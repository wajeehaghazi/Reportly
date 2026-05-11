import traceback

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from src.utils.model import model

from src.schema.state import (
    State,
    Sections
)

from src.utils.prompts.planner_prompt import (
    PLANNER_PROMPT
)

from src.utils.logger import logger


async def planner(
    state: State
):

    """
    Generate report sections
    """

    try:

        logger.info(
            "Planner Agent Started"
        )

        topic = state["topic"]

        logger.info(
            f"Planning sections for topic: {topic}"
        )

        structured_llm = model.with_structured_output(
            Sections
        )

        report_sections = await structured_llm.ainvoke(
            [
                SystemMessage(
                    content=PLANNER_PROMPT
                ),

                HumanMessage(
                    content=f"""
Generate sections for the topic:

{topic}
"""
                )
            ]
        )

        logger.info(
            "Planner Agent Completed"
        )

        logger.info(
            f"Generated {len(report_sections.sections)} sections"
        )

        return {
            "sections": report_sections.sections
        }

    except Exception as e:

        logger.error(
            f"Planner failed: {e}"
        )

        logger.error(
            traceback.format_exc()
        )

        raise e