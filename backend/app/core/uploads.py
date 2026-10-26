from app.models.media_asset import MediaAsset


def persist_image(db, filename: str, content: bytes, ext: str):
    """Add bytes and reference in the same transaction; never write temporary disk."""
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    db.add(MediaAsset(filename=filename, content_type=mime[ext], content=content))
