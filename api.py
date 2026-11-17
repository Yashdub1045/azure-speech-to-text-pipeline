from fastapi import FastAPI, HTTPException, Depends
from auth import verify_api_key

from models import ProcessRequest, ProcessResponse
from speech_pipeline import process_audio_file
from dependency import get_settings, get_blob_service, get_speech_config
from middleware import logging_middleware

app = FastAPI(
    title="Azure Speech-to-Text API",
    description="Process audio files stored in Azure Blob Storage using Azure Speech Service.",
    version="1.0.0"
)
app.middleware("http")(logging_middleware)


@app.get("/")
def root():
    return {
        "message": "Azure Speech-to-Text API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "Azure Speech Pipeline",
        "version": "1.0.0"
    }


@app.post("/process", response_model=ProcessResponse)
def process_blob(
    request: ProcessRequest,
    settings=Depends(get_settings),
    blob_service=Depends(get_blob_service),
    speech_config=Depends(get_speech_config),
    api_key=Depends(verify_api_key)
):

    process_audio_file(
        blob_name=request.blob_name,
        blob_service=blob_service,
        speech_config=speech_config,
        config=settings
    )

    return ProcessResponse(
        status="success",
        blob=request.blob_name
    )