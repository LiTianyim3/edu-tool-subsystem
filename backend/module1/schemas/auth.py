from pydantic import BaseModel
from typing import Literal

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Literal["teacher", "student"]
    student_no: str | None = None

class LoginRequest(BaseModel):
    username: str
    password: str
    role: Literal["teacher", "student"]

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class SendResetCodeRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: int

class UserInfoResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    class Config:
        from_attributes = True