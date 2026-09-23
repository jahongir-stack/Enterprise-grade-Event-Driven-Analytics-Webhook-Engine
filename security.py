"""Webhook payload'larini HMAC-SHA256 bilan imzolash va tekshirish."""

from __future__ import annotations

import hashlib
import hmac
import time


def sign_payload(secret: str, body: bytes, timestamp: int | None = None) -> str:
    """Stripe-uslubidagi 't=<ts>,v1=<hmac>' formatida imzo yaratadi.

    Timestamp imzoga kiritiladi — bu "replay attack" (eski so'rovni qayta
    yuborish) hujumlarining oldini oladi.
    """
    ts = timestamp or int(time.time())
    signed_payload = f"{ts}.".encode() + body
    digest = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={ts},v1={digest}"


def verify_signature(
    secret: str,
    body: bytes,
    signature_header: str,
    tolerance_seconds: int = 300,
) -> bool:
    """Kelgan webhook so'rovining haqiqiyligini tekshiradi.

    Vaqt farqi `tolerance_seconds`dan katta bo'lsa yoki imzo mos kelmasa,
    False qaytaradi — bu qabul qiluvchi tomon uchun himoya funksiyasi.
    """
    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        ts = int(parts["t"])
        received_digest = parts["v1"]
    except (KeyError, ValueError):
        return False

    if abs(time.time() - ts) > tolerance_seconds:
        return False

    expected = sign_payload(secret, body, timestamp=ts)
    expected_digest = expected.split("v1=")[1]

    return hmac.compare_digest(expected_digest, received_digest)
