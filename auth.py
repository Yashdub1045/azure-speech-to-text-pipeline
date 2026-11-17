from fastapi import Header, HTTPException, Depends

from dependency import get_settings


def verify_api_key(
    x_api_key: str = Header(...),
    settings=Depends(get_settings)
):
    """
    Verifies the API key sent in the request header.
    """

    if x_api_key != settings["api_key"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    return x_api_key