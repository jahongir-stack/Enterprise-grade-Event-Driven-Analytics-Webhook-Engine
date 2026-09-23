"""Domen modellari — Event, Subscription, Delivery."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class Event(BaseModel):
    """Tizimga kiritiladigan xom hodisa."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(..., description="Masalan: 'user.signed_up', 'order.paid'")
    payload: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="unknown")
    occurred_at: datetime = Field(default_factory=_now)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if not v or "." not in v:
            raise ValueError("Event type 'namespace.action' formatida bo'lishi kerak (masalan 'order.paid').")
        return v


class Subscription(BaseModel):
    """Muayyan event turlariga obuna bo'lgan webhook manzili."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_url: str
    event_types: list[str] = Field(default_factory=list, description="'*' — barcha hodisalar")
    secret: str = Field(..., description="HMAC imzo uchun maxfiy kalit")
    active: bool = True
    max_retries: int = 5
    created_at: datetime = Field(default_factory=_now)

    def matches(self, event_type: str) -> bool:
        if not self.active:
            return False
        return "*" in self.event_types or event_type in self.event_types


class DeliveryAttempt(BaseModel):
    """Bitta webhook yetkazish urinishi haqida yozuv."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    subscription_id: str
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempt_number: int = 1
    status_code: Optional[int] = None
    error: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=_now)
