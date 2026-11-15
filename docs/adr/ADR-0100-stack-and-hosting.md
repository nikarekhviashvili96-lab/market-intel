---
id: ADR-0100
type: adr
title: Stack and hosting — Next.js + Tailwind on Vercel, Supabase, Python daily job on GitHub Actions
status: proposed
date: 2026-11-15
deciders: owner (`/approve`); proposed by Claude Opus 5.5
related:
  - "[[intent]]"
  - "[[SPEC-0001-foundation-walking-skeleton]]"
  - "[[ADR-0101-data-and-access-model]]"
  - "[[vercel-hobby]]"
  - "[[supabase-free-plan]]"
  - "[[github]]"
---

# ADR-0100: Stack and hosting

## Context

SPEC-0001 needs a logged-in, phone-first site that reads only from the database, a daily job that writes FRED data,
row-level security that holds even when someone calls the database API directly, and $0 running cost. The owner's
default stack is in [[intent]] §5; later phases add owner-only AI runs that must run on a server (phase 5) and long
runs on GitHub Actions. The owner does not read code, so every check must be a machine check that runs in CI.

The website guide's stack options (`docs/guides/website.md` §2) are for static sites without login; they do not fit
an authenticated data app and are not the alternatives here.

Machine state on 2026-11-15: Node 24.14.0, npm 11.9.0, Python 3.12.10; Docker and the Supabase CLI are not installed.

## Decision

**Option A, chosen by the owner on 2026-11-15:**

- **Site:** Next.js (App Router, TypeScript) with Tailwind CSS, in `web/`, hosted on Vercel Hobby (project root
  directory `web/`, production branch `main`, Vercel Authentication on preview deployments). Browser and server code
  get only the public Supabase URL and the public (anon) key; no server secret is needed by the site in SPEC-0001.
- **Chart library: Recharts** (MIT, built on React and D3, renders SVG). It beats the main alternative, Apache
  ECharts, here because SVG output puts every point, label and colour in the page itself, so Vitest and Playwright
  can check the values (AC-001) and the contrast (AC-006) directly; ECharts draws on a canvas those tests cannot
  read.
- **Database and login:** one Supabase Free project; schema changes as SQL migrations in `supabase/migrations/`
  (data and access model: [[ADR-0101-data-and-access-model]]).
- **Daily job:** Python 3.12 in `ingest/`, run by GitHub Actions on a schedule (time and secrets: ADR-0101).
- **Tests:** pytest for the job and the database; Vitest for site units; Playwright for browser tests (request log,
  screenshots at 375×812, accessibility check).
- **Database tests run in CI only** (owner, 2026-11-15). They need a real Postgres with Supabase's roles; CI starts
  it with the Supabase CLI on GitHub's runner (which has Docker). On a machine without that database the database
  tests report **skipped**, never passed — pytest marks them skipped when `TEST_DATABASE_URL` is not set. To keep
  them inside the required `gates` check, the CI job that runs `gate.py` starts the local Supabase first and sets
  `TEST_DATABASE_URL`.
- **Pinned versions** (owner, 2026-11-15): npm installs with exact versions (`save-exact=true` in `web/.npmrc`) and
  `web/package-lock.json` is committed; Python dependencies are pinned with `==` for direct and transitive packages in
  `ingest/requirements.txt`, committed. Versions are fixed at the first install task of the plan.
- **Folders:** `web/` (site), `ingest/` (job), `supabase/` (migrations, local config), `tests/` (Python tests,
  fixtures in `tests/fixtures/`).

### The five commands (not yet run — the plan's first task runs each once)

`{venv_python}` is `.venv/Scripts/python` on Windows, `.venv/bin/python` on macOS and Linux.

