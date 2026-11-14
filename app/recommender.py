"""Pure deterministic scoring (0–100) with documented factor weights."""
from datetime import date, datetime, time
from math import radians, cos, sin, asin, sqrt

WEIGHTS = {"skills": 35, "education": 15, "employment_schedule": 15, "location_mode": 15, "salary": 10, "interest": 10}

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between coordinate pairs on Earth."""
    r = 6371.0088
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return 2 * r * asin(min(1, sqrt(a)))

def normalize(values):
    return {str(value).strip().casefold() for value in (values or []) if str(value).strip()}

def overlap_hours(a_start: time, a_end: time, b_start: time, b_end: time):
    def minute(t): return t.hour * 60 + t.minute
    covered = max(0, min(minute(a_end), minute(b_end)) - max(minute(a_start), minute(b_start)))
    required = max(1, minute(b_end) - minute(b_start))
    return min(1.0, covered / required)

def score_job(candidate, job, today=None):
    """Return None if ineligible; otherwise a explainable recommendation dictionary.

    Hard exclusion: expired, no positions, or soft-deleted jobs.
    Soft factors: missing salary = neutral 0.5; zero matching skills = 0 skill points.
    Work mode is evaluated separately from physical distance; remote work has no distance cost.
    """
    today = today or date.today()
    if job.deleted_at is not None or job.application_deadline < today or job.vacancies <= job.filled_positions:
        return None
    offered = normalize(job.required_skills)
    owned = normalize(candidate.skills)
    matching = sorted(offered & owned)
    skills = len(matching) / len(offered) if offered else 1.0
    area = candidate.study_area.strip().casefold()
    audience = job.target_audience.strip().casefold()
    education = 1.0 if audience in ("all graduates", "all students", "all applicants", "any") or audience == area else 0.0
    # Graduates (year 0) are eligible for all-graduate jobs, otherwise year is not a hard filter.
    emp = 1.0 if candidate.preferred_employment_type.casefold() == job.employment_type.casefold() else 0.3
    schedule = overlap_hours(candidate.available_from, candidate.available_to, job.schedule_start, job.schedule_end)
    employment_schedule = 0.6 * emp + 0.4 * schedule
    distance = None if job.work_mode.casefold() == "remote" else round(haversine_km(candidate.latitude, candidate.longitude, job.latitude, job.longitude), 2)
    preference = candidate.preferred_work_mode.casefold()
    mode = job.work_mode.casefold()
    if mode == "remote":
        location_mode = 1.0 if preference in ("remote", "hybrid") else 0.65
    else:
        distance_fit = 1.0 if distance <= 10 else (0.7 if distance <= 30 else (0.3 if distance <= 80 else 0.0))
        mode_fit = 1.0 if mode == preference else (0.7 if "hybrid" in (mode, preference) else 0.35)
        location_mode = 0.5 * distance_fit + 0.5 * mode_fit
    if job.salary_max is None:
        salary = 0.5
    elif job.salary_max >= candidate.min_salary:
        salary = 1.0
    else:
        salary = max(0.0, job.salary_max / max(1, candidate.min_salary)) * 0.4
    interest = 1.0 if job.category.strip().casefold() in normalize(candidate.interests) else 0.0
    ratios = {"skills": skills, "education": education, "employment_schedule": employment_schedule,
              "location_mode": location_mode, "salary": salary, "interest": interest}
    breakdown = {key: round(WEIGHTS[key] * value, 2) for key, value in ratios.items()}
    total = min(100, max(0, round(sum(breakdown.values()))))
    reason_parts = []
    if matching: reason_parts.append("Matches " + ", ".join(matching[:4]) + " skills")
    else: reason_parts.append("No direct required-skill overlap")
    if education: reason_parts.append("fits your study area")
    if mode == "remote": reason_parts.append("offers remote work")
    elif distance is not None: reason_parts.append(f"is {distance:g} km away")
    if job.salary_max is None: reason_parts.append("salary not specified")
    elif job.salary_max >= candidate.min_salary: reason_parts.append("meets your minimum salary")
    else: reason_parts.append("salary below your expectation")
    return {
        "job_id": job.id, "title": job.title, "category": job.category, "employer": job.employer,
        "employment_type": job.employment_type, "work_mode": job.work_mode,
        "location_name": job.location_name, "distance_km": distance,
        "salary_min": job.salary_min, "salary_max": job.salary_max,
        "application_deadline": job.application_deadline.isoformat(),
        "available_positions": job.vacancies - job.filled_positions,
        "score": total, "score_breakdown": breakdown, "matched_skills": matching,
        "reason": "; ".join(reason_parts).capitalize() + "."
    }

def rank_jobs(candidate, jobs, today=None):
    items = [result for job in jobs if (result := score_job(candidate, job, today)) is not None]
    return sorted(items, key=lambda rec: (-rec["score"], rec["job_id"]))
