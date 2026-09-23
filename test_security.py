"""HMAC signature testlari."""

import time

from event_engine.core.security import sign_payload, verify_signature


def test_sign_and_verify_roundtrip():
    secret = "test-secret"
    body = b'{"hello":"world"}'
    signature = sign_payload(secret, body)
    assert verify_signature(secret, body, signature) is True


def test_verify_fails_with_wrong_secret():
    body = b'{"hello":"world"}'
    signature = sign_payload("secret-a", body)
    assert verify_signature("secret-b", body, signature) is False


def test_verify_fails_with_tampered_body():
    secret = "test-secret"
    signature = sign_payload(secret, b'{"amount":100}')
    assert verify_signature(secret, b'{"amount":999}', signature) is False


def test_verify_fails_on_expired_timestamp():
    secret = "test-secret"
    body = b"payload"
    old_ts = int(time.time()) - 1000
    signature = sign_payload(secret, body, timestamp=old_ts)
    assert verify_signature(secret, body, signature, tolerance_seconds=300) is False


def test_verify_fails_on_malformed_header():
    assert verify_signature("secret", b"body", "not-a-valid-header") is False
