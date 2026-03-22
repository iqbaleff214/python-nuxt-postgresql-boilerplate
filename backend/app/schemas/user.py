from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime
from app.models.user import UserRole, UserStatus
import re


class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    is_2fa_enabled: bool
    last_login_at: Optional[datetime]
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.USER

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty")
        return v


class UpdateUserRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[UserRole] = None


class UpdateUserStatusRequest(BaseModel):
    status: UserStatus
    ban_reason: Optional[str] = None


class UserListParams(BaseModel):
    page: int = 1
    per_page: int = 20
    search: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_email_verified: Optional[bool] = None
    sort_by: str = "created_at"
    sort_dir: Literal["asc", "desc"] = "desc"
