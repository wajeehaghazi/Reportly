import traceback

from langchain_core.messages import (
    SystemMessage,
    HumanMessage
)

from src.utils.model import model

from src.schema.state import WorkerState

from src.tools.tavily_tool import tavily_tool

from src.utils.prompts.worker_prompt import (
    WORKER_PROMPT
)

from src.utils.logger import logger


async def llm_call(
    state: WorkerState
):

    """
    Generate professional report section
    using Tavily research
    """

    section_name = (
        state["section"].name
    )

    section_description = (
        state["section"].description
    )

    try:

        logger.info(
            f"Generating section: {section_name}"
        )

        # ---------------------------------------------------
        # TAVILY SEARCH
        # ---------------------------------------------------

        logger.info(
            f"Starting Tavily search for: {section_name}"
        )

        search_query = f"""
        {section_name}

        {section_description}
        """

        search_results = await tavily_tool.ainvoke(
            {
                "query": search_query
            }
        )

        logger.info(
            f"Tavily search completed for: {section_name}"
        )

        # ---------------------------------------------------
        # HANDLE EMPTY RESULTS
        # ---------------------------------------------------

        if not search_results:

            logger.warning(
                f"No Tavily results found for: {section_name}"
            )

        else:

            logger.info(
                f"Found {len(search_results)} search results"
            )

        # ---------------------------------------------------
        # FORMAT SEARCH RESULTS
        # ---------------------------------------------------

        formatted_results = ""

        if isinstance(
            search_results,
            list
        ):

            for idx, result in enumerate(
                search_results,
                start=1
            ):

                formatted_results += f"""

Result {idx}

Title:
{result.get("title", "")}

Summary:
{result.get("content", "")[:500]}

Source:
{result.get("url", "")}

-------------------------------------

"""

        else:

            formatted_results = str(
                search_results
            )

        # ---------------------------------------------------
        # GENERATE REPORT SECTION
        # ---------------------------------------------------

        logger.info(
            f"Sending section to LLM: {section_name}"
        )

        section = await model.ainvoke(
            [
                SystemMessage(
                    content=WORKER_PROMPT
                ),

                HumanMessage(
                    content=f"""

SECTION NAME:
{section_name}


SECTION DESCRIPTION:
{section_description}


INTERNET RESEARCH:
{formatted_results}


Write a professional executive-style
report section.

Keep content:
- concise
- highly readable
- well structured
- professional

Avoid giant walls of text.
"""
                )
            ]
        )

        logger.info(
            f"LLM generation completed: {section_name}"
        )

        logger.info(
            f"Completed section: {section_name}"
        )

        return {
            "completed_sections": [
                section.content
            ]
        }

    except Exception as e:

        logger.error(
            f"Worker failed for section: {section_name}"
        )

        logger.error(
            f"Error: {e}"
        )

        logger.error(
            traceback.format_exc()
        )

        raise e