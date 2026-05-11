import traceback

from src.utils.planner import planner

from src.utils.logger import logger


async def orchestrator(
    state
):

    """
    Generate report sections
    using planner
    """

    try:

        logger.info(
            "Generating report sections"
        )

        # CALL PLANNER
        result = await planner(state)

        logger.info(
            "Planner completed successfully"
        )

        return result

    except Exception as e:

        logger.error(
            f"Error in orchestrator: {e}"
        )

        logger.error(
            traceback.format_exc()
        )

        raise e