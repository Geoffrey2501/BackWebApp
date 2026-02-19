from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret-key")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
TOKEN_EXPIRY_HOURS = 8


def verify_admin_credentials(username: str, password: str) -> str | None:
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        payload = {
            "sub": username,
            "role": "admin",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return None


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
