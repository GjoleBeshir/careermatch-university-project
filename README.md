> **NEW — public browser preview:** See [Render deployment instructions](docs/RENDER_DEPLOYMENT.md) and the root `render.yaml`. A public URL requires you to connect your own GitHub/Render account; this ZIP is deployment-ready but is not yet deployed.

# CareerMatch — Job & Internship Recommendation System

![Stack](https://img.shields.io/badge/Python-FastAPI-285b47) ![Database](https://img.shields.io/badge/Database-PostgreSQL-336791) ![Scoring](https://img.shields.io/badge/Matching-Explainable-8baa71)

A complete **Solution 2** student project: deterministic, explainable matching of students to internships, part-time jobs and entry-level roles. Built with **FastAPI, SQLAlchemy, PostgreSQL, HTML, CSS and vanilla JavaScript**. No machine learning, external jobs API, or login required.

## Quick start (Windows / macOS / Linux)

**Prerequisites:** Python 3.11+, Docker Desktop (with Docker Compose), and a terminal. Docker Desktop must be started.

```bash
# 1. From the extracted CareerMatch folder
cp .env.example .env        # Windows PowerShell: Copy-Item .env.example .env
# 2. Launch PostgreSQL
 docker compose up -d
# 3. Create and activate Python virtual environment (or use uv instead)
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# 4. Populate database (refreshes synthetic CSV deadlines)
python -m scripts.wait_for_db
python -m scripts.seed
# 5. Start API and frontend
python -m uvicorn app.main:app --reload
```

**Open:** http://127.0.0.1:8000/ for the web application; http://127.0.0.1:8000/docs for interactive Swagger API docs. To stop, press Ctrl+C; optionally `docker compose down` (retains database data).

**uv alternative:** `uv sync --extra test`, then `uv run python -m scripts.seed` and `uv run uvicorn app.main:app --reload`.

**Important:** `localhost:5432` must be available, and the credentials in `.env` must match `docker-compose.yml`. If you already use PostgreSQL on port 5432, change the host port in `docker-compose.yml` and `.env` together. The seed operation is idempotent and safe to repeat; it refreshes example rows with the same IDs.

### Tests

```bash
python -m pytest -q
```

Tests use a temporary isolated SQLite DB for portability, override the FastAPI session dependency, run the real CSV parser, and exercise actual API routes. The **delivered runtime database remains PostgreSQL**. Verify PostgreSQL with the Docker-based quick start, too.

## What is included

- 160 synthetic jobs and 85 synthetic candidates, generated reproducibly with realistic fields and fresh future deadlines
- 12 job categories; fictional companies and student profiles; multiple skills/interests; eight North Macedonian cities
- PostgreSQL tables `jobs`, `candidates`, `job_applications` with timestamps and soft-delete support
- CSV validation/normalization + idempotent seed; JSON lists for skills and interests
- Eight required FastAPI routes, combinable `GET /jobs` filters, and `GET /health`
- Deterministic 0–100 scoring with documented weights, Haversine distance and itemized score breakdown
- Responsive single-page dashboard with candidate selection, three filters, loading/error/empty states, reasons, salary and deadlines
- Automated tests, scoring explanation, ER diagram, API samples, and an oral-defense script

## Required endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/jobs` | All jobs; filters: `category`, `employment_type`, `remote_only` |
| GET | `/jobs/{job_id}` | Single job |
| POST | `/jobs` | Add job (JSON) |
| GET | `/candidates` | List candidates |
| GET | `/candidates/{candidate_id}` | Candidate details |
| POST | `/candidates` | Add candidate (JSON) |
| GET | `/recommendations/{candidate_id}` | Personalized ranked jobs |
| GET | `/recommendations?lat=...&lon=...&skills=...` | Ad hoc matching by coordinates and skills |

Try:

```bash
curl "http://127.0.0.1:8000/jobs?category=Software%20Development&employment_type=Internship&remote_only=true"
curl "http://127.0.0.1:8000/recommendations/1"
curl "http://127.0.0.1:8000/recommendations?lat=41.9981&lon=21.4254&skills=Python,SQL"
```

`GET /recommendations` (ad hoc) uses `Internship`, `Hybrid`, availability 09:00–17:00, expected monthly minimum salary of **20,000 MKD**, and unknown study area by default. Optionally use `category=...`. It is not a stored profile.

## Algorithm overview

Eligible jobs must be active, not expired, and have vacancies left. A normalized weighted score is rounded to an integer:

| Factor | Maximum points |
|---|---:|
| Required skills matched | 35 |
| Education / audience | 15 |
| Employment type & working hours | 15 |
| Distance & work mode | 15 |
| Salary compatibility | 10 |
| Category interests | 10 |
| **Total** | **100** |

For complete formulas and special cases, see [docs/TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md). The server returns human-readable reasons and numeric breakdown per job. Salary values are **monthly MKD**. No machine learning.

## Structure

```text
CareerMatch/
├── app/                    FastAPI, models, schemas, scoring, DB
├── data/raw/jobs.csv       160 fictional jobs
├── data/candidates.csv     85 fictional candidates
├── scripts/generate_data.py
├── scripts/seed.py         Validate CSV and upsert
├── frontend/               HTML + CSS + vanilla JS
├── tests/                  Unit + route integration tests
├── docs/                   Technical report and presentation notes
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── pyproject.toml
```

## Academic submission notes

- **This dataset is entirely fictional**; do not represent these listings as verified live openings.
- The brief requests documentation using the exact **I am NEXT → Lesson → Week07** template. That template was **not provided**. The supplied technical report covers the content, but transfer it into the official template before submission.
- Create your own GitHub repository and push this project; `.env` is ignored. Do not push secrets.
- The brief allocates **60 implementation + 20 oral points**, with a minimum **10/20** on the individual oral defense. Review the architecture, scoring and code so you can explain it personally.
- For real use, replace demo credentials and add authentication, migrations, access controls and more robust validation. Authentication is intentionally omitted because the brief does not require it.

## QA update — 14 November 2026

See `docs/QA_REPORT.md`, `docs/LIVE_QA_RESULTS.json`, and `docs/UNIT_TEST_RESULTS.txt` for executed checks and limitations.
Cards now include **View details** with full description, requirements,
working hours and six-factor score breakdown. Close with the button or Escape.
Each category includes all three employment types in the synthetic dataset.
Seed synchronizes PostgreSQL ID sequences so POST endpoints work after import.
The health route checks database connectivity and returns 503 when unavailable.
Startup scripts wait for database readiness before seeding.

To repeat live checks on a **disposable local demo database**, start the app
on port 8765 (`python -m uvicorn app.main:app --port 8765`), then run
`python -m scripts.live_qa` in another terminal with the same DATABASE_URL.
The script expects exactly 160 jobs and 85 candidates and creates and removes
its own temporary QA job/candidate. Its default URL is loopback only.
