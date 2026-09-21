
import os
from dotenv import load_dotenv

# Load variables from .env into the program
load_dotenv()

# Store all configuration in one place
CONFIG = {
    "speech_key": os.getenv("SPEECH_KEY"),
    "speech_region": os.getenv("SPEECH_REGION"),
    "connection_string": os.getenv("STORAGE_CONNECTION_STRING"),
    "audio_container": os.getenv("STORAGE_CONTAINER"),
    "transcript_container": os.getenv("TRANSCRIPT_CONTAINER"),
}

def validate_config():
    """
    Checks whether every required environment variable exists.
    Stops the application early if anything is missing.
    """

    missing = [key for key, value in CONFIG.items() if not value]

    if missing:
        raise ValueError(
            "Missing environment variables: " + ", ".join(missing)
        )

    return CONFIG