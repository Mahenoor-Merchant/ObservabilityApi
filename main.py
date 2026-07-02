import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI()

# Allow the grader's browser to call us from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

YOUR_EMAIL = "your_login_email@example.com"  # <-- put your real login email here

# ---- Global state (lives in memory while the server runs) ----
START_TIME = time.time()          # used for uptime_s
REQUEST_COUNTER = 0                # used for http_requests_total
LOGS = []                          # our "diary" list

MAX_LOGS = 1000  # don't let the diary grow forever

def write_log(level, path, request_id):
    """Add one entry to our in-memory diary."""
    entry = {
        "level": level,
        "ts": time.time(),
        "path": path,
        "request_id": request_id,
    }
    LOGS.append(entry)
    if len(LOGS) > MAX_LOGS:
        LOGS.pop(0)  # remove oldest so memory doesn't grow forever

# ---- Middleware: runs on EVERY single request, no matter the endpoint ----
@app.middleware("http")
async def count_and_log_every_request(request: Request, call_next):
    global REQUEST_COUNTER
    REQUEST_COUNTER += 1
    request_id = str(uuid.uuid4())
    write_log("INFO", request.url.path, request_id)

    response = await call_next(request)
    return response

# ---- Endpoint 1: /work ----
@app.get("/work")
def work(n: int = 1):
    total = 0
    for i in range(n):
        total += 1  # pretend "work" — just counting
    return {"email": "25f2007833@ds.study.iitm.ac.in", "done": total}

# ---- Endpoint 2: /metrics ----
@app.get("/metrics")
def metrics():
    # Prometheus text format: a comment line + the metric line
    text = (
        "# HELP http_requests_total Total number of HTTP requests\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total {REQUEST_COUNTER}\n"
    )
    return PlainTextResponse(text)

# ---- Endpoint 3: /healthz ----
@app.get("/healthz")
def healthz():
    uptime = time.time() - START_TIME
    return {"status": "ok", "uptime_s": uptime}

# ---- Endpoint 4: /logs/tail ----
@app.get("/logs/tail")
def logs_tail(limit: int = 10):
    return LOGS[-limit:]