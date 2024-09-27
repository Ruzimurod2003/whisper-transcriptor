from app.config.database import client
from app.config.whisper_logging import write_log_error, write_log_info

# Ensure the client is valid
if not client:
    write_log_error("MongoDB client is not initialized.")
    raise ValueError("MongoDB client is not initialized.")

# Access the 'whisper_db' database
try:
    whisper_db = client["whisper_db"]
    write_log_info("Accessed 'whisper_db' database successfully.")
except Exception as e:
    write_log_error(f"Error accessing 'whisper_db' database: {e}")
    whisper_db = None

# Access the 'audio_files' collection
if whisper_db is not None:  # Corrected check
    try:
        audio_files = whisper_db["audio_files"]
        write_log_info("Accessed 'audio_files' collection successfully.")

        progress_statuses = whisper_db["progress_statuses"]
        write_log_info("Accessed 'progress_statuses' collection successfully.")
    except Exception as e:
        write_log_error(f"Error accessing 'audio_files' collection: {e}")
        audio_files = None
else:
    audio_files = None
