import os
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter
from fastapi.responses import Response

TOOL_NAME = os.getenv("TOOL_NAME", "friend-keeper")

# HTTP metrics
http_requests = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["tool", "endpoint", "method", "status"]
)

http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["tool", "endpoint", "method"]
)

# Business metrics
talk_starters_generated = Counter(
    "talk_starters_generated_total",
    "Total talk starters generated",
    ["tool"]
)

friends_created = Counter(
    "friends_created_total",
    "Total friends added",
    ["tool"]
)

interactions_logged = Counter(
    "interactions_logged_total",
    "Total interactions logged",
    ["tool"]
)

# Payment metrics
payment_success = Counter(
    "payment_success_total",
    "Successful payments",
    ["tool", "product_sku"]
)

payment_revenue_cents = Counter(
    "payment_revenue_cents_total",
    "Total revenue in cents",
    ["tool"]
)

tokens_consumed = Counter(
    "tokens_consumed_total",
    "Paid tokens consumed",
    ["tool"]
)

free_trial_used = Counter(
    "free_trial_used_total",
    "Free trial uses",
    ["tool"]
)

# SEO metrics
page_views = Counter(
    "page_views_total",
    "Page views",
    ["tool", "page"]
)

crawler_visits = Counter(
    "crawler_visits_total",
    "Crawler/bot visits",
    ["tool", "bot"]
)

# Friendship health metrics
active_friendships = Gauge(
    "active_friendships",
    "Number of active friendships being tracked",
    ["tool"]
)

# Router for /metrics endpoint
metrics_router = APIRouter()


@metrics_router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
