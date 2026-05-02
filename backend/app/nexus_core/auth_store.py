"""
Persistent user store and session management for Celestal Eye auth.

Users are persisted in a JSON file next to this module.  Passwords are hashed
with PBKDF2-HMAC-SHA256 using a random per-user salt so they are never stored
in plain text.

Sessions are kept in-memory for the lifetime of the process (acceptable for
this project scale).  A fresh session token is returned on every successful
register or login call.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from pathlib import Path
from threading import Lock
from typing import Dict, Optional, Tuple

# ── Storage paths ─────────────────────────────────────────────────────────────

_STORE_DIR = Path(os.environ.get("AUTH_STORE_DIR", Path(__file__).parent))
_USERS_FILE = _STORE_DIR / "users.json"

_lock = Lock()

# ── In-memory session store ───────────────────────────────────────────────────
# Maps session_token -> user_id
_sessions: Dict[str, str] = {}

# ── In-memory token hash cache ───────────────────────────────────────────────
# Maps SHA-256(raw_token) -> user_id for fast O(1) token lookups.
# Populated by issue_password_reset_token*; cleared on consume or expiry.
_token_hash_index: Dict[str, str] = {}

# ── Password helpers ──────────────────────────────────────────────────────────

_HASH_ITERS = 260_000  # NIST recommendation for PBKDF2-HMAC-SHA256 in 2024


def hash_password(password: str) -> str:
    """Return ``salt$hash`` for *password* using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(32)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _HASH_ITERS)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Return True iff *password* matches the stored hash produced by :func:`hash_password`."""
    try:
        salt, dk_hex = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _HASH_ITERS)
    return hmac.compare_digest(dk.hex(), dk_hex)


# ── Persistence helpers ───────────────────────────────────────────────────────

def _load_users() -> Dict[str, dict]:
    """Load the users store from disk; return {} if the file is missing/corrupt."""
    try:
        with open(_USERS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_users(users: Dict[str, dict]) -> None:
    """Persist *users* to disk, writing atomically via a temp file."""
    _STORE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _USERS_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(users, fh, indent=2)
    tmp.replace(_USERS_FILE)


# ── Public API ────────────────────────────────────────────────────────────────

def register_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    birth_date: Optional[str] = None,
) -> dict:
    """Create a new user record.

    Raises :class:`ValueError` if *email* is already registered.
    Returns the public user dict (no password hash).
    """
    email = email.strip().lower()
    with _lock:
        users = _load_users()
        # check for duplicate e-mail (O(n) is fine at this scale)
        for record in users.values():
            if record.get("email", "").lower() == email:
                raise ValueError(f"Email already registered: {email}")

        user_id = str(uuid.uuid4())
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        record = {
            "user_id": user_id,
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "full_name": f"{first_name.strip()} {last_name.strip()}".strip(),
            "email": email,
            "password_hash": hash_password(password),
            "birth_date": (birth_date or "").strip() or None,
            "created_at": now,
            "preferences": {},
        }
        users[user_id] = record
        _save_users(users)

    return _public_record(record)


def login_user(email: str, password: str) -> dict:
    """Verify credentials and return the public user dict.

    Raises :class:`ValueError` with a generic message on failure so that
    callers cannot infer which of email/password was wrong.
    """
    email = email.strip().lower()
    with _lock:
        users = _load_users()
        record = next(
            (r for r in users.values() if r.get("email", "").lower() == email),
            None,
        )

    if record is None or not verify_password(password, record.get("password_hash", "")):
        raise ValueError("Invalid email or password.")

    return _public_record(record)


def create_session(user_id: str) -> str:
    """Create a new session token for *user_id* and return it."""
    token = secrets.token_urlsafe(32)
    _sessions[token] = user_id
    return token


def get_user_by_session(token: str) -> Optional[dict]:
    """Return the public user dict for *token*, or None if the session is invalid."""
    user_id = _sessions.get(token)
    if not user_id:
        return None
    with _lock:
        users = _load_users()
    record = users.get(user_id)
    if not record:
        return None
    return _public_record(record)


def invalidate_session(token: str) -> None:
    """Remove *token* from the session store."""
    _sessions.pop(token, None)


def update_user_preferences(user_id: str, preferences: dict) -> dict:
    """Merge *preferences* into the stored record for *user_id*.

    Only recognised keys are written; unknown keys are silently ignored.
    Returns the updated public user dict.

    Raises :class:`ValueError` if *user_id* is not found.
    """
    allowed_keys = {
        "mental_state",
        "goals",
        "preferred_meditation_style",
        "dietary_preferences",
        "preferred_guide_time",
    }
    with _lock:
        users = _load_users()
        record = users.get(user_id)
        if record is None:
            raise ValueError(f"User not found: {user_id}")
        stored_prefs: dict = record.get("preferences") or {}
        for key, value in preferences.items():
            if key in allowed_keys:
                stored_prefs[key] = value
        record["preferences"] = stored_prefs
        users[user_id] = record
        _save_users(users)
    return _public_record(record)


def update_user_profile(
    user_id: str,
    birth_date: Optional[str] = None,
    birth_time: Optional[str] = None,
    location: Optional[str] = None,
    purchase_type: Optional[str] = None,
) -> dict:
    """Update profile fields for *user_id*.

    Only the provided (non-None) fields are updated; omitted fields are left
    unchanged.  Returns the updated public user dict.

    Raises :class:`ValueError` if *user_id* is not found.
    """
    with _lock:
        users = _load_users()
        record = users.get(user_id)
        if record is None:
            raise ValueError(f"User not found: {user_id}")

        # Update only the fields that were provided (non-None)
        if birth_date is not None:
            record["birth_date"] = birth_date.strip() or None
        if birth_time is not None:
            record["birth_time"] = birth_time.strip() or None
        if location is not None:
            record["location"] = location.strip() or None
        if purchase_type is not None:
            record["purchase_type"] = purchase_type.strip() or None

        users[user_id] = record
        _save_users(users)
    return _public_record(record)


def get_all_users() -> list:
    """Return a list of all public user dicts (no password hashes).

    Used by the daily-guide scheduler to iterate over registered users.
    """
    with _lock:
        users = _load_users()
    return [_public_record(r) for r in users.values()]


# ── Password-reset token helpers ──────────────────────────────────────────────

# Default TTL reduced to 15 minutes for tighter security.  Override via env.
_RESET_TOKEN_TTL = int(os.environ.get("PASSWORD_RESET_TOKEN_TTL_SECONDS", "900"))


def _hash_reset_token(token: str) -> str:
    """Return a SHA-256 hex digest of *token*."""
    return hashlib.sha256(token.encode()).hexdigest()


def issue_password_reset_token(email: str) -> Optional[str]:
    """Generate a password-reset token for the user with *email*.

    Stores a SHA-256 hash of the token and an expiry timestamp on the user
    record.  Returns the **raw** token (to be embedded in the reset link) if
    the user exists, or ``None`` if no matching user is found.
    """
    email = email.strip().lower()
    token = secrets.token_urlsafe(32)
    token_hash = _hash_reset_token(token)
    expires_at = time.time() + _RESET_TOKEN_TTL

    with _lock:
        users = _load_users()
        record = next(
            (r for r in users.values() if r.get("email", "").lower() == email),
            None,
        )
        if record is None:
            return None
        record["password_reset_token_hash"] = token_hash
        record["password_reset_expires_at"] = expires_at
        users[record["user_id"]] = record
        _save_users(users)
        _token_hash_index[token_hash] = record["user_id"]

    return token


def issue_password_reset_token_by_identifier(identifier: str) -> Tuple[Optional[str], Optional[str]]:
    """Generate a password-reset token by *email* or *username*.

    The *identifier* is matched case-insensitively first against ``email``,
    then against the ``username`` field (if present), and finally against the
    ``email`` prefix (the part before ``@``) as a convenience alias for users
    who do not remember their full address.  Returns the raw token and the
    resolved e-mail address as a tuple ``(token, email)`` so the caller can
    send the message, or ``(None, None)`` when no user is found.
    """
    identifier = identifier.strip()
    if not identifier:
        return None, None

    id_lower = identifier.lower()

    with _lock:
        users = _load_users()
        record = None

        # 1. Exact email match
        record = next(
            (r for r in users.values() if r.get("email", "").lower() == id_lower),
            None,
        )
        # 2. Explicit username field match
        if record is None:
            record = next(
                (r for r in users.values() if r.get("username", "").lower() == id_lower),
                None,
            )
        # 3. Email-prefix match (e.g. "alice" matches "alice@example.com")
        if record is None:
            record = next(
                (
                    r for r in users.values()
                    if r.get("email", "").lower().split("@")[0] == id_lower
                ),
                None,
            )
        if record is None:
            return None, None

        token = secrets.token_urlsafe(32)
        token_hash = _hash_reset_token(token)
        expires_at = time.time() + _RESET_TOKEN_TTL
        record["password_reset_token_hash"] = token_hash
        record["password_reset_expires_at"] = expires_at
        users[record["user_id"]] = record
        _save_users(users)
        _token_hash_index[token_hash] = record["user_id"]

    return token, record["email"]


def consume_password_reset_token(token: str, new_password: str) -> bool:
    """Verify *token*, update the password to *new_password*, and invalidate the token.

    Returns ``True`` on success.  Returns ``False`` if the token is invalid or
    expired (caller should respond with 400/401 without leaking details).

    Uses the in-memory :data:`_token_hash_index` for an O(1) lookup before
    falling back to a full scan so that the common hot-path is fast even when
    many users are registered.
    """
    token_hash = _hash_reset_token(token)
    now = time.time()

    with _lock:
        users = _load_users()

        # Fast path: consult the in-memory cache first
        cached_user_id = _token_hash_index.get(token_hash)
        if cached_user_id:
            record = users.get(cached_user_id)
            # Validate the cache entry still matches (guard against stale cache)
            if record is None or not hmac.compare_digest(
                record.get("password_reset_token_hash") or "", token_hash
            ):
                record = None

        # Slow path: full scan (covers restarts where cache is empty)
        if not cached_user_id or record is None:
            record = next(
                (
                    r for r in users.values()
                    if hmac.compare_digest(
                        r.get("password_reset_token_hash") or "",
                        token_hash,
                    )
                ),
                None,
            )

        if record is None:
            return False
        expires_at = record.get("password_reset_expires_at") or 0
        if now > expires_at:
            # Clean up expired token
            record.pop("password_reset_token_hash", None)
            record.pop("password_reset_expires_at", None)
            users[record["user_id"]] = record
            _save_users(users)
            _token_hash_index.pop(token_hash, None)
            return False
        # Update password and clear reset fields
        record["password_hash"] = hash_password(new_password)
        record.pop("password_reset_token_hash", None)
        record.pop("password_reset_expires_at", None)
        users[record["user_id"]] = record
        _save_users(users)
        _token_hash_index.pop(token_hash, None)

    return True


# ── Internal helpers ──────────────────────────────────────────────────────────

_RESET_SENSITIVE_KEYS = {"password_hash", "password_reset_token_hash", "password_reset_expires_at"}


def _public_record(record: dict) -> dict:
    """Return a copy of *record* without sensitive fields."""
    return {k: v for k, v in record.items() if k not in _RESET_SENSITIVE_KEYS}
