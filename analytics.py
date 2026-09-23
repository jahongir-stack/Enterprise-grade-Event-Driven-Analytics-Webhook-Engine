"""Real-vaqtli analitika — sliding window asosida event oqimini agregatsiya qiladi.

Har bir event uchun butun tarixni saqlab, har safar qayta hisoblash O(n) va
xotira uchun qimmat. Buning o'rniga `deque` bilan faqat window ichidagi
hodisalarni saqlaymiz — bu klassik "sliding window counter" patterni.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from .schema import Event


@dataclass
class WindowStats:
    total_events: int
    events_by_type: dict[str, int]
    events_per_second: float
    window_seconds: int


class AnalyticsEngine:
    def __init__(self, window_seconds: int = 300) -> None:
        self.window_seconds = window_seconds
        self._timestamps: deque[datetime] = deque()
        self._types: deque[str] = deque()
        self._lifetime_counter: Counter[str] = Counter()

    async def record(self, event: Event) -> None:
        now = datetime.now(timezone.utc)
        self._timestamps.append(now)
        self._types.append(event.type)
        self._lifetime_counter[event.type] += 1
        self._evict_expired(now)

    def _evict_expired(self, now: datetime) -> None:
        cutoff = now - timedelta(seconds=self.window_seconds)
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
            self._types.popleft()

    def current_window_stats(self) -> WindowStats:
        now = datetime.now(timezone.utc)
        self._evict_expired(now)

        counts = Counter(self._types)
        total = sum(counts.values())
        eps = total / self.window_seconds if self.window_seconds else 0.0

        return WindowStats(
            total_events=total,
            events_by_type=dict(counts),
            events_per_second=round(eps, 4),
            window_seconds=self.window_seconds,
        )

    def lifetime_counts(self) -> dict[str, int]:
        return dict(self._lifetime_counter)
