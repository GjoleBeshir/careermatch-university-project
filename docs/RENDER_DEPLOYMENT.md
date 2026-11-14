# Deploy CareerMatch on Render (browser-accessible demo)

This deploys **the actual FastAPI/SQLAlchemy app and PostgreSQL**, not the offline HTML demo.

## Deploy

1. Extract the ZIP. Create a GitHub repository, upload the **contents of the CareerMatch folder to the repository root** (so `render.yaml` appears at root). Do **not** upload `.env` or credentials.
2. Go to https://dashboard.render.com/blueprints and select **New Blueprint Instance**.
3. Connect the repository. Render reads `render.yaml` and proposes **a free web service and free PostgreSQL**. **Review pricing and all plan/expiry terms before accepting** (Render free databases are limited and may expire).
4. Apply the blueprint and watch the deployment logs. It automatically loads 160 synthetic jobs and 85 fictional candidates.
5. Once both resources show healthy, visit the assigned `https://YOUR-SERVICE.onrender.com/` URL.
6. Test `/health`, `/docs`, switch candidates, combine filters, and open job details. Do a mobile-width inspection in your browser.

The service must stay public for an external Work browser to load it. Do not put private student data in this demo: the sample data is fictional, **but the POST endpoints are unauthenticated and publicly writable** as requested by the assignment. This setup is for short-lived classroom demos, not production. Delete or restrict the resources afterward.

## Recording for presentation

Open the assigned URL in Chrome, run through candidate selector > job filtering > details > Swagger `/docs`, and capture the screen with Windows Xbox Game Bar (`Win+Alt+R`) or OBS. Work can also visit this public URL for browser QA if its browsing environment permits it. This ZIP does not include an actual browser recording.

## Troubleshooting

- `No module named ...`: confirm `render.yaml` is at repo root and `pip install -r requirements.txt` succeeds.
- `DATABASE_URL` / PostgreSQL connection failure: check that both Blueprint resources are up; the URL is set automatically by `fromDatabase`.
- Free web instance is asleep: wait for Render to spin it up, then refresh.
- Database expiry or billing: consult current Render plan details in your dashboard.
- `/health` returns 503: inspect DB resource and web service logs.

## Local fallback

Original local Windows instructions in `README.md` remain unchanged: Docker Desktop then `run_windows.bat`.
