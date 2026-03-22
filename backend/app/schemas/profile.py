from pydantic import BaseModel, EmailStr
from typing import Optional


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr


class BroadcastRequest(BaseModel):
    title: str
    body: str
