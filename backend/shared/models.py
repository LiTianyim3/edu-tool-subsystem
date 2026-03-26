from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class RoleEnum(str, enum.Enum):
    teacher = "teacher"
    student = "student"


class StatusEnum(str, enum.Enum):
    pending = "pending"
    ai_grading = "ai_grading"
    ai_done = "ai_done"
    teacher_reviewed = "teacher_reviewed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    classes = relationship("Class", back_populates="teacher")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    code = Column(String(32), unique=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="classes")
    students = relationship("StudentProfile", back_populates="class_")
    assignments = relationship("Assignment", back_populates="class_")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    student_no = Column(String(32), nullable=False)

    user = relationship("User", back_populates="student_profile")
    class_ = relationship("Class", back_populates="students")
    submissions = relationship("Submission", back_populates="student")


class GradingRule(Base):
    __tablename__ = "grading_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    max_score = Column(Integer, nullable=False, default=100)
    late_score = Column(Integer, nullable=False)
    quality_tiers = Column(JSON, nullable=False, default=list)
    prompt_template = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignments = relationship("Assignment", back_populates="rule")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("grading_rules.id"), nullable=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=False)
    max_score = Column(Integer, nullable=False, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

    class_ = relationship("Class", back_populates="assignments")
    rule = relationship("GradingRule", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")
    file_path = Column(String(512), nullable=True)


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    file_path = Column(String(512), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    is_late = Column(Boolean, default=False)
    final_score = Column(Integer, nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.pending)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("StudentProfile", back_populates="submissions")
    ai_result = relationship("AIGradingResult", back_populates="submission", uselist=False)


class AIGradingResult(Base):
    __tablename__ = "ai_grading_results"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False, unique=True)
    ai_score = Column(Integer, nullable=True)
    ai_comment = Column(Text, nullable=True)
    model_used = Column(String(64), nullable=True)
    graded_at = Column(DateTime, default=datetime.utcnow)

    submission = relationship("Submission", back_populates="ai_result")
