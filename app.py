"""REST API — event ingestion, subscription boshqaruvi, analitika.

Dependency Injection FastAPI'ning o'z `Depends()` mexanizmi orqali amalga
oshiriladi — bu test yozishda real HTTP client/repository'ni mock bilan
almashtirishni osonlashtiradi.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from ..core.analytics import AnalyticsEngine
from ..core.bus import EventBus
from ..core.schema import Event, Subscription
from ..core.security import verify_signature
from ..storage.repository import InMemoryRepository, Repository
from ..workers.dispatcher import WebhookDispatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_engine.api")


class AppState:
    """Ilova butun umri davomida yashaydigan singleton komponentlar."""

    def __init__(self) -> None:
        self.repository: Repository = InMemoryRepository()
        self.analytics = AnalyticsEngine(window_seconds=300)
        self.bus = EventBus()
        self.http_client = httpx.AsyncClient(timeout=5.0)
        self.dispatcher = WebhookDispatcher(self.repository, self.http_client)


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.bus.subscribe(state.repository.save_event)
    state.bus.subscribe(state.analytics.record)
    state.bus.subscribe(state.dispatcher.handle_event)
    await state.bus.start()
    logger.info("Event Engine ishga tushdi.")
    yield
    await state.bus.stop()
    await state.http_client.aclose()
    logger.info("Event Engine to'xtatildi.")


app = FastAPI(
    title="Event-Driven Analytics & Webhook Engine",
    version="1.0.0",
    description="Enterprise-grade hodisalarni qabul qilish, tarqatish va real-vaqtli tahlil qilish tizimi.",
    lifespan=lifespan,
)


def get_state() -> AppState:
    return state


@app.post("/v1/events", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(event: Event, s: AppState = Depends(get_state)) -> dict:
    """Yangi hodisani qabul qiladi va darhol 202 qaytaradi (async processing)."""
    await s.bus.publish(event)
    return {"id": event.id, "status": "accepted"}


@app.post("/v1/subscriptions", status_code=status.HTTP_201_CREATED)
async def create_subscription(sub: Subscription, s: AppState = Depends(get_state)) -> Subscription:
    await s.repository.save_subscription(sub)
    return sub


@app.get("/v1/subscriptions")
async def list_subscriptions(s: AppState = Depends(get_state)) -> list[Subscription]:
    return await s.repository.get_subscriptions()


@app.get("/v1/analytics/window")
async def analytics_window(s: AppState = Depends(get_state)) -> dict:
    stats = s.analytics.current_window_stats()
    return {
        "total_events": stats.total_events,
        "events_by_type": stats.events_by_type,
        "events_per_second": stats.events_per_second,
        "window_seconds": stats.window_seconds,
    }


@app.get("/v1/analytics/lifetime")
async def analytics_lifetime(s: AppState = Depends(get_state)) -> dict:
    return {"events_by_type": s.analytics.lifetime_counts()}


@app.get("/v1/events/{event_id}/deliveries")
async def get_deliveries(event_id: str, s: AppState = Depends(get_state)) -> list:
    return await s.repository.get_deliveries(event_id)


@app.get("/healthz")
async def health(s: AppState = Depends(get_state)) -> dict:
    return {"status": "ok", "queue_size": s.bus.queue_size()}


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
