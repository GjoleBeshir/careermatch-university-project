# 5–7 minute oral defense — talking points

## 0:00–0:45: Problem
Students waste time scanning jobs unsuitable for their skills, location or schedule. CareerMatch ranks early-career jobs and internships for a chosen student profile, and explains why.

## 0:45–1:45: Architecture
Browser (HTML/CSS/JS) calls FastAPI REST endpoints and receives JSON. FastAPI queries PostgreSQL with SQLAlchemy. Pydantic validates POST payloads. The scoring module is pure Python. Docker starts PostgreSQL locally. Demonstrate Swagger at `/docs`.

## 1:45–2:35: Dataset and database
Explain synthetic 160 jobs/85 candidates, multiple skills stored as JSON, eight cities, job/candidate tables and optional applications table, `created_at`/`updated_at`/`deleted_at`. Seed reads CSV and cleans numeric, date and list fields, then upserts. Deadline dates generated relative to today's date.

## 2:35–4:05: Algorithm
Draw 35 skills + 15 education + 15 employment/schedule + 15 location/work mode + 10 salary + 10 interests = 100. Explain Haversine for local jobs. Remote jobs don't get a distance penalty. Missing salary receives 5/10; zero skill match gives 0/35, but a job remains eligible. Expired or filled jobs are discarded. The output includes exact factors, score and human-readable reasons. No ML.

## 4:05–5:15: Live demo
Choose another candidate in the dropdown. Show scores change. Filter by category, employment and work mode; clear filters. Show `/jobs?remote_only=true`, `/recommendations/1`, and `POST /jobs` inside Swagger. Display loading and empty filter behavior.

## 5:15–6:15: Testing, tradeoffs, conclusion
Show `python -m pytest -q`. Tests cover API operations and scoring edge cases. Acknowledge simulated data and missing production authentication. The same explainable model can be extended to a real university career service.

## Questions you should be able to answer

**Why not ML?** Deterministic rules are mandatory and more transparent, testable and appropriate for a small synthetic dataset.

**Why JSON arrays?** One candidate can have several skills and interests; JSON makes storage simple for the scope while SQLAlchemy supports it in PostgreSQL. Many-to-many tables would suit large-scale searching.

**What is Haversine?** A spherical Earth distance formula based on two coordinate pairs. Remote roles have no geographic distance.

**Why 35 points for skills?** Technical fit should dominate, but study area, hours, distance and wage must still influence ranking. Weights sum to exactly 100.

**How do API endpoints differ?** `/jobs` returns filterable records, `/recommendations/{id}` ranks for a stored candidate, and `/recommendations?lat&lon&skills` builds a temporary profile using documented defaults.

**How are deadlines handled?** Jobs with deadlines before today are excluded; filled positions are excluded. Synthetic data is refreshed with future deadlines every time you seed.

**What are the limitations?** Fictional data, no login, no real job applications workflow, no migrations and no production security guarantees.
