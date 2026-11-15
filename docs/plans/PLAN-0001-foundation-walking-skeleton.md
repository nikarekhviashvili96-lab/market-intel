---
id: PLAN-0001
type: plan
title: Foundation and walking skeleton — build plan for SPEC-0001
status: draft
created: 2026-11-15
updated: 2026-11-15
spec: "[[SPEC-0001-foundation-walking-skeleton]]"
adrs:
  - "[[ADR-0100-stack-and-hosting]]"
  - "[[ADR-0101-data-and-access-model]]"
---

# PLAN-0001: Foundation and walking skeleton

## 1. Approach

Build SPEC-0001 on the accepted stack ([[ADR-0100-stack-and-hosting]]) and data model
([[ADR-0101-data-and-access-model]]) in thin slices, each ending green and committed. The first two tasks produce
something the owner can open: the parser's output for a real FRED recording (T1), then a chart page rendered from
that recording on the owner's laptop (T2). T3 is the first database task and the live proof that `ingest_writer`
can log in through Supabase's session pooler from a GitHub runner — the riskiest assumption, checked before the
schema is built on it. From there the path is filled layer by layer, always end to end: schema and access rules, the
job writing real data, the schedule, the site reading through row-level security, the browser checks, and finally
deployment. Every task writes its failing test first. Database tests run in CI only and show as skipped on the
owner's laptop (ADR-0100). Every install is from the owner's two approved lists (2026-11-15); versions are exact
and lockfiles are committed. One branch and one PR per task (T1…T9); each PR is merged after its `gates` check is
green, and the next task starts only after that merge (owner, 2026-11-15).

## 2. Tasks

- [ ] T1 — Python foundation: create `.venv`, install `pytest`, `httpx`, `psycopg[binary]` with exact versions into `ingest/requirements.txt` (approved list); write failing tests, then `ingest/fred.py` that parses a recorded FRED `DGS10` response — `"."` becomes no observation (never 0), an error body, a non-numeric value, an empty series and a repeated date each make the parse fail; `scripts/lint.sh` and `scripts/test.sh` run the stack's commands; switch on the `lint` and `unit` gates in `tools/gates/gates.toml` (protected file — the owner's yes is asked in one sentence) and turn `unit` red once on purpose, then back (REQ-001, AC-001, AC-003) — verify: `bash .claude/hooks/py.sh tools/gates/gate.py` exits 0; you see `{venv_python} -m ingest.fred tests/fixtures/fred_dgs10.json` print the parsed count and the skipped holiday dates
- [ ] T2 — Web skeleton with a fixture chart: scaffold `web/` (Next.js, TypeScript, Tailwind, ESLint; `save-exact=true`; `package-lock.json` committed) and add `recharts`, `vitest`, `@vitejs/plugin-react`, `jsdom`, `@testing-library/react` (approved lists); failing Vitest tests first for en-US date and number formatting, the credit line and the tab title; a phone-first page that draws `DGS10` from the T1 recording with 1Y / 5Y / 10Y buttons, light and dark mode, the credit line "Source: U.S. Treasury via Federal Reserve H.15; retrieved from FRED, Federal Reserve Bank of St. Louis", FRED's API notice, Terms link and acceptance sentence; lint and test scripts extended to `web/` (REQ-004, REQ-009, AC-004, AC-006) — verify: gate green; you open `http://127.0.0.1:3000` on your laptop (`npm --prefix web run dev`), see the chart, switch dark mode, tap 1Y / 5Y / 10Y, and the browser tab shows the product name, not "Create Next App"
- [ ] T3 — Live database and pooler proof (first database task, ADR-0101): add the Supabase CLI (`supabase`, dev dependency, approved); first migration creates `ingest_writer` and a throw-away table; a GitHub Actions workflow applies migrations to the live project after merge to `main` and a manual workflow connects as `ingest_writer.[PROJECT-REF]` through the session pooler, inserts one row and checks that update and delete are refused. **Owner steps first (accounts — cannot be undone by `git revert`):** create the Supabase Free project and, before anything else, switch public sign-up off and set the 12-character password minimum in its Auth settings — the API is public from the first minute (owner, 2026-11-15); set `ingest_writer`'s password in the SQL editor; add `SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `INGEST_DATABASE_URL` as GitHub Secrets — I give the exact clicks, no secret goes through the chat (ADR-0101) — verify: the manual workflow's run on GitHub is green and its log shows "insert ok, update refused, delete refused"; if it fails, stop and write a superseding ADR
- [ ] T4 — Schema and access rules: migrations for `core` and `markets` per ADR-0101 (sources, series registry with `DGS10` and its credit line, job runs, user roles with one owner and at most 5 viewers, observations, latest view, run-status view, append-only triggers, `core.app_role()`, `core.ai_run_allowed()`, `ai_reader`, sign-up off and 12-character passwords in `supabase/config.toml`); failing pytest database tests first for every cell of ADR-0101's access table, the roleless account, the 6th viewer, account deletion, the sharing-flag lock, the AI role, append-only, and the catalog check that every table has row-level security; CI starts the local Supabase on the Ubuntu job and sets `TEST_DATABASE_URL` inside the `gates` job (`.github/workflows/gates.yml`) (REQ-002, REQ-005, REQ-006, REQ-007, AC-007, AC-008, AC-009) — verify: gate green locally with the database tests reported as skipped; the CI `gates` check green with the same tests reported as run
- [ ] T5 — The job writes data: `{venv_python} -m ingest` fetches `DGS10` with `httpx` (10 years on the first run, last 30 days after), compares with the latest stored value per date, inserts new and revised rows with `as_of`, writes one run record, and exits non-zero on failure; failing tests first for idempotence, revision, Saturday run record and every faulty-source case against the CI database (REQ-001, REQ-003, AC-001, AC-002, AC-003) — verify: gate and CI green; then, **with the owner's yes (first write of real data to the live project)** and the FRED key added as GitHub Secret `FRED_API_KEY` by the owner, one manual run fills the live table; you see the row count and the newest date in the run's log
- [ ] T6 — Daily schedule and staleness: workflow `ingest.yml` with cron `17 2 * * *` (02:17 UTC) and a manual button; US federal holiday list from the official source and H.15's publication timing verified and recorded in `docs/domain/` with dates, then the 2-business-day stale rule tested against them; a failed run ends red so GitHub emails the owner (REQ-001, REQ-003, AC-002, AC-003) — verify: gate and CI green; the next scheduled run on GitHub is green and leaves a `success` run record; one deliberately failed manual run (FRED key temporarily wrong in a test run) produces GitHub's failure email in your inbox
- [ ] T7 — The site reads through row-level security: add `@supabase/supabase-js` and `@supabase/ssr` (approved); login page, change-password page and sign-out; the chart reads `markets.observations_latest` with the user's session; viewer of a non-shareable source sees the title and "This data is not available to viewers yet"; stale badge with both dates (only "stale" for a non-shareable source); every label, unit, description and credit line from the registry; failing Vitest tests first; **owner steps before the owner check:** expose the `core` and `markets` schemas in the Supabase dashboard, create your own account there and set its role to `owner` in the SQL editor (I give the exact statement) (REQ-002, REQ-004, REQ-005, REQ-006, REQ-009, AC-003, AC-004, AC-007) — verify: gate and CI green; on your laptop you log in as owner and see the live `DGS10` chart, then log in as your test viewer (you create it in the Supabase dashboard — I give the clicks) and see the same chart
- [ ] T8 — Browser checks: add `@playwright/test`, `@axe-core/playwright` and Playwright's Chromium (approved); failing tests first: every network request on page load goes only to the site and the database; screenshots at 375×812 in light and dark mode with no horizontal scroll and the first screen holding value, date and chart; 44×44 px tap targets and no contrast error; no non-Latin script on any page, login error or tab title; a scan of the build output finds neither key nor their variable names (including `INGEST_DATABASE_URL`); switch on the `e2e` gate (protected file — owner's yes) (REQ-004, REQ-008, REQ-009, AC-004, AC-005, AC-006) — verify: gate and CI green; I give you the two screenshot file paths to look at
- [ ] T9 — Deploy and prove it live: **owner steps first (account and publishing):** create the Vercel project (root `web/`, production branch `main`, Vercel Authentication on previews), add the public Supabase URL and anon key as Vercel environment variables; then a smoke test against the live site: sign-up is refused (it has been off since T3); one demonstration PR with a planted fake secret and a failing test is blocked by the `gates` check, and a direct push to `main` is refused (REQ-005, REQ-008, AC-008, AC-010) — verify: you open the live Vercel address on your phone, log in, see the chart; the demonstration PR on GitHub shows a red check and a blocked merge button; the `verifier` subagent returns `VERDICT: pass`

