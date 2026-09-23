"""Webhooklarni yetkazish — exponential backoff + jitter bilan qayta urinish.

Enterprise webhook tizimlarining (Stripe, GitHub, Svix) asosiy patternlari:
1. Har bir urinish HMAC bilan imzolanadi (soxta so'rovlarning oldini olish)
2. Muvaffaqiyatsizlikda darhol emas, ekspotensial kechikish bilan qayta urinadi
3. "Jitter" (tasodifiy qo'shimcha) — bir vaqtda ko'p webhook qayta urinib,
   qabul qiluvchi serverni "thundering herd" bilan qulatib qo'ymasligi uchun
4. max_retries'dan keyin "dead letter" holatiga o'tadi — kuzatib borish mumkin
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Protocol

from ..core.schema import DeliveryAttempt, DeliveryStatus, Event, Subscription
from ..core.security import sign_payload
from ..storage.repository import Repository

logger = logging.getLogger("event_engine.dispatcher")


class HttpClient(Protocol):
    """Test uchun almashtirilishi mumkin bo'lgan HTTP client interfeysi."""

    async def post(self, url: str, content: bytes, headers: dict) -> "HttpResponse": ...


class HttpResponse(Protocol):
    status_code: int


def compute_backoff(attempt: int, base: float = 2.0, cap: float = 60.0) -> float:
    """Exponensial backoff + jitter: 2^attempt soniya, cap bilan cheklangan."""
    raw = min(cap, base**attempt)
    jitter = random.uniform(0, raw * 0.25)
    return raw + jitter


class WebhookDispatcher:
    def __init__(self, repository: Repository, http_client: HttpClient, max_concurrency: int = 20) -> None:
        self.repo = repository
        self.http = http_client
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def handle_event(self, event: Event) -> None:
        """EventBus tomonidan chaqiriladigan asosiy handler: mos obunachilarni topib, yetkazadi."""
        subscriptions = await self.repo.get_subscriptions()
        matching = [s for s in subscriptions if s.matches(event.type)]

        await asyncio.gather(*(self._deliver_with_retry(event, sub) for sub in matching))

    async def _deliver_with_retry(self, event: Event, sub: Subscription) -> None:
        async with self._semaphore:
            attempt_number = 1
            while attempt_number <= sub.max_retries:
                delivery = await self._attempt_delivery(event, sub, attempt_number)
                await self.repo.save_delivery(delivery)

                if delivery.status == DeliveryStatus.SUCCESS:
                    return

                if attempt_number == sub.max_retries:
                    logger.warning(
                        "Dead letter: event=%s subscription=%s barcha %d urinish muvaffaqiyatsiz.",
                        event.id, sub.id, sub.max_retries,
                    )
                    return

                delay = compute_backoff(attempt_number)
                await asyncio.sleep(delay)
                attempt_number += 1

    async def _attempt_delivery(self, event: Event, sub: Subscription, attempt_number: int) -> DeliveryAttempt:
        body = json.dumps(event.model_dump(mode="json")).encode()
        signature = sign_payload(sub.secret, body)
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
            "X-Webhook-Event-Type": event.type,
            "X-Webhook-Attempt": str(attempt_number),
        }

        try:
            response = await self.http.post(sub.target_url, content=body, headers=headers)
            success = 200 <= response.status_code < 300
            return DeliveryAttempt(
                event_id=event.id,
                subscription_id=sub.id,
                status=DeliveryStatus.SUCCESS if success else DeliveryStatus.RETRYING,
                attempt_number=attempt_number,
                status_code=response.status_code,
            )
        except Exception as exc:  # tarmoq xatosi, timeout va h.k.
            return DeliveryAttempt(
                event_id=event.id,
                subscription_id=sub.id,
                status=DeliveryStatus.RETRYING,
                attempt_number=attempt_number,
                error=str(exc),
            )