| Step | Command |
|---|---|
| install | `bash .claude/hooks/py.sh -m venv .venv`, then `{venv_python} -m pip install -r ingest/requirements.txt`; `npm --prefix web ci`; `npm --prefix web exec playwright install chromium` |
| run (local) | `npm --prefix web run dev` → `http://127.0.0.1:3000`; the job against a recorded fixture: `{venv_python} -m ingest --fixture tests/fixtures/fred_dgs10.json --dry-run` |
| lint | `npm --prefix web run lint` (ESLint and `tsc --noEmit`); `{venv_python} -m compileall -q ingest tests` (syntax only) |
| test | `{venv_python} -m pytest -q` (job and database tests; database tests skipped without `TEST_DATABASE_URL`); `npm --prefix web run test` (Vitest); `npm --prefix web run test:e2e` (Playwright) |
| show | `npm --prefix web run build`, then `npm --prefix web run start` → `http://127.0.0.1:3000`; after deployment, the Vercel address |

At stage 4, with the owner's yes (`tools/gates/gates.toml` is a protected file), the `lint` and `unit` gates are
switched on with these commands as argument lists, e.g. `["npm", "--prefix", "web", "run", "lint"]`.

### Packages

**Approved by the owner on 2026-11-15:**

- Python, in `.venv`: `pytest`, `httpx`, `psycopg`.
- npm, in `web/`: `next`, `tailwindcss`, `recharts`, `@supabase/supabase-js`, `vitest`, `@playwright/test`,
  `supabase` (CLI, development dependency).

**Also approved by the owner on 2026-11-15 (second list):**

- Brought by the Next.js + Tailwind + TypeScript scaffold: `react`, `react-dom`, `typescript`, `@types/node`,
  `@types/react`, `@types/react-dom`, `@tailwindcss/postcss`, `eslint`, `eslint-config-next`.
- `@supabase/ssr` — Supabase's helper that keeps the login session in cookies for Next.js server pages.
- For Vitest component tests: `@vitejs/plugin-react`, `jsdom`, `@testing-library/react`.
- `@axe-core/playwright` — the automated accessibility and contrast check of AC-006.
- The Chromium browser that Playwright downloads (`playwright install chromium`).
- `psycopg[binary]` instead of plain `psycopg` — the prebuilt variant, so Windows needs no C compiler or libpq.

## Alternatives considered

- **B — React built with Vite, talking to Supabase from the browser only.** Simpler today and also free on Vercel.
  Not chosen: there is no server side, so owner-only AI runs and server-held keys (phase 5) would need a second
  service or a rebuild.
- **C — Astro.** Good for content sites. Not chosen: login, per-user data and interactive charts work against its
  grain.
- **Chart library: Apache ECharts.** More chart types out of the box. Not chosen: canvas output that tests cannot
  inspect (see Decision).
- **Database tests on the owner's machine (Docker Desktop).** Not chosen by the owner: a large background install;
  CI covers the tests on every PR.

## Consequences

- + One language per job (TypeScript for the site, Python for the data), matching [[intent]] §5; phase 5 can add
  owner-only server code in the same Next.js app.
- + Every acceptance criterion of SPEC-0001 has a test runner: pytest, Vitest, Playwright, and CI for the database.
- + $0: Vercel Hobby, Supabase Free, GitHub Actions on a public repository ([[vercel-hobby]], [[supabase-free-plan]]).
- − Database tests do not run locally; a database bug shows up only in CI. The skipped count is printed every time.
- − Two package ecosystems (npm and pip) to keep pinned and updated.
- − Vercel Hobby is personal or non-commercial only; more than 5 viewers or commercial use needs a new ADR.

## Verification

- The plan's first task runs each of the five commands once; any difference goes into the plan's deviations section,
  this ADR stays as approved.
- `gate.py` exits 0 with the `lint` and `unit` gates switched on; the CI `gates` check is green on the first code PR.
- A deliberate break (a wrong expected value in one test) turns the `unit` gate red once, then is reverted.
- CI output shows the database tests as run (not skipped); a local run shows them as skipped.
- `web/package-lock.json` and `ingest/requirements.txt` are committed, and every version in them is exact.
