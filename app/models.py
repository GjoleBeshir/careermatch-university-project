"""Relational schema; list-valued attributes use portable SQLAlchemy JSON columns."""
from datetime import datetime, date, time, timezone
from sqlalchemy import String, Integer, Float, Date, Time, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def utc_now():
    return datetime.now(timezone.utc)

class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Candidate(AuditMixin, Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    study_area: Mapped[str] = mapped_column(String(100), nullable=False)
    year_of_study: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    interests: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    preferred_employment_type: Mapped[str] = mapped_column(String(40), nullable=False)
    preferred_work_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    available_from: Mapped[time] = mapped_column(Time, nullable=False)
    available_to: Mapped[time] = mapped_column(Time, nullable=False)
    min_salary: Mapped[int] = mapped_column(Integer, nullable=False)

class Job(AuditMixin, Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(90), index=True, nullable=False)
    employer: Mapped[str] = mapped_column(String(150), nullable=False)
    location_name: Mapped[str] = mapped_column(String(120), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    employment_type: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    work_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    required_skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    target_audience: Mapped[str] = mapped_column(String(100), nullable=False)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    application_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    vacancies: Mapped[int] = mapped_column(Integer, nullable=False)
    filled_positions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    schedule_start: Mapped[time] = mapped_column(Time, nullable=False)
    schedule_end: Mapped[time] = mapped_column(Time, nullable=False)

class JobApplication(AuditMixin, Base):
    __tablename__ = "job_applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    application_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    status: Mapped[str] = mapped_column(String(20), default="submitted")
