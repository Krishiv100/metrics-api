from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import Response
import time
import uuid

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-w7a78u.example.com"
EMAIL = "24f3002540@ds.study.iitm.ac.in"


@app.middleware("http")
async def add_headers_and_cors(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    origin = request.headers.get("origin")

    # Handle OPTIONS preflight request
    if request.method == "OPTIONS" and request.url.path == "/stats":
        process_time = time.perf_counter() - start_time

        headers = {
            "X-Request-ID": request_id,
            "X-Process-Time": f"{process_time:.6f}",
        }

        # Only allowed origin gets CORS header
        if origin == ALLOWED_ORIGIN:
            headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            headers["Access-Control-Allow-Headers"] = "*"
            headers["Vary"] = "Origin"
            return Response(status_code=204, headers=headers)

        # Other origins rejected, no Access-Control-Allow-Origin header
        return Response(status_code=403, headers=headers)

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    # Add CORS only for allowed origin
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Vary"] = "Origin"

    return response


@app.get("/")
def home():
    return {"message": "Metrics API running"}


@app.get("/stats")
def get_stats(values: str = Query(...)):
    try:
        numbers = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except:
        raise HTTPException(status_code=400, detail="Invalid numbers")

    if len(numbers) == 0:
        raise HTTPException(status_code=400, detail="No values provided")

    total = sum(numbers)
    count = len(numbers)

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / count
    }