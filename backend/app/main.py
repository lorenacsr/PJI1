from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal, Base, get_db
from app.models.media_asset import MediaAsset
from app.db.init_db import init_db
from app.routers import auth, users, checklists, ws

# Import all models so SQLAlchemy registers them
from app.models import user, department, checklist  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await init_db(session)
    yield
    await engine.dispose()


import os as _os
_is_prod = _os.getenv("ENV", "development") == "production"

app = FastAPI(
    title="Pizzaria Checklist API",
    version="1.0.0",
    description="Sistema de gestão de checklist para pizzaria – multi-plataforma",
    lifespan=lifespan,
    docs_url=None if _is_prod else "/docs",
    redoc_url=None if _is_prod else "/redoc",
    openapi_url=None if _is_prod else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/uploads/{filename}")
async def media_file(filename: str, ticket: str = "", db: AsyncSession = Depends(get_db)):
    from app.core.media import valid_media_ticket
    if not valid_media_ticket(ticket, filename):
        raise HTTPException(403, "Link de imagem inválido ou expirado; atualize a tela")
    if "/" in filename or "\\" in filename or filename in (".", ".."):
        raise HTTPException(404, "Imagem não encontrada")
    asset = await db.get(MediaAsset, filename)
    if asset is not None:
        return Response(content=asset.content, media_type=asset.content_type, headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})
    # Compatibility for pre-existing local installations; all new uploads use DB.
    path = settings.upload_path / filename
    if not path.is_file():
        raise HTTPException(404, "Imagem não encontrada")
    return FileResponse(path, headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(checklists.router, prefix="/api/v1")
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
