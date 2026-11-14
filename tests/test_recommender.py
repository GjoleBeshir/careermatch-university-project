from datetime import date, timedelta, time
from types import SimpleNamespace
from app.recommender import score_job, rank_jobs, haversine_km, WEIGHTS

def example():
    candidate = SimpleNamespace(study_area='Computer Science', skills=['Python','SQL'], interests=['Software Development'], preferred_employment_type='Internship', preferred_work_mode='Remote',latitude=41.9981,longitude=21.4254,available_from=time(9),available_to=time(17),min_salary=20000)
    job = SimpleNamespace(id=9,title='Python Intern',category='Software Development',employer='Demo',employment_type='Internship',work_mode='Remote',location_name='Skopje',latitude=41.9981,longitude=21.4254,required_skills=['Python','SQL'],target_audience='Computer Science',salary_min=25000,salary_max=35000,application_deadline=date.today()+timedelta(days=10),vacancies=2,filled_positions=0,schedule_start=time(9),schedule_end=time(15),deleted_at=None)
    return candidate, job

def test_perfect_match_and_determinism():
    c,j=example()
    first=score_job(c,j)
    assert first['score']==100
    assert first==score_job(c,j)
    assert sum(WEIGHTS.values())==100
    assert first['distance_km'] is None

def test_exclude_expired_full_and_deleted():
    c,j=example()
    j.application_deadline=date.today()-timedelta(days=1)
    assert score_job(c,j) is None
    j.application_deadline=date.today()+timedelta(days=1)
    j.filled_positions=2
    assert score_job(c,j) is None
    j.filled_positions=0
    j.deleted_at='deleted'
    assert score_job(c,j) is None

def test_missing_salary_and_no_skills():
    c,j=example()
    j.salary_max=None; j.salary_min=None; c.skills=[]
    result=score_job(c,j)
    assert result['score_breakdown']['skills']==0
    assert result['score_breakdown']['salary']==5
    assert 'No direct required-skill overlap' in result['reason']

def test_distance_and_sorting():
    c,j=example()
    assert haversine_km(41.9981,21.4254,41.9981,21.4254)==0
    j2=SimpleNamespace(**vars(j)); j2.id=10; j2.required_skills=['Rust']; j2.work_mode='On-site'; j2.latitude=42.5
    result=rank_jobs(c,[j2,j])
    assert result[0]['job_id']==9
    assert result[1]['distance_km']>30


def test_independent_factor_changes():
    c,j=example()
    j.required_skills=['Python','SQL','Git','Java']
    assert score_job(c,j)['score_breakdown']['skills']==17.5
    j.target_audience='Engineering'
    assert score_job(c,j)['score_breakdown']['education']==0
    j.target_audience='Any'
    assert score_job(c,j)['score_breakdown']['education']==15
    c.available_from=time(15); c.available_to=time(17)
    assert score_job(c,j)['score_breakdown']['employment_schedule']==9
    c.preferred_employment_type='Full-time'
    assert score_job(c,j)['score_breakdown']['employment_schedule']==2.7
    j.salary_max=10000
    assert score_job(c,j)['score_breakdown']['salary']==2
    j.application_deadline=date.today()
    assert score_job(c,j) is not None
    j.filled_positions=j.vacancies-1
    assert score_job(c,j)['available_positions']==1

def test_near_far_and_remote_distance():
    c,j=example(); j.work_mode='On-site'; c.preferred_work_mode='On-site'
    assert score_job(c,j)['score_breakdown']['location_mode']==15
    j.latitude=45
    assert score_job(c,j)['score_breakdown']['location_mode']==7.5
    j.work_mode='Remote'; c.preferred_work_mode='Remote'
    assert score_job(c,j)['score_breakdown']['location_mode']==15
    assert score_job(c,j)['distance_km'] is None

def test_ties_use_id_and_normalized_skills():
    c,j=example(); c.skills=[' python ', 'SQL', 'SQL']
    other=SimpleNamespace(**vars(j)); other.id=2
    assert [x['job_id'] for x in rank_jobs(c,[j,other])]==[2,9]
    assert score_job(c,j)['score_breakdown']['skills']==35
