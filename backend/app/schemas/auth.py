"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_user(cls, user: object) -> "UserOut":
        return cls(
            id=str(getattr(user, "id")),
            email=getattr(user, "email"),
            full_name=getattr(user, "full_name", None),
            is_active=getattr(user, "is_active", True),
            is_verified=getattr(user, "is_verified", False),
        )
