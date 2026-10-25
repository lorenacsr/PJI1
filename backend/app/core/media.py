"""Scoped, short-lived links for Flutter image controls (no login JWT in URLs)."""
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from jose import jwt, JWTError
from app.core.config import settings


def media_link(path: str | None) -> str | None:
    if not path or not path.startswith("/uploads/"):
        return path
    filename = path.split("?", 1)[0].removeprefix("/uploads/")
    token = jwt.encode({"purpose": "media", "file": filename,
                        "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
                       settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return "/uploads/" + filename + "?" + urlencode({"ticket": token})


def valid_media_ticket(ticket: str, filename: str) -> bool:
    try:
        data = jwt.decode(ticket, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return data.get("purpose") == "media" and data.get("file") == filename
    except JWTError:
        return False
