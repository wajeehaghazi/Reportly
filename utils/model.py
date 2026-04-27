from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

model = init_chat_model(
    model="gpt-4o-mini",
    model_provider="openai",
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)