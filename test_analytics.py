"""AnalyticsEngine testlari."""

import pytest

from event_engine.core.analytics import AnalyticsEngine
from event_engine.core.schema import Event


@pytest.mark.asyncio
async def test_record_increments_lifetime_counter():
    engine = AnalyticsEngine(window_seconds=60)
    await engine.record(Event(type="user.signed_up"))
    await engine.record(Event(type="user.signed_up"))
    await engine.record(Event(type="order.paid"))

    lifetime = engine.lifetime_counts()
    assert lifetime["user.signed_up"] == 2
    assert lifetime["order.paid"] == 1


@pytest.mark.asyncio
async def test_window_stats_totals():
    engine = AnalyticsEngine(window_seconds=60)
    for _ in range(5):
        await engine.record(Event(type="ui.click"))

    stats = engine.current_window_stats()
    assert stats.total_events == 5
    assert stats.events_by_type == {"ui.click": 5}
    assert stats.events_per_second == pytest.approx(5 / 60, rel=1e-3)


@pytest.mark.asyncio
async def test_window_evicts_old_events(monkeypatch):
    import event_engine.core.analytics as mod
    from datetime import datetime, timedelta, timezone

    engine = AnalyticsEngine(window_seconds=1)

    fixed_time = datetime(2025, 1, 1, tzinfo=timezone.utc)

    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_time

    monkeypatch.setattr(mod, "datetime", FakeDatetime)
    await engine.record(Event(type="old.event"))

    later_time = fixed_time + timedelta(seconds=5)

    class LaterDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return later_time

    monkeypatch.setattr(mod, "datetime", LaterDatetime)
    stats = engine.current_window_stats()
    assert stats.total_events == 0
