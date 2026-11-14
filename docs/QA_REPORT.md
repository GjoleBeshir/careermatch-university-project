# CareerMatch QA — 14 November 2026

## Result

The actual FastAPI application ran against PostgreSQL 16.2. All eight required endpoints passed live HTTP checks. The visible Work browser could not reach the runner's isolated loopback network, so the requested interactive browser demonstration and visual desktop/mobile QA were **not completed**. No screenshots, mockups or replayed data are presented as a running application.

## Executed verification

- Installed the project requirements. Docker and system PostgreSQL were unavailable; installed PostgreSQL binaries using the pgserver package and ran the real PostgreSQL server over local TCP. No SQLite substitution in the running application.
- Loaded exactly 160 jobs and 85 candidates into PostgreSQL. All 12 categories include Internship, Part-time and Full-time listings.
- Executed 79 live HTTP/database assertions twice, with reseeding between runs. See LIVE_QA_RESULTS.json for named assertions and five candidate summaries.
- All eight required endpoints, database version/connectivity, health, HTML/CSS/JS serving, /docs HTML and OpenAPI JSON passed.
- POST candidate and job returned 201 with IDs above the seeded range. Duplicate email returned 409; invalid coordinates/vacancies returned 422; missing jobs/candidates/recommendations returned 404.
- Compared all 36 category/type/remote filter combinations with independently filtered jobs; tested empty results and five independently ranked candidate profiles.
- Exactly 151 eligible jobs for each candidate: nine filled jobs excluded. Ranked results were deterministic and sorted by score then job ID; scores equaled rounded breakdown sums and stayed within 0–100.
- Isolated automated suite: 16 passed. Covers exact skills ratios, education mismatch/Any audience, schedule overlap, type preference, near/far/remote distance, salary above/below/undisclosed, expired/deadline-today jobs, full/remaining vacancies, soft deletion, stable ties, no skills, API validation, filters, profiles and simulated database outage (health 503). These tests use SQLite as disclosed in conftest; PostgreSQL verification is separate.
- JavaScript syntax check: node --check frontend/app.js passed.

## Fixes

1. CSV IDs did not advance PostgreSQL SERIAL sequences. Seed now synchronizes job/candidate sequences; live POST checks pass before and after reseeding.
2. Job cards lacked individual detail access. Added a native dialog fetching GET /jobs/{id}, showing description, requirements, schedule, salary, deadline, remaining positions and all six score factors.
3. Rapid candidate changes could show a stale response. Added request-version handling.
4. Connection status previously claimed success before any request. Added connecting/failure/success status and cleared stale counts on error. Health now queries the database.
5. Generated job type was correlated with category, making many filter combinations impossible. Each category now includes all three types.
6. Added narrow-screen wrapping and visible keyboard focus styles. Graduate profile labels are readable.
7. Launchers now run from their project directory and wait for database readiness before seeding.

## Browser limitation and unexecuted checks

The cloud browser attempted http://127.0.0.1:8765 and received net::ERR_CONNECTION_REFUSED. The same address returned successful live HTTP results inside the runner. Each command runs with a separate isolated local network; the PostgreSQL server, FastAPI server and live HTTP tests were therefore launched together in one runner process. The browser was unable to connect to that process.

Not verified: rendered dashboard/navigation, dropdown interactions, filter interactions, dialog opening/closing/focus, desktop/mobile layout and overflow, loading/error/empty-state appearance, browser console errors, or rendered interactive Swagger UI. /docs HTML and /openapi.json returned 200, but that is not proof that Swagger rendered. UI changes were inspected in source and syntax checked only. Windows/macOS launcher execution and Docker Compose startup were not available here. The two dependency deprecation warnings in UNIT_TEST_RESULTS.txt do not fail tests.

## Run on your computer

Start Docker Desktop, extract the ZIP, and double-click run_windows.bat on Windows (Python installed). On macOS/Linux run bash run_mac_linux.sh. Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/docs. The required FastAPI/PostgreSQL/vanilla HTML-CSS-JavaScript stack is preserved.

Choose candidates 1–5 to compare recommendations, combine the three filters, clear them, and click View details. Test at 390px and 1440px widths. Data is fictional university demonstration data. The official Week07 documentation template remains an academic submission task because it was not supplied.
