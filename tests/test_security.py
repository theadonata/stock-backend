"""Tests for the password hashing / JWT issuing & verification primitives —
these back every protected route via app.api.deps.get_current_user, so a
break here is a break in auth for the whole API."""
from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_store_plaintext():
    hashed = hash_password("correct-horse-battery-staple")
    assert hashed != "correct-horse-battery-staple"


def test_verify_password_accepts_matching_plaintext():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_rejects_wrong_plaintext():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("wrong-password", hashed) is False


def test_access_token_round_trips_the_subject():
    token = create_access_token(subject="alice")
    assert decode_access_token(token) == "alice"


def test_decode_access_token_rejects_tampered_token():
    token = create_access_token(subject="alice")
    # Flip a character in the middle, not the last one: base64url's final
    # character in a segment can carry only padding bits depending on
    # segment length, so tampering it sometimes decodes to the exact same
    # bytes -- flakily leaving the token still valid. A middle character is
    # always fully significant.
    middle = len(token) // 2
    tampered = token[:middle] + ("A" if token[middle] != "A" else "B") + token[middle + 1 :]
    assert decode_access_token(tampered) is None


def test_decode_access_token_rejects_expired_token():
    # Negative expires_delta backdates `exp` into the past, so jose's own
    # expiry check rejects it -- same as an ordinary token that's timed out.
    token = create_access_token(subject="alice", expires_delta=timedelta(minutes=-1))
    assert decode_access_token(token) is None
