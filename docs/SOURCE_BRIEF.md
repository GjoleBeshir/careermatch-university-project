# Job and Internship Recommendation System — Student Project Brief

### Subject: Implementation of Solution 2

## 1. Project Overview

The goal of this project is to build a simple recommendation system that suggests relevant jobs and internships to students and recent graduates.

The system should recommend opportunities such as internships, entry-level positions, part-time jobs, graduate programs, and remote positions.

Recommendations should be based on:

- candidate skills and interests
- education or study area
- year of study or graduation status
- job category and required skills
- employment type and schedule
- job location and distance from the candidate
- remote or hybrid availability
- salary expectations
- application deadline and open vacancies

## 2. Business Context

The system is designed for a university career center, recruitment agency, or early-career job platform that wants to connect students and recent graduates with suitable opportunities.

Candidates often struggle to identify relevant openings among many listings. This system collects job advertisements in one place and ranks them according to candidate preferences and job requirements.

The final application can be imagined as:

- a webview inside a university career portal
- a simple recruitment platform feature
- a recommendation widget for a job board

## 3. Main Objective

Build a working **FastAPI** backend, **PostgreSQL** database, and simple frontend that displays recommended job and internship opportunities for a selected candidate.

The system must use **deterministic logic**. Do not use machine learning models. The recommendation score should be based on clear rules that can be explained in the documentation.

## 4. Required Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- psycopg2-binary
- python-dotenv

### Database

- PostgreSQL
- Docker or local PostgreSQL installation

### Frontend

- HTML
- CSS
- JavaScript

### Utilities

- uv for Python environment management
- CSV or TSV files for initial data
- Optional: requests for testing API calls

## 5. Required Features

### Data processing

You must prepare or generate a dataset of job opportunities and candidate profiles.

The system should:

- read job opportunities from a CSV or TSV file
- clean and validate the data
- insert jobs into PostgreSQL
- generate or import sample candidate profiles

### Database design

You must design database tables for:

- candidates
- jobs
- optional job applications or saved jobs

Every new database table should include:

- `created_at`
- `updated_at`
- `deleted_at`

### Backend API

You must build REST API endpoints using FastAPI.

Required endpoints:

- `GET /jobs`
- `GET /candidates`
- `GET /candidates/{candidate_id}`
- `GET /recommendations/{candidate_id}`
- `POST /candidates`
- `POST /jobs`
- `GET /recommendations?lat=...&lon=...&skills=...`
- `GET /jobs/{job_id}`

Required job filtering functionality:

- filter jobs by category
- filter jobs by employment type (internship, full-time, part-time)
- filter jobs to show remote opportunities only

You should implement these filters using query parameters on the `GET /jobs` endpoint. The filters should also be available from the frontend. Multiple filters should be able to work together when appropriate.

Example requests:

```text
GET /jobs?category=Software Development
GET /jobs?employment_type=Internship
GET /jobs?remote_only=true
GET /jobs?category=Software Development&employment_type=Internship&remote_only=true
```

### Recommendation logic

You must implement a scoring system that ranks jobs for a candidate.

The score should include:

- skills match
- education or target audience match
- employment type and schedule match
- distance score or remote-work compatibility
- salary compatibility
- vacancy availability and application deadline

### Frontend

You must build a simple frontend page that:

- loads recommendation data from the backend
- displays job cards
- shows job title, category, employer, employment type, location, distance or remote status, salary, deadline, and score
- handles loading, error, and empty states
- works well on mobile screen sizes

## 6. Suggested Dataset

You must prepare the datasets required by the system.

For the **jobs dataset**, you may create or generate your own synthetic dataset. It may be prepared manually, generated with a Python script, or inspired by publicly available job listings. It does not need to come from a live API. Use fictional employer and candidate data where appropriate.

For the **candidates dataset**, you must create or generate synthetic candidate profiles.

Recommended minimum dataset size:

- **100 to 200 jobs**
- **70 to 100 candidates**

The `skills` and `interests` fields in the candidate dataset must support **multiple values for each candidate**, not only one value. The `required_skills` field in the jobs dataset should also support multiple skills.

### Jobs CSV structure

