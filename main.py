from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import Response
import time
import uuid

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-w7a78u.example.com"
EMAIL = "24f3002540@ds.study.iitm.ac.in"


def cors_headers(origin: str | None):
    if origin == ALLOWED_ORIGIN:
        return {
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
            "Vary": "Origin",
        }
    return {}


@app.middleware("http")
async def add_headers(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    origin = request.headers.get("origin")

    # Handle CORS preflight manually
    if request.method == "OPTIONS":
        process_time = time.perf_counter() - start_time

        headers = {
            "X-Request-ID": request_id,
            "X-Process-Time": f"{process_time:.6f}",
        }

        # Allowed origin gets ACAO header
        if origin == ALLOWED_ORIGIN:
            headers.update(cors_headers(origin))
            return Response(status_code=204, headers=headers)

        # Evil origin gets NO Access-Control-Allow-Origin
        return Response(status_code=403, headers=headers)

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    # Add CORS only for allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers.update(cors_headers(origin))

    return response


@app.get("/")
def home():
    return {"message": "Metrics API running"}


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        numbers = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be integers")

    if len(numbers) == 0:
        raise HTTPException(status_code=400, detail="values cannot be empty")

    total = sum(numbers)
    count = len(numbers)

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / count,
    }