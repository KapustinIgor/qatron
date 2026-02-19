"""Unit tests for app.core.security."""

import pytest

from app.core.security import (
    decode_access_token,
    create_access_token,
    verify_password,
    get_password_hash,
    generate_service_token,
    hash_service_token,
)


def test_password_hash_roundtrip():
    """Hashing and verifying a password works."""
    password = "test-secret-password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_access_token():
    """JWT create and decode roundtrip."""
    payload = {"sub": "123", "scope": "user"}
    token = create_access_token(data=payload)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["scope"] == "user"
    assert "exp" in decoded


def test_decode_invalid_token_returns_none():
    """Invalid or malformed token decodes to None."""
    assert decode_access_token("invalid") is None
    assert decode_access_token("") is None


def test_generate_service_token_format():
    """Service token is a non-empty URL-safe string."""
    token = generate_service_token()
    assert isinstance(token, str)
    assert len(token) >= 32
    assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in token)


def test_hash_service_token():
    """Hashing a service token returns a bcrypt-style hash."""
    plain = "my-service-token"
    hashed = hash_service_token(plain)
    assert hashed != plain
    assert hashed.startswith("$2")  # bcrypt prefix
