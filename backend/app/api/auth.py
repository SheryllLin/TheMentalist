"""
Authentication endpoints: register, login, me.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token
from app.services.auth import AuthService, get_current_user
from app.utils.audit import log_action

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await AuthService.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=AuthService.hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.flush()
    await log_action(db, "USER_REGISTER", user_id=user.id, metadata={"email": payload.email})
    return user


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = AuthService.create_access_token(user)
    ip = request.client.host if request.client else None
    await log_action(db, "USER_LOGIN", user_id=user.id, ip_address=ip)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # JWT is stateless; client discards the token.
    # We record the logout for audit purposes.
    await log_action(db, "USER_LOGOUT", user_id=current_user.id)
