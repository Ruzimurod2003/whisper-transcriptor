from dotenv import dotenv_values
from app.config.whisper_logging import write_log_info, write_log_error

# Load environment variables from the specified .env file
try:
    config = dotenv_values()
    write_log_info(f"Loaded config: {config}")
except Exception as e:
    write_log_error(f"Error loading .env file: {e}")
    config = {}