Example file: `data/raw/jobs.csv`

```csv
job_id,title,description,category,employer,location_name,latitude,longitude,employment_type,work_mode,required_skills,target_audience,salary_min,salary_max,application_deadline,vacancies,filled_positions
1,Junior Python Developer,Build backend APIs,Software Development,TechNova,Skopje,41.9981,21.4254,Full-time,Hybrid,"Python,SQL,Git",Computer Science,45000,65000,2027-05-20,3,1
2,Marketing Intern,Assist with digital campaigns,Marketing,MarketLab,Skopje,41.9990,21.4261,Internship,On-site,"Social Media,Communication,Excel",All Graduates,15000,22000,2027-05-25,4,0
3,Data Analyst Intern,Analyze business data,Data Analytics,DataBridge,Skopje,41.9975,21.4248,Internship,Remote,"Python,Excel,SQL",Computer Science,20000,30000,2027-06-01,2,0
```

Dates are illustrative. The application should use future deadlines relative to the date it is run.

### Candidates CSV structure

Example file: `data/candidates.csv`

```csv
candidate_id,name,email,study_area,year_of_study,latitude,longitude,skills,interests,preferred_employment_type,preferred_work_mode,available_from,available_to,min_salary
1,Ana Petrova,ana.pet@example.com,Computer Science,3,41.9980,21.4250,"Python,SQL,Git","Software Development,Data Analytics",Internship,Hybrid,09:00,17:00,20000
2,Marko Ivanov,marko@example.com,Economics,4,41.9992,21.4262,"Excel,Communication,Social Media","Marketing,Business",Internship,On-site,09:00,16:00,15000
3,Elena Stojanova,elena@example.com,Computer Science,2,41.9976,21.4249,"Python,Excel,SQL","Data Analytics,Software Development",Internship,Remote,10:00,18:00,18000
```

### Suggested job categories

- Software Development
- Data Analytics
- Marketing
- Business
- Design
- Finance
- Human Resources
- Customer Support
- Engineering
- Project Management
- Sales
- Research

### Suggested locations

You may use fictional employers and offices around Skopje or another city. Include on-site, hybrid, and remote opportunities.

## 7. Suggested Database Schema

### `candidates` table

Required fields:

- `id`
- `name`
- `email`
- `study_area`
- `year_of_study`
- `latitude`
- `longitude`
- `skills`
- `interests`
- `preferred_employment_type`
- `preferred_work_mode`
- `available_from`
- `available_to`
- `min_salary`
- `created_at`
- `updated_at`
- `deleted_at`

The `skills` and `interests` fields must support multiple values. They can be stored as comma-separated strings, JSON fields, or separate many-to-many tables.

### `jobs` table

Required fields:

- `id`
- `title`
- `description`
- `category`
- `employer`
- `location_name`
- `latitude`
- `longitude`
- `employment_type`
- `work_mode`
- `required_skills`
- `target_audience`
- `salary_min`
- `salary_max`
- `application_deadline`
- `vacancies`
- `filled_positions`
- `created_at`
- `updated_at`
- `deleted_at`

### Optional `job_applications` table

Suggested fields:

- `id`
- `candidate_id`
- `job_id`
- `application_datetime`
- `status`
- `created_at`
- `updated_at`
- `deleted_at`

## 8. Recommendation Logic

The recommendation system must be **explainable and deterministic**.

You must design and implement your own scoring approach for ranking jobs for a candidate. The brief intentionally does not prescribe point values, weights, thresholds, or a fixed score distribution. You are expected to decide how the relevant factors should contribute to the final recommendation score and justify your decisions in the project documentation.

The scoring logic must consider the following features:

- **Skills match** — how many of the required skills match the candidate's skills; jobs may require multiple skills.
- **Education or audience match** — whether the opportunity targets the candidate's study area or is open to all applicants.
- **Employment type and schedule** — whether the employment type and expected working hours fit the candidate's preferences and availability. For simplicity, define a consistent expected schedule for each employment type or add a schedule field to the dataset.
- **Distance / work mode** — use the Haversine formula to calculate distance for on-site or hybrid opportunities and handle fully remote opportunities appropriately.
- **Salary compatibility** — whether the advertised salary range meets the candidate's minimum expected salary. Treat all salaries in the same currency and time period.
- **Vacancy availability / deadline** — whether vacancies remain and the application deadline has not passed.

