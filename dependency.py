from fastapi import Depends
from azure.storage.blob import BlobServiceClient
import azure.cognitiveservices.speech as speechsdk

from config import validate_config


def get_settings():
    """
    Returns validated application settings.
    """
    return validate_config()


def get_blob_service(settings=Depends(get_settings)):
    """
    FastAPI dependency for BlobServiceClient.
    """
    return BlobServiceClient.from_connection_string(
        settings["connection_string"]
    )


# NEW: Shared factory for non-FastAPI code (batch scripts)
def create_blob_service_client():
    """
    Creates a BlobServiceClient that can be reused
    outside FastAPI (batch processing).
    """
    settings = validate_config()

    return BlobServiceClient.from_connection_string(
        settings["connection_string"]
    )


def get_speech_config(settings=Depends(get_settings)):
    """
    FastAPI dependency for Azure SpeechConfig.
    """
    return speechsdk.SpeechConfig(
        subscription=settings["speech_key"],
        region=settings["speech_region"]
    )