from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def queue_notification(session, user_id, data):
    session.info.setdefault("notifications_after_commit", []).append((user_id, data))


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            from app.routers.ws import manager
            for user_id, data in session.info.pop("notifications_after_commit", []):
                await manager.send_notification(user_id, data)
        except Exception:
            await session.rollback()
            raise
