from src.schema.state import State
from src.utils.logger import logger


def synthesizer(state: State):

    """Combine all report sections"""

    try:

        logger.info("Synthesizing final report")

        completed_sections = state[
            "completed_sections"
        ]

        completed_report_sections = "\n\n---\n\n".join(
            completed_sections
        )

        return {
            "final_report": completed_report_sections
        }

    except Exception as e:

        logger.error(
            f"Error in synthesizer: {e}"
        )

        return {
            "final_report": ""
        }