from pymongo import MongoClient
from app.config.configuration import config
from app.config.whisper_logging import write_log_error, write_log_info

# Ensure DB_HOST, DB_PORT, DB_USER, and DB_PASSWORD are set in the config
db_host = config.get("DB_HOST")
db_port = config.get("DB_PORT")
db_user = config.get("DB_USER")
db_password = config.get("DB_PASSWORD")

if not db_host or not db_port or not db_user or not db_password:
    write_log_error(
        "Database host, port, username, and password must be specified in the configuration."
    )
    raise ValueError(
        "Database host, port, username, and password must be specified in the configuration."
    )

# Create a MongoDB client using the host, port, username, and password from the configuration
try:
    client = MongoClient(f"mongodb://{db_user}:{db_password}@{db_host}:{db_port}/")
    # client = MongoClient(f"mongodb://localhost:27017")
    write_log_info("MongoDB client created successfully.")
except Exception as e:
    write_log_error(f"Error creating MongoDB client: {e}")
    client = None
