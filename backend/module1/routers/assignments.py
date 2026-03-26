from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models import Assignment, Submission, GradingRule, Class, StudentProfile, User, StatusEnum
from shared.security import require_teacher, get_current_user
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import os, shutil, uuid
from datetime import timezone
from module1.services.ai_grader import ai_grade
from shared.models import AIGradingResult

AI_MODEL = os.getenv("AI_MODEL", "deepseek-ai/DeepSeek-V3")

router = APIRouter(prefix="/api/v1/assignments", tags=["作业管理"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class CreateAssignmentRequest(BaseModel):
    class_id: int
    title: str
    description: Optional[str] = None
    deadline: datetime
    max_score: int = 100


class CreateRuleRequest(BaseModel):
    name: str
    max_score: int = 100
    late_score: int = 60
    quality_tiers: list = []
    prompt_template: str


class UpdateScoreRequest(BaseModel):
    final_score: int


# ── 教师：创建评分规则 ────────────────────────────────────────────
@router.post("/rules", status_code=201)
def create_rule(
    body: CreateRuleRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    rule = GradingRule(
        name=body.name,
        max_score=body.max_score,
        late_score=body.late_score,
        quality_tiers=body.quality_tiers,
        prompt_template=body.prompt_template,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "name": rule.name}


# ── 教师：查看评分规则列表 ────────────────────────────────────────
@router.get("/rules")
def list_rules(
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    rules = db.query(GradingRule).all()
    return [{"id": r.id, "name": r.name, "max_score": r.max_score, "late_score": r.late_score} for r in rules]


# ── 教师：发布作业 ────────────────────────────────────────────────
@router.post("/", status_code=201)
async def create_assignment(
    class_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    deadline: str = Form(...),
    max_score: int = Form(100),
    rule_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    class_ = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    if not class_:
        raise HTTPException(404, "班级不存在或无权限")

    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
    if deadline_dt.replace(tzinfo=None) <= datetime.utcnow():
        raise HTTPException(400, "截止时间必须晚于当前时间")

    # 处理附件
    file_path = None
    if file and file.filename:
        allowed = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".ppt", ".pptx"}
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            raise HTTPException(400, f"不支持的文件类型")
        filename = f"assignment_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    assignment = Assignment(
        class_id=class_id,
        title=title,
        description=description,
        deadline=deadline_dt.replace(tzinfo=None),
        max_score=max_score,
        file_path=file_path,
        rule_id=rule_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {
        "id": assignment.id,
        "title": assignment.title,
        "deadline": assignment.deadline,
        "max_score": assignment.max_score,
        "file_path": assignment.file_path,
    }


# ── 教师：查看某班级的作业列表 ────────────────────────────────────
@router.get("/class/{class_id}")
def list_assignments_by_class(
    class_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    class_ = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user.id
    ).first()
    if not class_:
        raise HTTPException(404, "班级不存在或无权限")
    assignments = db.query(Assignment).filter(Assignment.class_id == class_id).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "deadline": a.deadline,
            "max_score": a.max_score,
            "submission_count": db.query(Submission).filter(Submission.assignment_id == a.id).count(),
            "created_at": a.created_at,
        }
        for a in assignments
    ]


# ── 学生：查看自己班级的作业列表 ──────────────────────────────────
@router.get("/my")
def my_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(403, "仅学生可查看")
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(404, "请先加入班级")

    assignments = db.query(Assignment).filter(Assignment.class_id == profile.class_id).all()
    result = []
    for a in assignments:
        submission = db.query(Submission).filter(
            Submission.assignment_id == a.id,
            Submission.student_id == profile.id
        ).first()
        result.append({
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "deadline": a.deadline,
            "max_score": a.max_score,
            "file_path": a.file_path,
            "submitted": submission is not None,
            "final_score": submission.final_score if submission else None,
            "status": submission.status if submission else None,
            "is_late": submission.is_late if submission else None,
        })
    return result


# ── 学生：上传提交作业 ────────────────────────────────────────────
@router.post("/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "student":
        raise HTTPException(403, "仅学生可提交")

    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(404, "作业不存在")

    profile = db.query(StudentProfile).filter(
        StudentProfile.user_id == current_user.id,
        StudentProfile.class_id == assignment.class_id
    ).first()
    if not profile:
        raise HTTPException(403, "你不在该作业对应的班级中")

    # 检查是否已提交
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == profile.id
    ).first()
    if existing:
        raise HTTPException(400, "已提交过该作业，如需修改请联系教师")

    # 校验文件类型
    allowed = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"不支持的文件类型，仅支持：{', '.join(allowed)}")

    # 保存文件
    filename = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 判断是否迟交
    is_late = datetime.utcnow() > assignment.deadline

    submission = Submission(
        assignment_id=assignment_id,
        student_id=profile.id,
        file_path=save_path,
        is_late=is_late,
        status=StatusEnum.pending,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return {
        "message": "提交成功" + ("（迟交）" if is_late else ""),
        "submission_id": submission.id,
        "is_late": is_late,
    }


# ── 教师：查看某作业的所有提交 ────────────────────────────────────
@router.get("/{assignment_id}/submissions")
def list_submissions(
    assignment_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(404, "作业不存在")
    class_ = db.query(Class).filter(
        Class.id == assignment.class_id,
        Class.teacher_id == current_user.id
    ).first()
    if not class_:
        raise HTTPException(403, "无权限查看")

    submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    return [
        {
            "submission_id": s.id,
            "student_name": s.student.user.username,
            "student_no": s.student.student_no,
            "submitted_at": s.submitted_at,
            "is_late": s.is_late,
            "final_score": s.final_score,
            "status": s.status,
            "file_path": s.file_path,
            "ai_score": s.ai_result.ai_score if s.ai_result else None,
            "ai_comment": s.ai_result.ai_comment if s.ai_result else None,
        }
        for s in submissions
    ]


# ── 教师：修改最终分数 ────────────────────────────────────────────
@router.put("/submissions/{submission_id}/score")
def update_score(
    submission_id: int,
    body: UpdateScoreRequest,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(404, "提交记录不存在")
    if body.final_score < 0:
        raise HTTPException(400, "分数不能为负数")
    submission.final_score = body.final_score
    submission.status = StatusEnum.teacher_reviewed
    db.commit()
    return {"message": "分数已更新"}


# ── 成绩统计：班级平均分和分数分布（给ECharts用）────────────────
@router.get("/{assignment_id}/stats")
def assignment_stats(
    assignment_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.final_score != None
    ).all()

    if not submissions:
        return {"average": 0, "distribution": [], "total": 0, "graded": 0}

    scores = [s.final_score for s in submissions]
    average = round(sum(scores) / len(scores), 1)

    # 分数区间分布（给柱状图用）
    buckets = {"0-59": 0, "60-69": 0, "70-79": 0, "80-89": 0, "90-100": 0}
    for score in scores:
        if score < 60:      buckets["0-59"] += 1
        elif score < 70:    buckets["60-69"] += 1
        elif score < 80:    buckets["70-79"] += 1
        elif score < 90:    buckets["80-89"] += 1
        else:               buckets["90-100"] += 1

    total = db.query(Submission).filter(Submission.assignment_id == assignment_id).count()

    return {
        "average": average,
        "distribution": [{"range": k, "count": v} for k, v in buckets.items()],
        "total": total,
        "graded": len(scores),
    }

# ── 教师：AI批改单个提交 ──────────────────────────────────────────
@router.post("/submissions/{submission_id}/ai-grade")
async def ai_grade_single(
    submission_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(404, "提交记录不存在")

    assignment = submission.assignment
    rule = assignment.rule

    late_score = rule.late_score if rule else int(assignment.max_score * 0.6)



    try:
        print(f"[ai-grade start] submission_id={submission_id} teacher_path={assignment.file_path} student_path={submission.file_path}")
        result = await ai_grade(
            assignment_title=assignment.title,
            assignment_desc=assignment.description or "",
            max_score=assignment.max_score,
            is_late=submission.is_late,
            late_score=late_score,
            teacher_file_path=assignment.file_path or "",   # 教师附件
            student_file_path=submission.file_path or "",   # 学生提交
        )
        print(f"[ai-grade success] submission_id={submission_id} result={result}")
    except Exception as e:
        import traceback
        print(f"[ai-grade error] submission_id={submission_id} error={e}")
        traceback.print_exc()
        raise HTTPException(500, f"AI批改失败：{str(e)}")

    # 保存或更新 AI 批改结果
    ai_result = db.query(AIGradingResult).filter(
        AIGradingResult.submission_id == submission_id
    ).first()

    if ai_result:
        ai_result.ai_score = result["score"]
        ai_result.ai_comment = result["comment"]
        ai_result.model_used = AI_MODEL
    else:
        ai_result = AIGradingResult(
            submission_id=submission_id,
            ai_score=result["score"],
            ai_comment=result["comment"],
            model_used=AI_MODEL,
        )
        db.add(ai_result)

    submission.status = StatusEnum.ai_done
    db.commit()

    return {"score": result["score"], "comment": result["comment"]}


# ── 教师：一键AI批改该作业所有提交 ───────────────────────────────
@router.post("/{assignment_id}/ai-grade-all")
async def ai_grade_all(
    assignment_id: int,
    current_user: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(404, "作业不存在")

    submissions = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).all()

    if not submissions:
        raise HTTPException(404, "该作业暂无提交")

    rule = assignment.rule
    late_score = rule.late_score if rule else int(assignment.max_score * 0.6)

    results = []
    for s in submissions:
        
        try:
            result = await ai_grade(
                assignment_title=assignment.title,
                assignment_desc=assignment.description or "",
                max_score=assignment.max_score,
                is_late=s.is_late,
                late_score=late_score,
                teacher_file_path=assignment.file_path or "",
                student_file_path=s.file_path or "",
            )
            ai_result = db.query(AIGradingResult).filter(
                AIGradingResult.submission_id == s.id
            ).first()
            if ai_result:
                ai_result.ai_score = result["score"]
                ai_result.ai_comment = result["comment"]
                ai_result.model_used = AI_MODEL
            else:
                db.add(AIGradingResult(
                    submission_id=s.id,
                    ai_score=result["score"],
                    ai_comment=result["comment"],
                    model_used=AI_MODEL,
                ))
            s.status = StatusEnum.ai_done
            results.append({"submission_id": s.id, "score": result["score"], "comment": result["comment"]})
        except Exception as e:
            results.append({"submission_id": s.id, "error": str(e)})

    db.commit()
    return {"total": len(submissions), "results": results}