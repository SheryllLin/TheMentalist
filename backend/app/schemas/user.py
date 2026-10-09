from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator
from app.models.user import UserRole


class UserCreate(BaseModel):
    name: str
    # Use plain str instead of EmailStr — newer email-validator rejects .local/.test domains
    email: str
    password: str
    role: UserRole = UserRole.INVESTIGATOR

    @field_validator("email")
    @classmethod
    def email_basic_check(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Enter a valid email address")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return v.strip().lower()


class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    sub: str          # user id (UUID string)
    role: str
    exp: int
