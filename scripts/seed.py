"""Validate CSV and upsert into PostgreSQL (idempotent)."""
import csv
from pathlib import Path
from datetime import date, time
from sqlalchemy import select, text
from app.database import Base, engine, SessionLocal
from app.models import Candidate, Job
from app.schemas import CandidateCreate, JobCreate
from scripts.generate_data import generate

ROOT = Path(__file__).resolve().parent.parent

def clean_list(value):
    return list(dict.fromkeys(s.strip() for s in (value or "").split(",") if s.strip()))

def maybe_int(value):
    return None if value is None or str(value).strip() == "" else int(value)

def load_jobs(db):
    with (ROOT / "data" / "raw" / "jobs.csv").open(newline="", encoding="utf-8") as f:
        for record in csv.DictReader(f):
            pk = int(record.pop("job_id"))
            record["required_skills"] = clean_list(record["required_skills"])
            for key in ("salary_min", "salary_max"): record[key] = maybe_int(record[key])
            for key in ("vacancies", "filled_positions"): record[key] = int(record[key])
            for key in ("latitude", "longitude"): record[key] = float(record[key])
            record["application_deadline"] = date.fromisoformat(record["application_deadline"])
            for key in ("schedule_start", "schedule_end"): record[key] = time.fromisoformat(record[key])
            data = JobCreate.model_validate(record).model_dump()
            obj = db.get(Job, pk)
            if obj:
                for field, value in data.items(): setattr(obj, field, value)
            else: db.add(Job(id=pk, **data))
    db.commit()

def load_candidates(db):
    with (ROOT / "data" / "candidates.csv").open(newline="", encoding="utf-8") as f:
        for record in csv.DictReader(f):
            pk = int(record.pop("candidate_id"))
            for key in ("skills", "interests"): record[key] = clean_list(record[key])
            for key in ("latitude", "longitude"): record[key] = float(record[key])
            for key in ("year_of_study", "min_salary"): record[key] = int(record[key])
            for key in ("available_from", "available_to"): record[key] = time.fromisoformat(record[key])
            data = CandidateCreate.model_validate(record).model_dump()
            obj = db.get(Candidate, pk)
            if obj:
                for field, value in data.items(): setattr(obj, field, value)
            else: db.add(Candidate(id=pk, **data))
    db.commit()

def main():
    # Refresh the synthetic CSV deadlines whenever seeding so ads do not age out.
    generate()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        load_jobs(db)
        load_candidates(db)
        # Explicit CSV primary keys do not advance PostgreSQL SERIAL sequences.
        if engine.dialect.name == "postgresql":
            for table in ("jobs", "candidates"):
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1), true)"))
            db.commit()
        print("Seeded 160 jobs and 85 candidates. You can re-run this safely.")

if __name__ == "__main__":
    main()
