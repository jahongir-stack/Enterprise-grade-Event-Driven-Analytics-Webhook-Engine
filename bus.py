"""Ichki event bus — kelayotgan hodisalarni obunachilarga tarqatadi.

Nega asyncio.Queue? Chunki ingestion (POST /events) darhol 202 qaytarishi
kerak, webhook yetkazish esa orqa fonda, tezlik cheklovisiz davom etadi.
Bu producer-consumer patternning klassik qo'llanilishi.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable

from .schema import Event

logger = logging.getLogger("event_engine.bus")

Handler = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self, max_queue_size: int = 10_000) -> None:
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=max_queue_size)
        self._handlers: list[Handler] = []
        self._worker_task: asyncio.Task | None = None
        self._running = False

    def subscribe(self, handler: Handler) -> None:
        """Har bir hodisa kelganda chaqiriladigan handlerni ro'yxatdan o'tkazadi."""
        self._handlers.append(handler)

    async def publish(self, event: Event) -> None:
        """Hodisani navbatga qo'yadi. Navbat to'lgan bo'lsa, backpressure sifatida kutadi."""
        await self._queue.put(event)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._worker_task = asyncio.create_task(self._run())
        logger.info("EventBus ishga tushdi.")

    async def stop(self) -> None:
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus to'xtatildi.")

    async def _run(self) -> None:
        while self._running:
            event = await self._queue.get()
            await self._dispatch(event)
            self._queue.task_done()

    async def _dispatch(self, event: Event) -> None:
        # Har bir handler mustaqil ishlaydi — bittasi xato bersa, boshqalari to'xtamaydi.
        results = await asyncio.gather(
            *(self._safe_call(h, event) for h in self._handlers),
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception):
                logger.error("Handler xatosi: %s", r)

    async def _safe_call(self, handler: Handler, event: Event) -> None:
        try:
            await handler(event)
        except Exception:
            logger.exception("Handler '%s' event '%s' ustida ishlov berishda xato.", handler, event.id)
            raise

    def queue_size(self) -> int:
        return self._queue.qsize()
