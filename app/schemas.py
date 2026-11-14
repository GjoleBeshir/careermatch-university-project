"""Public contract and validation for create/read APIs."""
from datetime import date, time, datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator

class CandidateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    study_area: str = Field(min_length=2)
    year_of_study: int = Field(ge=0, le=8)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    preferred_employment_type: str
    preferred_work_mode: str
    available_from: time
    available_to: time
    min_salary: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.available_to <= self.available_from:
            raise ValueError("available_to must be after available_from")
        return self

class CandidateRead(CandidateCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

class JobCreate(BaseModel):
    title: str = Field(min_length=2)
    description: str = Field(min_length=5)
    category: str = Field(min_length=2)
    employer: str = Field(min_length=2)
    location_name: str = Field(min_length=2)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    employment_type: str
    work_mode: str
    required_skills: list[str] = Field(default_factory=list)
    target_audience: str
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    application_deadline: date
    vacancies: int = Field(ge=0)
    filled_positions: int = Field(default=0, ge=0)
    schedule_start: time
    schedule_end: time

    @model_validator(mode="after")
    def validate_data(self):
        if self.salary_max is not None and self.salary_min is not None and self.salary_max < self.salary_min:
            raise ValueError("salary_max must be >= salary_min")
        if self.filled_positions > self.vacancies:
            raise ValueError("filled_positions cannot exceed vacancies")
        if self.schedule_end <= self.schedule_start:
            raise ValueError("schedule_end must be after schedule_start")
        return self

class JobRead(JobCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
