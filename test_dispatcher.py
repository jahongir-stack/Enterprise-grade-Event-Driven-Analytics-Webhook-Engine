"""WebhookDispatcher testlari — fake HTTP client bilan retry logikasini tekshiradi."""

import pytest

from event_engine.core.schema import DeliveryStatus, Event, Subscription
from event_engine.storage.repository import InMemoryRepository
from event_engine.workers.dispatcher import WebhookDispatcher, compute_backoff


class FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class FakeHttpClient:
    """Har chaqiriqda oldindan belgilangan status kodlarni qaytaruvchi mock client."""

    def __init__(self, status_sequence: list[int]) -> None:
        self.status_sequence = status_sequence
        self.calls: list[dict] = []

    async def post(self, url, content, headers):
        self.calls.append({"url": url, "headers": headers})
        idx = len(self.calls) - 1
        status_code = self.status_sequence[min(idx, len(self.status_sequence) - 1)]
        return FakeResponse(status_code)


@pytest.fixture
def repo():
    return InMemoryRepository()


@pytest.mark.asyncio
async def test_successful_delivery_on_first_attempt(repo, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", lambda *_: _fast_sleep())
    http = FakeHttpClient([200])
    dispatcher = WebhookDispatcher(repo, http)

    sub = Subscription(target_url="https://example.com/hook", event_types=["*"], secret="s3cr3t")
    await repo.save_subscription(sub)
    event = Event(type="order.paid", payload={"amount": 100})

    await dispatcher.handle_event(event)

    deliveries = await repo.get_deliveries(event.id)
    assert len(deliveries) == 1
    assert deliveries[0].status == DeliveryStatus.SUCCESS
    assert len(http.calls) == 1


@pytest.mark.asyncio
async def test_retries_on_failure_then_succeeds(repo, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", lambda *_: _fast_sleep())
    http = FakeHttpClient([500, 500, 200])
    dispatcher = WebhookDispatcher(repo, http)

    sub = Subscription(
        target_url="https://example.com/hook", event_types=["*"], secret="s3cr3t", max_retries=5
    )
    await repo.save_subscription(sub)
    event = Event(type="order.paid")

    await dispatcher.handle_event(event)

    deliveries = await repo.get_deliveries(event.id)
    assert len(deliveries) == 3
    assert deliveries[-1].status == DeliveryStatus.SUCCESS
    assert len(http.calls) == 3


@pytest.mark.asyncio
async def test_dead_letter_after_max_retries(repo, monkeypatch):
    monkeypatch.setattr("asyncio.sleep", lambda *_: _fast_sleep())
    http = FakeHttpClient([500])
    dispatcher = WebhookDispatcher(repo, http)

    sub = Subscription(
        target_url="https://example.com/hook", event_types=["*"], secret="s3cr3t", max_retries=3
    )
    await repo.save_subscription(sub)
    event = Event(type="order.failed")

    await dispatcher.handle_event(event)

    deliveries = await repo.get_deliveries(event.id)
    assert len(deliveries) == 3
    assert all(d.status == DeliveryStatus.RETRYING for d in deliveries)


@pytest.mark.asyncio
async def test_non_matching_subscription_is_skipped(repo):
    http = FakeHttpClient([200])
    dispatcher = WebhookDispatcher(repo, http)

    sub = Subscription(target_url="https://example.com/hook", event_types=["user.signed_up"], secret="s")
    await repo.save_subscription(sub)
    event = Event(type="order.paid")

    await dispatcher.handle_event(event)

    assert len(http.calls) == 0


def test_backoff_increases_with_attempt():
    delays = [compute_backoff(i) for i in range(1, 5)]
    assert delays[0] < delays[-1]


async def _fast_sleep(*_):
    return None
