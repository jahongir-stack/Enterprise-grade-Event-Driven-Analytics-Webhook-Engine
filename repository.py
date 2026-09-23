"""Repository qatlami — hozircha in-memory, kelajakda Postgres/Redis bilan almashtiriladi.

Interfeys (Protocol) orqali ajratilgan bo'lgani uchun, storage backend'ini
o'zgartirish qolgan kodga ta'sir qilmaydi — bu Dependency Inversion printsipi.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Protocol

from ..core.schema import DeliveryAttempt, Event, Subscription


class Repository(Protocol):
    async def save_event(self, event: Event) -> None: ...
    async def get_events(self, limit: int = 100) -> list[Event]: ...
    async def save_subscription(self, sub: Subscription) -> None: ...
    async def get_subscriptions(self) -> list[Subscription]: ...
    async def save_delivery(self, delivery: DeliveryAttempt) -> None: ...
    async def get_deliveries(self, event_id: str) -> list[DeliveryAttempt]: ...


class InMemoryRepository:
    """Testlar va kichik deploymentlar uchun thread-safe in-memory implementatsiya."""

    def __init__(self) -> None:
        self._events: list[Event] = []
        self._subscriptions: dict[str, Subscription] = {}
        self._deliveries: dict[str, list[DeliveryAttempt]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def save_event(self, event: Event) -> None:
        async with self._lock:
            self._events.append(event)

    async def get_events(self, limit: int = 100) -> list[Event]:
        async with self._lock:
            return list(self._events[-limit:])

    async def save_subscription(self, sub: Subscription) -> None:
        async with self._lock:
            self._subscriptions[sub.id] = sub

    async def get_subscriptions(self) -> list[Subscription]:
        async with self._lock:
            return list(self._subscriptions.values())

    async def save_delivery(self, delivery: DeliveryAttempt) -> None:
        async with self._lock:
            self._deliveries[delivery.event_id].append(delivery)

    async def get_deliveries(self, event_id: str) -> list[DeliveryAttempt]:
        async with self._lock:
            return list(self._deliveries.get(event_id, []))
