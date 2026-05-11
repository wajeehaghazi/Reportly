import logging
import os

# Create logs folder automatically
os.makedirs("logs", exist_ok=True)

# Create logger
logger = logging.getLogger("reportly")

# Set logging level
logger.setLevel(logging.INFO)

# Create log format
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - Line:%(lineno)d - %(levelname)s - %(message)s"
)

# Save logs into file
file_handler = logging.FileHandler("logs/app.log")
file_handler.setFormatter(formatter)

# Show logs in terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)