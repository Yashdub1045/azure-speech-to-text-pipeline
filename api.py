from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from speech_pipeline import process_audio_file

app = FastAPI(
    title="Azure Speech Pipeline",
    version="1.0"
)


class ProcessRequest(BaseModel):
    blob_name: str


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Azure Speech Pipeline"
    }


@app.post("/process")
def process_blob(request: ProcessRequest):

    try:
        process_audio_file(request.blob_name)

        return {
            "status": "success",
            "blob": request.blob_name
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )