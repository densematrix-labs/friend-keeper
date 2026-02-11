from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import re

from app.config import get_settings
from app.database import engine, Base
from app.api import friends, talk_starters, payment
from app.metrics import metrics_router, http_requests, http_request_duration, crawler_visits

# Create tables
Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="FriendKeeper API",
    description="Help ADHD individuals track and maintain friendships",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bot patterns for crawler detection
BOT_PATTERNS = ["Googlebot", "bingbot", "Baiduspider", "YandexBot", "DuckDuckBot", "Slurp", "facebookexternalhit"]


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track HTTP metrics and crawler visits."""
    start_time = time.time()
    
    # Check for crawlers
    ua = request.headers.get("user-agent", "")
    for bot in BOT_PATTERNS:
        if bot.lower() in ua.lower():
            crawler_visits.labels(tool=settings.tool_name, bot=bot).inc()
            break
    
    response = await call_next(request)
    
    # Record metrics (simplified endpoint)
    duration = time.time() - start_time
    endpoint = re.sub(r'/\d+', '/{id}', request.url.path)
    
    http_requests.labels(
        tool=settings.tool_name,
        endpoint=endpoint,
        method=request.method,
        status=response.status_code
    ).inc()
    
    http_request_duration.labels(
        tool=settings.tool_name,
        endpoint=endpoint,
        method=request.method
    ).observe(duration)
    
    return response


# Include routers
app.include_router(friends.router)
app.include_router(talk_starters.router)
app.include_router(payment.router)
app.include_router(metrics_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "FriendKeeper API",
        "version": "1.0.0",
        "description": "Help ADHD individuals track and maintain friendships"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "friend-keeper"}