## 3. Gates, tests and evals

- Must be green: every gate of `bash .claude/hooks/py.sh tools/gates/gate.py` (graph, secrets, drill and the other engine gates already on), plus `lint` and `unit` from T1 and `e2e` from T8; the CI `gates` check on every PR.
- Switched on by this plan (existing gates, protected file — each with the owner's yes and one deliberate red run): `lint` → `["bash", "scripts/lint.sh"]`, `unit` → `["bash", "scripts/test.sh"]`, `e2e` → `["npm", "--prefix", "web", "run", "test:e2e"]`. No new gate type, guard or hook is added, so the drill gets no new case; the deliberate red run proves each switched-on gate can fail.
- Tests added: pytest (parser, job, database access — database tests skipped locally, run in CI), Vitest (formatting, registry-driven labels, page states), Playwright (requests, screenshots, accessibility, script check, build scan).
- No eval set: SPEC-0001 has no AI feature (SPEC-0001 §6).

## 4. Orchestration

Code loop ([[ADR-0005-maker-checker-orchestration]], stage I): Sonnet 5.5 writes, Opus 5.5 checks, at most 2 rounds per task — only if `orchestration/config.toml` has `enabled = true`. It is `false` (checked 2026-11-15), so each task is checked by the gates, CI and, before done, the `verifier` subagent.

## 5. Risks and rollback

| Risk | Mitigation | Rollback |
|---|---|---|
| `ingest_writer` cannot log in through the session pooler | T3 proves it before anything is built on it | Stop; a superseding ADR picks another write path |
| A protected-file change (gates, CI) breaks the commit check | One gate at a time, each with a deliberate red run | `git revert` of that task's commit |
| GitHub disables the schedule after 60 days without activity ([[github]]) | Regular PRs; the owner checks the Actions tab once a month at stage 6 | Re-enable the workflow in GitHub's Actions tab |
| Supabase pauses the free project ([[supabase-free-plan]]) | Daily writes; warning email | Resume the project in the dashboard; data is kept |
| A bad migration reaches the live database | Migrations reviewed in a PR and tested in CI first; observations are append-only | A new corrective migration; live data is never edited by hand |
| A bad deployment | Vercel keeps earlier deployments | Promote the previous deployment in Vercel |

## 6. Done when

Every task is ticked; every gate is green; the `verifier` subagent returns `VERDICT: pass`; the owner has opened the live site on a phone and seen the chart as owner and as viewer.

## გადახრები

(added during execution, old lines are never removed: `YYYY-MM-DD — what changed and why`)
