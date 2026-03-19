from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models import Class, StudentProfile, User
from shared.security import get_current_user, require_teacher
from pydantic import BaseModel
import random, string

router = APIRouter(prefix="/api/v1/classes", tags=["班级管理"])


class CreateClassRequest(BaseModel):
    name: str


class JoinClassRequest(BaseModel):
    class_code: str
    student_no: str


def gen_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# ── 教师：创建班级 ────────────────────────────────────────────────
@router.post("/", status_code=201)
def create_class(
    body: CreateClassRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    if len(body.name.strip()) < 2:
        raise HTTPException(400, "班级名称至少2个字符")
    # 生成唯一邀请码
    while True:
        code = gen_code()
        if not db.query(Class).filter(Class.code == code).first():
            break
    class_ = Class(name=body.name.strip(), code=code, teacher_id=current_user.id)
    db.add(class_)
    db.commit()
    db.refresh(class_)
    return {"id": class_.id, "name": class_.name, "code": class_.code}


# ── 教师：查看自己的班级列表 ──────────────────────────────────────
@router.get("/my")
def my_classes(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    classes = db.query(Class).filter(Class.teacher_id == current_user.id).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "student_count": db.query(StudentProfile).filter(StudentProfile.class_id == c.id).count(),
            "created_at": c.created_at,
        }
        for c in classes
    ]


# ── 教师：查看班级学生列表 ────────────────────────────────────────
@router.get("/{class_id}/students")
def class_students(
    class_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    class_ = db.query(Class).filter(Class.id == class_id, Class.teacher_id == current_user.id).first()
    if not class_:
        raise HTTPException(404, "班级不存在或无权限")
    profiles = db.query(StudentProfile).filter(StudentProfile.class_id == class_id).all()
    return [
        {
            "student_profile_id": p.id,
            "user_id": p.user_id,
            "username": p.user.username,
            "student_no": p.student_no,
        }
        for p in profiles
    ]


# ── 学生：加入班级 ────────────────────────────────────────────────
@router.post("/join")
def join_class(
    body: JoinClassRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(403, "仅学生可加入班级")
    class_ = db.query(Class).filter(Class.code == body.class_code).first()
    if not class_:
        raise HTTPException(404, "邀请码无效")
    # 检查是否已加入
    exists = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id,
        StudentProfile.class_id == class_.id
    ).first()
    if exists:
        raise HTTPException(400, "已加入该班级")
    profile = StudentProfile(
        user_id=current_user.id,
        class_id=class_.id,
        student_no=body.student_no,
    )
    db.add(profile)
    db.commit()
    return {"message": f"成功加入班级：{class_.name}"}


# ── 学生：查看已加入的班级 ────────────────────────────────────────
@router.get("/joined")
def joined_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(403, "仅学生可查看")
    profiles = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).all()
    return [
        {
            "class_id": p.class_id,
            "class_name": p.class_.name,
            "class_code": p.class_.code,
            "student_no": p.student_no,
            "teacher": p.class_.teacher.username,
        }
        for p in profiles
    ]