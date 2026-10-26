"""Small academic-demo uploads persisted with their owning database transaction."""
from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class MediaAsset(Base):
    __tablename__ = "media_assets"

    filename: Mapped[str] = mapped_column(String(180), primary_key=True)
    content_type: Mapped[str] = mapped_column(String(80), nullable=False)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