You must calculate a final recommendation score for each eligible job and sort the jobs from the highest score to the lowest score. Define and document how expired listings, filled vacancies, missing salary values, remote jobs, and candidates without matching skills are handled. The exact scoring formula, weights, thresholds, and treatment of special cases are part of your design decisions and must be clearly explained in the documentation.

## 9. Required API Response Example

Endpoint:

```text
GET /recommendations/1
```

Example response:

```json
{
  "candidate_id": 1,
  "candidate_name": "Ana Petrova",
  "recommendations": [
    {
      "job_id": 1,
      "title": "Junior Python Developer",
      "category": "Software Development",
      "employer": "TechNova",
      "employment_type": "Full-time",
      "work_mode": "Hybrid",
      "location_name": "Skopje",
      "distance_km": 0.14,
      "salary_min": 45000,
      "salary_max": 65000,
      "application_deadline": "2027-05-20",
      "available_positions": 2,
      "score": 92,
      "reason": "Matches your Python, SQL and Git skills, is close to your location, and meets your salary expectation."
    }
  ]
}
```

The example score is illustrative, not a prescribed formula.

## 10. Frontend Requirements

The frontend should be simple but complete.

Each recommendation card should show:

- job title
- category
- employer
- employment type and work mode
- location
- distance (when applicable)
- salary range
- application deadline
- available positions
- recommendation score
- short reason for the recommendation

The frontend should include:

- loading state
- error state
- empty recommendations state
- candidate selector or query parameter support
- controls for the required job filters

Example webview URL:

```text
frontend/index.html?candidate_id=1
```

## 11. Technical Documentation

You must prepare **technical documentation** for the final project.

The template for the technical documentation is attached on the **I am NEXT** platform, under Lesson → Week07. You must use the provided template when preparing and submitting your technical documentation.

## 12. Optional Extensions

You may extend the project with additional features or functionality based on your own ideas. Any optional extension should be relevant to the project and should not replace the required functionality described in this brief.

## 13. Grading

The project is graded with a maximum of **80 points**.

- **60 points** are awarded for the project implementation.
- **20 points** are awarded for the individual oral presentation and questions about the project implementation.

### Project implementation — 60 points

| Requirement | Points |
|---|---:|
| Data preparation and processing | 6 |
| Database design and PostgreSQL integration | 7 |
| FastAPI backend, required endpoints, and job filtering | 13 |
| Recommendation logic and scoring | 14 |
| Frontend implementation and backend integration | 10 |
| Technical documentation and GitHub repository | 10 |
| **Total** | **60** |

The implementation will be evaluated based on whether the required functionality works correctly, whether the different components are properly integrated, and whether the implementation follows the requirements defined in this brief.

### Individual oral presentation and questions — 20 points

Each student must prepare and deliver **a short pitch presentation (5–7 minutes)** about the project.

After the presentation, each student must individually answer questions about the project and its implementation.

The oral assessment may include:

- explanation of the overall project architecture and workflow
- demonstration of the implemented functionality
- explanation of selected parts of the code
- explanation of the database design and API endpoints
- explanation and justification of the recommendation scoring logic
- questions about implementation decisions and how specific functionality works

### Minimum Requirement for Passing the Subject

To successfully pass the subject, each student must achieve
**at least 50% of the available points (10 out of 20 points)**
in the individual oral presentation and questions.

This is a **mandatory passing requirement**, regardless of
the total number of points earned from the project implementation.

Students who score fewer than 10 points in the individual oral
assessment will not be eligible to pass the subject, even if
their combined project score would otherwise be sufficient.

## 14. Important Rules

- No authentication is required.
- No machine learning model is required.
- The recommendation formula must be explainable.
- The frontend should remain simple.
- The system must run locally.
- Prepare final technical documentation using the provided template.
- Show evidence that the API and frontend were tested.
- Create and maintain a GitHub repository for the project.
