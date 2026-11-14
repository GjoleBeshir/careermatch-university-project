"""Run against a locally running disposable CareerMatch/PostgreSQL instance."""
import json
from pathlib import Path
from datetime import date
import httpx
from sqlalchemy import text
from app.database import engine

out = {"database": "PostgreSQL", "checks": [], "profiles": []}
def check(name, condition):
    assert condition, name
    out['checks'].append(name)

with engine.connect() as db:
    check('PostgreSQL SELECT version and SELECT 1', 'PostgreSQL' in db.scalar(text('SELECT version()')) and db.scalar(text('SELECT 1')) == 1)
with httpx.Client(base_url='http://127.0.0.1:8765', trust_env=False) as client:
    jobs=client.get('/jobs').json(); candidates=client.get('/candidates').json()
    check('GET /jobs: exactly 160 jobs',len(jobs)==160)
    check('GET /candidates: exactly 85 candidates',len(candidates)==85)
    check('GET /health',client.get('/health').json()=={'status':'ok'})
    for path in ['/jobs/1','/candidates/1','/docs','/openapi.json','/','/static/app.js','/static/styles.css']:
        check('GET '+path,client.get(path).status_code==200)
    for path in ['/jobs/99999','/candidates/99999','/recommendations/99999']:
        check('404 '+path,client.get(path).status_code==404)
    check('422 invalid coordinates',client.get('/recommendations?lat=91&lon=0').status_code==422)
    check('422 invalid candidate ID',client.get('/recommendations/nope').status_code==422)
    for category in sorted({j['category'] for j in jobs}):
        for employment in ['Internship','Part-time','Full-time']:
            expected=[j for j in jobs if j['category']==category and j['employment_type']==employment and j['work_mode']=='Remote']
            actual=client.get('/jobs',params={'category':category,'employment_type':employment,'remote_only':True}).json()
            check(f'Combined filters: {category}/{employment}/Remote',actual==expected)
    check('Empty jobs',client.get('/jobs?category=Missing').json()==[])
    check('Empty ad-hoc recommendations',client.get('/recommendations?lat=41&lon=21&category=Missing').json()['recommendations']==[])
    check('GET /recommendations ad hoc',bool(client.get('/recommendations?lat=41.9981&lon=21.4254&skills=Python,SQL').json()['recommendations']))
    eligible={j['id'] for j in jobs if j['application_deadline']>=date.today().isoformat() and j['vacancies']>j['filled_positions']}
    for candidate_id in [1,2,3,4,5]:
        payload=client.get(f'/recommendations/{candidate_id}?limit=200').json(); items=payload['recommendations']
        check(f'Profile {candidate_id}: exact eligible jobs', {r['job_id'] for r in items}==eligible)
        check(f'Profile {candidate_id}: sorted deterministic ranking', items==sorted(items,key=lambda r:(-r['score'],r['job_id'])) and items==client.get(f'/recommendations/{candidate_id}?limit=200').json()['recommendations'])
        check(f'Profile {candidate_id}: bounds and breakdown',all(0<=r['score']<=100 and r['score']==round(sum(r['score_breakdown'].values())) and r['reason'] for r in items))
        out['profiles'].append({'id':candidate_id,'name':payload['candidate_name'],'top_job':items[0]['title'],'top_job_id':items[0]['job_id'],'score':items[0]['score'],'matches':len(items)})
    check('Five different recommendation rankings',len({(p['top_job_id'],p['score']) for p in out['profiles']})==5)
    created_job=created_candidate=None
    try:
        def create_payload(row): return {k:v for k,v in row.items() if k not in ('id','created_at','updated_at','deleted_at')}
        candidate=create_payload(candidates[0]);candidate['email']='qa-live@example.test'
        r=client.post('/candidates',json=candidate)
        check('POST /candidates: 201 after explicit-ID seed',r.status_code==201)
        created_candidate=r.json()['id'];check('Candidate sequence > 85',created_candidate>85)
        check('Duplicate candidate: 409',client.post('/candidates',json=candidate).status_code==409)
        r=client.post('/jobs',json=create_payload(jobs[0]))
        check('POST /jobs: 201 after explicit-ID seed',r.status_code==201)
        created_job=r.json()['id'];check('Job sequence > 160',created_job>160)
        check('Read created job',client.get(f'/jobs/{created_job}').status_code==200)
        bad=create_payload(jobs[0]);bad['filled_positions']=bad['vacancies']+1
        check('Invalid vacancies: 422',client.post('/jobs',json=bad).status_code==422)
    finally:
        # Delete only records created by this disposable QA run.
        with engine.begin() as db:
            if created_job: db.execute(text('DELETE FROM jobs WHERE id=:id'),{'id':created_job})
            if created_candidate: db.execute(text('DELETE FROM candidates WHERE id=:id'),{'id':created_candidate})
            for table in ('jobs','candidates'):
                db.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}','id'),(SELECT max(id) FROM {table}),true)"))
    check('Original dataset counts restored',len(client.get('/jobs').json())==160 and len(client.get('/candidates').json())==85)
out['passed']=len(out['checks'])
Path('docs/LIVE_QA_RESULTS.json').write_text(json.dumps(out,indent=2))
print(json.dumps({'passed':out['passed'],'profiles':out['profiles']},indent=2))
