from dotenv import load_dotenv
import os

from langchain_community.tools.tavily_search import TavilySearchResults

from src.utils.logger import logger

logger.info(
    "Initializing Tavily Tool"
)

load_dotenv()


try:

    TAVILY_API_KEY = os.getenv(
        "TAVILY_API_KEY"
    )

    if not TAVILY_API_KEY:

        raise ValueError(
            "TAVILY_API_KEY is not set"
        )

    tavily_tool = TavilySearchResults(
        max_results=5
    )

    logger.info(
        "Tavily tool initialized successfully"
    )

except Exception as e:

    logger.error(
        f"Tavily initialization failed: {e}"
    )

    raise