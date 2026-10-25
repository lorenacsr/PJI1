import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.department import Department
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.core.security import get_password_hash
from app.core.deps import get_current_user, get_current_manager
from app.core.config import settings
import aiofiles
import uuid as _uuid

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(get_current_manager),
):
    result = await db.execute(
        select(User)
        .options(selectinload(User.department))
        .order_by(User.name)
    )
    users = result.scalars().all()
    out = []
    for u in users:
        o = UserOut.model_validate(u)
        if u.department:
            o.department_name = u.department.display_name
        out.append(o)
    return out


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(get_current_manager),
):
    if actor.role != UserRole.admin and body.role != UserRole.employee:
        raise HTTPException(403, "Somente administrador pode criar contas privilegiadas")
    existing = await db.execute(select(User).where(User.email == body.email.lower().strip()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    if body.department_id is not None and not await db.get(Department, body.department_id):
        raise HTTPException(422, "Departamento inválido")
    user = User(
        name=body.name,
        email=body.email.lower().strip(),
        hashed_password=get_password_hash(body.password),
        role=body.role,
        department_id=body.department_id,
    )
    db.add(user)
    await db.flush()
    result = await db.execute(
        select(User).options(selectinload(User.department)).where(User.id == user.id)
    )
    user = result.scalar_one()
    out = UserOut.model_validate(user)
    if user.department:
        out.department_name = user.department.display_name
    return out


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    actor: User = Depends(get_current_manager),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if actor.role != UserRole.admin and (user.role != UserRole.employee or body.role not in (None, UserRole.employee)):
        raise HTTPException(403, "Somente administrador pode alterar contas privilegiadas")
    if body.department_id is not None and not await db.get(Department, body.department_id):
        raise HTTPException(422, "Departamento inválido")
    for field, value in body.model_dump(exclude_unset=True).items():
        if value is None and field in ("name", "email", "role", "is_active", "password"):
            raise HTTPException(422, "Campo obrigatório não pode ser nulo")
        if field == "password":
            user.hashed_password = get_password_hash(value)
        else:
            setattr(user, field, value)
    await db.flush()
    result2 = await db.execute(
        select(User).options(selectinload(User.department)).where(User.id == user_id)
    )
    user = result2.scalar_one()
    out = UserOut.model_validate(user)
    if user.department:
        out.department_name = user.department.display_name
    return out


_AVATAR_ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}
_AVATAR_ALLOWED_MAGIC = {
    b"\xff\xd8\xff": "jpg",   # JPEG
    b"\x89PNG":      "png",   # PNG
    b"RIFF":         "webp",  # WebP (RIFF....WEBP)
}
_AVATAR_MAX_SIZE = 3 * 1024 * 1024  # 3 MB


@router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.core.images import read_image
    content, ext = await read_image(file, _AVATAR_MAX_SIZE)
    filename = f"avatar_{current_user.id}_{_uuid.uuid4().hex}.{ext}"
    filepath = settings.upload_path / filename

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    current_user.avatar_url = f"/uploads/{filename}"
    await db.flush()
    out = UserOut.model_validate(current_user)
    if current_user.department:
        out.department_name = current_user.department.display_name
    return out
