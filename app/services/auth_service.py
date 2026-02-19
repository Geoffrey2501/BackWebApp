from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt
from werkzeug.security import check_password_hash, generate_password_hash

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret-key")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD_HASH contient le hash du mot de passe (genere avec generate_password_hash)
# Fallback : si ADMIN_PASSWORD est fourni en clair, on le hashe au demarrage
_raw_password = os.environ.get("ADMIN_PASSWORD", "admin")
_password_hash = os.environ.get("ADMIN_PASSWORD_HASH", "")
ADMIN_PASSWORD_HASH = _password_hash if _password_hash else generate_password_hash(_raw_password)
TOKEN_EXPIRY_HOURS = 8


def verify_admin_credentials(username: str, password: str) -> str | None:
    if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
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
