from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models import User, StudentProfile, RoleEnum
from shared.security import hash_password, verify_password, create_access_token, get_current_user
from module1.schemas.auth import (
    RegisterRequest, LoginRequest, ChangePasswordRequest,
    SendResetCodeRequest, ResetPasswordRequest, TokenResponse, UserInfoResponse
)
from module1.services.mail import generate_code, save_code, verify_code, send_reset_code

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

@router.post("/register", response_model=UserInfoResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if len(body.username) < 2:
        raise HTTPException(400, "用户名至少2个字符")
    if len(body.password) < 6:
        raise HTTPException(400, "密码至少6位")
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(400, "用户名已存在")
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "邮箱已被注册")
    user = User(
        username=body.username,
        email=body.email or "",
        hashed_password=hash_password(body.password),
        role=RoleEnum(body.role),
    )
    db.add(user)
    db.flush()
    pass
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")
    if user.role != body.role:
        raise HTTPException(403, f"该账号不是{'教师' if body.role == 'teacher' else '学生'}账号")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token, role=user.role, username=user.username, user_id=user.id)

@router.get("/me", response_model=UserInfoResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/change-password")
def change_password(body: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(400, "原密码错误")
    if len(body.new_password) < 6:
        raise HTTPException(400, "新密码至少6位")
    current_user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"message": "密码修改成功"}

@router.post("/send-reset-code")
async def send_code_api(body: SendResetCodeRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(404, "该邮箱未注册")
    code = generate_code()
    save_code(body.email, code)
    try:
        await send_reset_code(body.email, code)
    except Exception as e:
        raise HTTPException(500, f"邮件发送失败：{str(e)}")
    return {"message": "验证码已发送，请查收邮件"}

@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(body.new_password) < 6:
        raise HTTPException(400, "新密码至少6位")
    if not verify_code(body.email, body.code):
        raise HTTPException(400, "验证码错误或已过期")
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.hashed_password = hash_password(body.new_password)
    db.commit()
    return {"message": "密码重置成功，请重新登录"}