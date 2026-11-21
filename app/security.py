"""Authentication primitives for the single-owner app."""
import base64
import getpass
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass

PBKDF2_ITERATIONS = 600_000
SESSION_MAX_AGE = 8 * 60 * 60
LOGIN_CSRF_MAX_AGE = 15 * 60


@dataclass(frozen=True)
class AuthConfig:
    password_hash: str
    session_secret: bytes
    api_token_hash: str
    cookie_secure: bool


def _enc(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _dec(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _parse(encoded):
    try:
        algorithm, rounds, salt, digest = encoded.split("$", 3)
        rounds, salt, digest = int(rounds), _dec(salt), _dec(digest)
    except (ValueError, TypeError):
        raise ValueError("APP_PASSWORD_HASH is invalid.") from None
    if algorithm != "pbkdf2_sha256" or not 600_000 <= rounds <= 2_000_000 or len(salt) < 16 or len(digest) != 32:
        raise ValueError("APP_PASSWORD_HASH must be a generated PBKDF2-HMAC-SHA256 hash.")
    return rounds, salt, digest


def hash_password(password):
    if not isinstance(password, str) or not 12 <= len(password) <= 1024:
        raise ValueError("Use an app password between 12 and 1024 characters.")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256$" + str(PBKDF2_ITERATIONS) + "$" + _enc(salt) + "$" + _enc(digest)


def verify_password(password, encoded):
    try:
        rounds, salt, expected = _parse(encoded)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, UnicodeError):
        return False


def hash_api_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_api_token(token, config):
    return isinstance(token, str) and 32 <= len(token) <= 256 and hmac.compare_digest(
        hash_api_token(token), config.api_token_hash
    )


def load_auth_config():
    password_hash = os.getenv("APP_PASSWORD_HASH", "")
    session_secret = os.getenv("APP_SESSION_SECRET", "").encode()
    api_hash = os.getenv("APP_API_TOKEN_HASH", "").lower()
    missing = [name for name, value in (
        ("APP_PASSWORD_HASH", password_hash),
        ("APP_SESSION_SECRET", session_secret),
        ("APP_API_TOKEN_HASH", api_hash),
    ) if not value]
    if missing:
        raise RuntimeError("Missing authentication settings: " + ", ".join(missing) + ". Run python -m app.security.")
    try:
        _parse(password_hash)
    except ValueError as error:
        raise RuntimeError(str(error)) from None
    if len(session_secret) < 32:
        raise RuntimeError("APP_SESSION_SECRET must be at least 32 characters.")
    if len(api_hash) != 64 or any(c not in "0123456789abcdef" for c in api_hash):
        raise RuntimeError("APP_API_TOKEN_HASH must be a generated SHA-256 hex digest.")
    setting = os.getenv("APP_COOKIE_SECURE")
    if setting is None:
        secure = os.getenv("APP_ENV", "development").lower() in {"production", "prod"}
    elif setting.lower() in {"1", "true", "yes"}:
        secure = True
    elif setting.lower() in {"0", "false", "no"}:
        secure = False
    else:
        raise RuntimeError("APP_COOKIE_SECURE must be true or false.")
    if os.getenv("APP_ENV", "development").lower() in {"production", "prod"} and not secure:
        raise RuntimeError("APP_COOKIE_SECURE must be true in production.")
    return AuthConfig(password_hash, session_secret, api_hash, secure)


def create_session(config, now=None):
    issued = int(time.time() if now is None else now)
    csrf = secrets.token_urlsafe(32)
    payload = _enc(json.dumps({"iat": issued, "exp": issued + SESSION_MAX_AGE, "csrf": csrf},
                              separators=(",", ":")).encode())
    signature = hmac.new(config.session_secret, payload.encode(), hashlib.sha256).digest()
    return payload + "." + _enc(signature), csrf


def get_session_csrf_token(cookie, config, now=None):
    if not isinstance(cookie, str) or not cookie or len(cookie) > 2048:
        return None
    try:
        payload, signature = cookie.split(".", 1)
        expected = hmac.new(config.session_secret, payload.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _dec(signature)):
            return None
        data = json.loads(_dec(payload))
        current = int(time.time() if now is None else now)
        issued, expires, csrf = int(data["iat"]), int(data["exp"]), data["csrf"]
        if not isinstance(csrf, str) or not csrf or issued > current + 30 or expires <= current:
            return None
        if expires - issued != SESSION_MAX_AGE:
            return None
        return csrf
    except (ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError):
        return None


def create_login_csrf(config, now=None):
    issued = int(time.time() if now is None else now)
    payload = f"{issued}.{secrets.token_urlsafe(24)}"
    signature = hmac.new(config.session_secret, b"login:" + payload.encode(), hashlib.sha256).digest()
    return payload + "." + _enc(signature)


def verify_login_csrf(cookie, submitted, config, now=None):
    if not cookie or not submitted or len(cookie) > 512 or len(submitted) > 512:
        return False
    if not hmac.compare_digest(cookie, submitted):
        return False
    try:
        issued_text, nonce, signature = cookie.split(".", 2)
        issued = int(issued_text)
        current = int(time.time() if now is None else now)
        payload = f"{issued}.{nonce}"
        expected = hmac.new(config.session_secret, b"login:" + payload.encode(), hashlib.sha256).digest()
        return bool(nonce) and hmac.compare_digest(expected, _dec(signature)) and issued <= current + 30 and current - issued <= LOGIN_CSRF_MAX_AGE
    except (ValueError, TypeError, UnicodeError):
        return False


def _setup():
    password = getpass.getpass("Choose the app password (12+ characters): ")
    if password != getpass.getpass("Enter it again: "):
        raise SystemExit("Passwords did not match.")
    try:
        encoded = hash_password(password)
    except ValueError as error:
        raise SystemExit(str(error)) from None
    token = secrets.token_urlsafe(48)
    print("\nCopy these settings to your private .env file:\n")
    print(f"APP_PASSWORD_HASH={encoded}")
    print(f"APP_SESSION_SECRET={secrets.token_urlsafe(48)}")
    print(f"APP_API_TOKEN_HASH={hash_api_token(token)}")
    print("\nSave this bearer token in your API client secret settings; it is shown once:")
    print(token)


if __name__ == "__main__":
    _setup()

