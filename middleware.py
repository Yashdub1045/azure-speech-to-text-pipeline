import time
import uuid

from fastapi import Request


async def logging_middleware(request: Request, call_next):
    """
    Logs every incoming request and outgoing response.
    """

    request_id = str(uuid.uuid4())

    start_time = time.time()

    print("\n==============================")
    print("Incoming Request")
    print("==============================")
    print(f"Request ID : {request_id}")
    print(f"Method     : {request.method}")
    print(f"Path       : {request.url.path}")

    response = await call_next(request)

    duration = time.time() - start_time

    print("------------------------------")
    print("Outgoing Response")
    print("------------------------------")
    print(f"Status     : {response.status_code}")
    print(f"Duration   : {duration:.2f}s")
    print("==============================")

    response.headers["X-Request-ID"] = request_id

    return response