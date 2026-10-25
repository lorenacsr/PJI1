"""Bounded image validation shared by checklist evidence and profile photos."""
from io import BytesIO
import warnings
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


async def read_image(file: UploadFile, limit: int) -> tuple[bytes, str]:
    content = await file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(413, "Imagem excede o limite permitido")
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    formats = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
    if ext not in formats:
        raise HTTPException(400, "Use JPG, PNG ou WEBP")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as image:
                if image.format != formats[ext] or image.width * image.height > 20_000_000:
                    raise ValueError("Formato ou dimensões inválidas")
                image.verify()
    except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombWarning,
            Image.DecompressionBombError):
        raise HTTPException(400, "Arquivo de imagem inválido")
    return content, "jpg" if ext == "jpeg" else ext
