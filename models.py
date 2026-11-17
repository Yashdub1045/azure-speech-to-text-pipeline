from pydantic import BaseModel, Field

class ProcessRequest(BaseModel):
    blob_name: str = Field(
        min_length=5,
        description="Audio file inside the Blob Storage audio container."
    )

class ProcessResponse(BaseModel):
    status: str
    blob: str