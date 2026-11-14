'use strict';
const $ = id => document.getElementById(id);
let requestVersion = 0;
const state = {jobs: [], candidates: [], recommendations: []};
const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function fetchJSON(url) { const response = await fetch(url); if (!response.ok) throw new Error(`Request failed (${response.status})`); return response.json(); }
function option(value, label) { const el = document.createElement('option'); el.value = value; el.textContent = label; return el; }
async function init() {
  try {
    const [candidates, jobs] = await Promise.all([fetchJSON('/candidates'), fetchJSON('/jobs')]);
    $('connection-status').textContent = 'Connected to CareerMatch API';
    state.candidates = candidates; state.jobs = jobs;
    $('candidate').replaceChildren(...candidates.map(c => option(c.id, c.name)));
    const categories = [...new Set(jobs.map(j => j.category))].sort();
    $('category').append(...categories.map(c => option(c, c)));
    const requested = new URLSearchParams(location.search).get('candidate_id');
    if (requested && candidates.some(c => String(c.id) === requested)) $('candidate').value = requested;
    if (!candidates.length) { $('list').innerHTML = '<div class="empty"><b>No candidates found</b>Run the seed command from README first.</div>'; return; }
    await loadMatches();
  } catch(e) { errorState(e); }
}
function errorState(e) { $('connection-status').textContent = 'Connection failed — retry by reloading'; $('count').textContent = '—'; $('visible-count').textContent = '';  $('list').innerHTML = `<div class="empty"><b>Could not load results</b>${escapeHTML(e.message)}. Check that the API and PostgreSQL are running and the seed command completed.</div>`; }
function profile(c) {
  $('profile-card').innerHTML = `<div class="profile-name">${escapeHTML(c.name)}</div><div class="profile-sub">${escapeHTML(c.study_area)} · ${c.year_of_study === 0 ? 'Graduate' : 'Year ' + c.year_of_study}</div><div class="skill-chips">${c.skills.slice(0,4).map(s => `<span class="chip">${escapeHTML(s)}</span>`).join('')}</div>`;
}
async function loadMatches() {
  const version = ++requestVersion;
  const id = $('candidate').value;
  const c = state.candidates.find(c => String(c.id) === id);
  if (c) profile(c);
  $('list').innerHTML = '<div class="loading">Calculating personalized matches...</div>';
  try {
    const data = await fetchJSON(`/recommendations/${encodeURIComponent(id)}?limit=200`);
    if (version !== requestVersion) return;
    $('connection-status').textContent = 'Connected to CareerMatch API';
    state.recommendations = data.recommendations;
    $('count').textContent = data.total_matches;
    const params = new URLSearchParams(location.search); params.set('candidate_id', id);
    history.replaceState(null, '', `${location.pathname}?${params.toString()}${location.hash}`);
    render();
  } catch(e) {if (version === requestVersion) errorState(e);}
}
function render() {
  let items = state.recommendations.filter(item => {
    if ($('category').value && item.category !== $('category').value) return false;
    if ($('employment').value && item.employment_type !== $('employment').value) return false;
    if ($('remote').value && item.work_mode.toLowerCase() !== $('remote').value) return false;
    return true;
  });
  $('visible-count').textContent = `(${items.length})`;
  if (!items.length) { $('list').innerHTML = '<div class="empty"><b>No matching opportunities</b>Try clearing filters or selecting another candidate.</div>'; return; }
  $('list').innerHTML = items.map(item => {
    const initials = item.employer.split(' ').map(w => w[0]).slice(0,2).join('');
    const salary = item.salary_min == null ? 'Salary undisclosed' : `${Number(item.salary_min).toLocaleString()}–${Number(item.salary_max).toLocaleString()} MKD/mo`;
    const location = item.work_mode === 'Remote' ? 'Remote' : `${item.location_name}${item.distance_km == null ? '' : ` · ${item.distance_km} km away`}`;
    const date = new Date(item.application_deadline + 'T12:00:00').toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric'});
    return `<article class="job-card"><div class="job-main"><div class="job-top"><span class="company-icon">${escapeHTML(initials)}</span><div><h3 class="job-title">${escapeHTML(item.title)}</h3><span class="employer">${escapeHTML(item.employer)} · ${escapeHTML(item.category)}</span></div></div>
    <div class="tags"><span class="tag primary">${escapeHTML(item.employment_type)}</span><span class="tag">${escapeHTML(item.work_mode)}</span><span class="tag">${escapeHTML(location)}</span></div>
    <p class="reason">✦ ${escapeHTML(item.reason)}</p><div class="details"><span>◷ Apply by ${escapeHTML(date)}</span><span>◈ ${escapeHTML(salary)}</span><span>◉ ${item.available_positions} available</span></div></div>
    <div class="job-right"><div><div class="score">${item.score}<small>/100</small></div><div class="score-label">MATCH SCORE</div><div class="score-bar"><div class="score-fill" style="width:${item.score}%"></div></div></div><button class="detail-btn" data-job-id="${item.job_id}">View details ↗</button></div></article>`;
  }).join('');
}
$('candidate').addEventListener('change', loadMatches);
for (const id of ['category','employment','remote']) $(id).addEventListener('change', render);
$('reset').addEventListener('click', () => { for (const id of ['category','employment','remote']) $(id).value = ''; render(); });
init();

$('list').addEventListener('click', async event => {
  const button = event.target.closest('[data-job-id]');
  if (!button) return;
  const id = Number(button.dataset.jobId);
  const match = state.recommendations.find(item => item.job_id === id);
  $('job-detail').innerHTML = '<p>Loading job details…</p>';
  $('job-dialog').showModal();
  try {
    const job = await fetchJSON(`/jobs/${id}`);
    $('job-detail').innerHTML = `<h2 id="detail-title">${escapeHTML(job.title)}</h2><p>${escapeHTML(job.employer)} · ${escapeHTML(job.location_name)} · ${escapeHTML(job.work_mode)}</p><p>${escapeHTML(job.description)}</p><h3>Requirements</h3><p>${job.required_skills.map(escapeHTML).join(', ')} · ${escapeHTML(job.target_audience)}</p><p>Schedule: ${job.schedule_start.slice(0,5)}–${job.schedule_end.slice(0,5)} · ${escapeHTML(job.employment_type)}</p><p>Salary: ${job.salary_min ?? 'Undisclosed'}–${job.salary_max ?? 'Undisclosed'} MKD/month</p><p>Apply by ${escapeHTML(job.application_deadline)} · ${job.vacancies-job.filled_positions} positions available</p><h3>Why this matches: ${match.score}/100</h3><p>${escapeHTML(match.reason)}</p><dl class="breakdown">${Object.entries(match.score_breakdown).map(([key, points]) => `<div><dt>${escapeHTML(key.replaceAll('_',' '))}</dt><dd>${points} points</dd></div>`).join('')}</dl>`;
  } catch (error) { $('job-detail').textContent = `Could not load job: ${error.message}. Close and try again.`; }
});
$('close-details').addEventListener('click', () => $('job-dialog').close());
