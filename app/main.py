"""REST API plus static frontend served at /; Swagger documentation at /docs."""
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Candidate, Job
from .schemas import CandidateCreate, CandidateRead, JobCreate, JobRead
from .recommender import rank_jobs

ROOT = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="CareerMatch API", version="1.0.0", description="Deterministic internship and job matching", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(ROOT / "frontend")), name="static")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(ROOT / "frontend" / "index.html")

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(503, "Database unavailable")
    return {"status": "ok"}

@app.get("/jobs", response_model=list[JobRead])
def get_jobs(category: str | None = None, employment_type: str | None = None, remote_only: bool = False,
             limit: int = Query(default=250, ge=1, le=500), db: Session = Depends(get_db)):
    query = select(Job).where(Job.deleted_at.is_(None))
    if category: query = query.where(Job.category.ilike(category.strip()))
    if employment_type: query = query.where(Job.employment_type.ilike(employment_type.strip()))
    if remote_only: query = query.where(Job.work_mode.ilike("Remote"))
    return db.scalars(query.order_by(Job.id).limit(limit)).all()

@app.get("/jobs/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None or job.deleted_at is not None:
        raise HTTPException(404, "Job not found")
    return job

@app.post("/jobs", response_model=JobRead, status_code=201)
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    job = Job(**data.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@app.get("/candidates", response_model=list[CandidateRead])
def get_candidates(db: Session = Depends(get_db)):
    return db.scalars(select(Candidate).where(Candidate.deleted_at.is_(None)).order_by(Candidate.id)).all()

@app.get("/candidates/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if candidate is None or candidate.deleted_at is not None:
        raise HTTPException(404, "Candidate not found")
    return candidate

@app.post("/candidates", response_model=CandidateRead, status_code=201)
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db)):
    candidate = Candidate(**data.model_dump())
    db.add(candidate)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Candidate email already exists")
    db.refresh(candidate)
    return candidate

@app.get("/recommendations/{candidate_id}")
def candidate_recommendations(candidate_id: int, limit: int = Query(40, ge=1, le=200), db: Session = Depends(get_db)):
    candidate = db.get(Candidate, candidate_id)
    if candidate is None or candidate.deleted_at is not None:
        raise HTTPException(404, "Candidate not found")
    jobs = db.scalars(select(Job).where(Job.deleted_at.is_(None))).all()
    recommendations = rank_jobs(candidate, jobs)
    return {"candidate_id": candidate.id, "candidate_name": candidate.name,
            "total_matches": len(recommendations), "recommendations": recommendations[:limit]}

@app.get("/recommendations")
def location_recommendations(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180),
                             skills: str = "", category: str | None = None, limit: int = Query(40, ge=1, le=200),
                             db: Session = Depends(get_db)):
    """Ad-hoc candidate defaults documented so the endpoint is deterministic."""
    from datetime import time
    from types import SimpleNamespace
    candidate = SimpleNamespace(study_area="Any", skills=[s.strip() for s in skills.split(",") if s.strip()],
        interests=[category] if category else [], preferred_employment_type="Internship",
        preferred_work_mode="Hybrid", latitude=lat, longitude=lon,
        available_from=time(9, 0), available_to=time(17, 0), min_salary=20000)
    query = select(Job).where(Job.deleted_at.is_(None))
    if category: query = query.where(Job.category.ilike(category.strip()))
    matches = rank_jobs(candidate, db.scalars(query).all())
    return {"query": {"lat": lat, "lon": lon, "skills": candidate.skills, "category": category},
            "total_matches": len(matches), "recommendations": matches[:limit]}
