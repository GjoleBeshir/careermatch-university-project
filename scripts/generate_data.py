"""Deterministic, fictional datasets. Deadlines refresh relative to execution date."""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
CATEGORIES = {
    "Software Development": ["Python", "JavaScript", "SQL", "Git", "Java", "React", "FastAPI"],
    "Data Analytics": ["Python", "SQL", "Excel", "Power BI", "Statistics", "Tableau"],
    "Marketing": ["Social Media", "SEO", "Excel", "Copywriting", "Communication"],
    "Business": ["Excel", "Communication", "Research", "Presentation", "CRM"],
    "Design": ["Figma", "Adobe Illustrator", "Photoshop", "UX Research", "Prototyping"],
    "Finance": ["Excel", "Accounting", "Financial Analysis", "Power BI", "Budgeting"],
    "Human Resources": ["Communication", "Recruiting", "Excel", "Interviewing", "Organization"],
    "Customer Support": ["Communication", "CRM", "English", "Problem Solving", "Excel"],
    "Engineering": ["AutoCAD", "SolidWorks", "MATLAB", "Technical Drawing", "Problem Solving"],
    "Project Management": ["Agile", "Trello", "Excel", "Communication", "Planning"],
    "Sales": ["CRM", "Negotiation", "Communication", "Excel", "Presentation"],
    "Research": ["Research", "Statistics", "Python", "Writing", "Data Collection"],
}
AREA = {"Software Development": "Computer Science", "Data Analytics": "Computer Science", "Marketing": "Marketing",
        "Business": "Economics", "Design": "Design", "Finance": "Economics", "Human Resources": "Business",
        "Customer Support": "All Graduates", "Engineering": "Engineering", "Project Management": "Business",
        "Sales": "All Graduates", "Research": "All Graduates"}
LOCATIONS = [("Skopje", 41.9981, 21.4254), ("Ohrid", 41.1172, 20.8016), ("Bitola", 41.0314, 21.3347),
             ("Tetovo", 42.0097, 20.9716), ("Prilep", 41.3451, 21.5550), ("Struga", 41.1775, 20.6788),
             ("Kumanovo", 42.1322, 21.7144), ("Shtip", 41.7464, 22.1997)]
EMPLOYERS = ["NovaBridge Labs", "PixelPath Studio", "BlueLake Systems", "OrbitWorks", "Summit Partners",
             "BrightCurrent", "Northstar Digital", "Verde Solutions", "Catalyst Group", "Astra Research",
             "Mosaic Dynamics", "Futura Works", "Lumen Technologies", "VectorPoint", "Meridian Office"]
NAMES = ["Ana", "Marko", "Elena", "Stefan", "Mila", "Petar", "Ivana", "Filip", "Sara", "Nikola", "Jovana", "Martin", "Teodora", "David", "Marija", "Luka", "Ema"]
SURNAMES = ["Petrova", "Ivanov", "Stojanova", "Trajkov", "Nikolova", "Angelov", "Risteska", "Popov", "Kostova", "Mitev"]

def write_csv(path, columns, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)

def generate(jobs_count=160, candidates_count=85):
    rng = random.Random(20261114)
    jobs, candidates = [], []
    cats = list(CATEGORIES)
    types = ["Internship", "Full-time", "Part-time"]
    for i in range(1, jobs_count + 1):
        cat = cats[(i - 1) % len(cats)]
        jobtype = types[((i - 1) // len(cats)) % 3]
        city, lat, lon = LOCATIONS[(i - 1) % len(LOCATIONS)]
        mode = ["On-site", "Hybrid", "Remote"][(i + i // 7) % 3]
        skill_set = rng.sample(CATEGORIES[cat], k=min(3, len(CATEGORIES[cat])))
        title = {"Internship": "Intern", "Part-time": "Assistant", "Full-time": "Junior Specialist"}[jobtype]
        start, end = {"Internship": ("09:00", "15:00"), "Full-time": ("09:00", "17:00"), "Part-time": ("10:00", "14:00")}[jobtype]
        salary = {"Internship": 18000, "Part-time": 22000, "Full-time": 38000}[jobtype] + rng.randrange(0, 8) * 2500
        vacancies = rng.randint(1, 6)
        jobs.append(dict(job_id=i, title=f"{cat} {title}", description=f"Early-career {cat.lower()} opportunity involving {', '.join(skill_set)}. Learn with a supportive team.",
            category=cat, employer=EMPLOYERS[(i - 1) % len(EMPLOYERS)], location_name=city, latitude=lat + rng.uniform(-0.025, 0.025),
            longitude=lon + rng.uniform(-0.025, 0.025), employment_type=jobtype, work_mode=mode,
            required_skills=", ".join(skill_set), target_audience=AREA[cat] if i % 5 else "All Graduates",
            salary_min="" if i % 14 == 0 else salary, salary_max="" if i % 14 == 0 else salary + 9000,
            application_deadline=(date.today() + timedelta(days=10 + i % 130)).isoformat(), vacancies=vacancies,
            filled_positions=vacancies if i % 17 == 0 else rng.randint(0, vacancies - 1), schedule_start=start, schedule_end=end))
    for i in range(1, candidates_count + 1):
        cat = cats[(i - 1) % len(cats)]
        city, lat, lon = LOCATIONS[(i - 1) % len(LOCATIONS)]
        skills = rng.sample(CATEGORIES[cat], k=min(4, len(CATEGORIES[cat])))
        interests = [cat, cats[(i + 2) % len(cats)]]
        name = f"{NAMES[(i - 1) % len(NAMES)]} {SURNAMES[(i - 1) % len(SURNAMES)]}"
        candidates.append(dict(candidate_id=i, name=name, email=f"student{i:03d}@example.test", study_area=AREA[cat] if AREA[cat] != "All Graduates" else "Business",
            year_of_study=(i % 4) + 1, latitude=lat + rng.uniform(-0.04, 0.04), longitude=lon + rng.uniform(-0.04, 0.04),
            skills=", ".join(skills), interests=", ".join(interests),
            preferred_employment_type=types[(i - 1) % 3], preferred_work_mode=["Hybrid", "Remote", "On-site"][(i - 1) % 3],
            available_from="09:00", available_to="17:00", min_salary=15000 + (i % 12) * 2500))
    write_csv(OUT / "raw" / "jobs.csv", list(jobs[0]), jobs)
    write_csv(OUT / "candidates.csv", list(candidates[0]), candidates)
    return len(jobs), len(candidates)

if __name__ == "__main__":
    print("Created fictional records:", generate())
