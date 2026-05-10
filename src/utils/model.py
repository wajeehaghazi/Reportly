from dotenv import load_dotenv
import os

from langchain.chat_models import init_chat_model

from src.utils.logger import logger

load_dotenv()


try:

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY"
    )

    OPENAI_BASE_URL = os.getenv(
        "OPENAI_BASE_URL"
    )

    if not OPENAI_API_KEY:

        raise ValueError(
            "OPENAI_API_KEY is not set"
        )

    model = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

    logger.info(
        "OpenAI model initialized successfully"
    )

except Exception as e:

    logger.error(
        f"Model initialization failed: {e}"
    )

    raise