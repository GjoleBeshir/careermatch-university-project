from datetime import date, timedelta

def test_seed_counts(client):
    assert len(client.get('/jobs').json()) == 160
    assert len(client.get('/candidates').json()) == 85

def test_required_endpoints(client):
    assert client.get('/health').json() == {'status':'ok'}
    assert client.get('/jobs/1').status_code == 200
    assert client.get('/candidates/1').status_code == 200
    assert client.get('/jobs/9999').status_code == 404
    assert client.get('/candidates/9999').status_code == 404
    assert client.get('/recommendations/9999').status_code == 404
    r = client.get('/recommendations/1'); assert r.status_code == 200
    assert r.json()['candidate_id'] == 1
    assert r.json()['recommendations']
    adhoc = client.get('/recommendations?lat=41.9981&lon=21.4254&skills=Python,SQL')
    assert adhoc.status_code == 200 and adhoc.json()['recommendations']

def test_filters_combine(client):
    jobs = client.get('/jobs?category=Software%20Development&employment_type=Internship&remote_only=true').json()
    assert all(j['category'] == 'Software Development' and j['employment_type'] == 'Internship' and j['work_mode'] == 'Remote' for j in jobs)
    assert len(client.get('/jobs?remote_only=true').json()) > 0

def test_post_candidate_and_job(client):
    c = client.get('/candidates/1').json()
    c.pop('id'); c.pop('created_at'); c.pop('updated_at'); c.pop('deleted_at')
    c['email'] = 'newcandidate@example.test'
    assert client.post('/candidates', json=c).status_code == 201
    assert client.post('/candidates', json=c).status_code == 409
    j = client.get('/jobs/1').json()
    for f in ('id', 'created_at', 'updated_at', 'deleted_at'): j.pop(f)
    j['application_deadline'] = (date.today()+timedelta(days=30)).isoformat()
    result = client.post('/jobs', json=j)
    assert result.status_code == 201, result.text
    assert client.get('/jobs/'+str(result.json()['id'])).status_code == 200

def test_rank_and_explanation(client):
    items = client.get('/recommendations/2').json()['recommendations']
    assert all(0 <= item['score'] <= 100 and item['reason'] and item['score_breakdown'] for item in items)
    assert [i['score'] for i in items] == sorted((i['score'] for i in items), reverse=True)
    assert all(i['available_positions'] > 0 for i in items)

def test_validation(client):
    bad = client.get('/jobs/1').json()
    for f in ('id','created_at','updated_at','deleted_at'): bad.pop(f)
    bad['vacancies'] = 1; bad['filled_positions'] = 2
    assert client.post('/jobs', json=bad).status_code == 422
    assert client.get('/recommendations?lat=91&lon=0').status_code == 422


def test_empty_results_and_five_profiles(client):
    assert client.get('/jobs?category=NoSuchCategory').json()==[]
    assert client.get('/recommendations?lat=41&lon=21&category=NoSuchCategory').json()['recommendations']==[]
    signatures=[]
    for candidate_id in (1,2,3,4,5):
        result=client.get(f'/recommendations/{candidate_id}?limit=200').json()
        items=result['recommendations']
        assert items and result['candidate_id']==candidate_id
        assert items==sorted(items,key=lambda r:(-r['score'],r['job_id']))
        signatures.append([(r['job_id'],r['score']) for r in items])
    assert len({str(x) for x in signatures})==5

def test_dataset_types_are_varied_per_category(client):
    jobs=client.get('/jobs').json()
    for category in {j['category'] for j in jobs}:
        assert {j['employment_type'] for j in jobs if j['category']==category}=={'Internship','Part-time','Full-time'}


def test_health_reports_database_outage(client, db, monkeypatch):
    from sqlalchemy.exc import OperationalError
    def unavailable(*args, **kwargs):
        raise OperationalError('SELECT 1', {}, Exception('offline'))
    monkeypatch.setattr(db,'execute',unavailable)
    assert client.get('/health').status_code==503
