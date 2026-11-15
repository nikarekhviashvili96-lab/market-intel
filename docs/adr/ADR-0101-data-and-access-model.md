---
id: ADR-0101
type: adr
title: Data and access model — point-in-time tables, series registry, roles, row-level security, sharing flag, AI role, daily schedule
status: proposed
date: 2026-11-15
deciders: owner (`/approve`); proposed by Claude Opus 5.5
related:
  - "[[intent]]"
  - "[[SPEC-0001-foundation-walking-skeleton]]"
  - "[[ADR-0100-stack-and-hosting]]"
  - "[[fred]]"
  - "[[supabase]]"
  - "[[supabase-free-plan]]"
  - "[[github]]"
---

# ADR-0101: Data and access model

## Context

SPEC-0001 fixes what must hold: append-only, point-in-time storage with `as_of` (REQ-001), a series registry that
drives every label (REQ-002), invite-only accounts with `owner` / `viewer` roles and at most 5 viewers (REQ-005),
row-level security on every table with a per-source sharing flag (REQ-006), a read-only AI role and
`ai_run_allowed()` (REQ-007), and a daily run every day of the week (REQ-001, REQ-003). [[intent]] §1 asks for one
schema per domain so later phases (companies, valuation, portfolio, journal) can be added without rebuilding. These
choices are the hardest to undo once data exists, which is why they are a separate decision from the stack
([[ADR-0100-stack-and-hosting]]).

## Decision

### Schemas and tables

- **`core` schema** — shared across domains:
  - `core.sources` — one row per data source: id, name, terms URL, `shareable` (boolean, default `false`), basis of
    the sharing decision (text, e.g. "owner's explicit decision 2026-11-15, [[fred]]"), decided date.
  - `core.series` — the registry: series id (`DGS10`), source id, title, exact definition, units, frequency,
    transformation, stale threshold in business days, credit line.
  - `core.job_runs` — one row per run, written once at the end: run id, source id, started at, ended at, result
    (`success` / `failed`), rows added, error text.
  - `core.user_roles` — one row per account: user id (references the Supabase Auth user, deleted with it), role
    (`owner` or `viewer`); at most one `owner` (unique index), at most 5 `viewer` rows (trigger).
- **`markets` schema** — v1's market data:
  - `markets.observations` — series id, observation date, value (numeric, never null), `as_of` (retrieval time),
    source id, run id; unique on (series id, observation date, `as_of`).
  - `markets.observations_latest` — a view (`security_invoker`, so row-level security of the caller applies) with
    the newest `as_of` row per series and date — what the chart reads.
- Later domains get their own schema (`companies`, `valuation`, `portfolio`, `journal`) with the same rules.
- Both schemas are exposed to Supabase's data API (a project setting, set by the owner once and in
  `supabase/config.toml` locally); all access goes through row-level security.

### Point-in-time and append-only

- The job inserts a row only when a date is new or its value differs from the latest stored value for that date;
  `"."` and invalid answers never become rows (SPEC-0001 REQ-001).
- `markets.observations` and `core.job_runs` reject `UPDATE` and `DELETE` for every role through a trigger; a revision
  is a new row. Data is corrected only by a new migration, reviewed in a PR.

### Roles

- **Database roles (Postgres):**
  - `ingest_writer` — a login role used only by the daily job: `INSERT` on `markets.observations` and
    `core.job_runs`, `SELECT` on what it must compare against, nothing else. It connects through Supabase's
    **shared pooler (Supavisor) in session mode** — IPv4, port 5432, username `ingest_writer.[PROJECT-REF]`
    ([[supabase]]). That is the primary and only path: on the Free plan a direct connection is IPv6-only, and
    GitHub-hosted runners have no IPv6 ([[github]]). Its connection string and password live only in GitHub Secrets
    (`INGEST_DATABASE_URL`). The Supabase service-role key is not used by the job or the site.
  - `ai_reader` — `SELECT` on every table and view, no `INSERT` / `UPDATE` / `DELETE` anywhere; no login until an AI
    feature exists (phase 5).
  - `anon` (not logged in) — no grants and no policies on any project table.
  - `authenticated` (logged in) — `SELECT` only, and only through the policies below.
- **App roles** (`core.user_roles`): a trigger on new Supabase Auth users inserts `viewer` while fewer than 5 viewers
  exist, otherwise inserts nothing — the account is left without a role and reads nothing until the owner deletes it
  (SPEC-0001 AC-008). The owner's own row is set to `owner` once, by hand, in the Supabase SQL editor.
- **Helper functions** (`SECURITY DEFINER`, fixed `search_path`): `core.app_role()` returns the caller's role or null;
  `core.ai_run_allowed()` returns true only when `core.app_role() = 'owner'`.

### Row-level security

On every table from the first migration; a catalog test fails if any table in `core`, `markets` or `public` lacks it.

| Table / view | owner | viewer | account without role | not logged in | `ai_reader` | `ingest_writer` |
|---|---|---|---|---|---|---|
| `core.sources`, `core.series` | read | read | nothing | nothing | read | read |
| `core.job_runs` | read | result and time only (view `core.run_status`) | nothing | nothing | read | insert |
| `markets.observations` (and the view) | read all | read rows of `shareable` sources only | nothing | nothing | read | insert, read |
| `core.user_roles` | read own row | read own row | nothing | nothing | read | nothing |

No role gets an update or delete policy. The sharing flag changes only through a migration (a PR the owner sees),
after the source's terms are recorded in `docs/domain/` and the owner confirms; `DGS10`'s source starts as
`shareable = true` by the owner's decision of 2026-11-15 ([[fred]]).

### Login settings

Public sign-up off and email + password only — in `supabase/config.toml` for the CI database, and set by the owner in
the Supabase dashboard for the live project (checked by SPEC-0001 AC-008's smoke test). Password minimum length 12.
Supabase Auth's built-in rate limits stay on.

### Daily schedule and migrations

- GitHub Actions runs the job daily at 02:17 UTC (06:17 Tbilisi), cron `17 2 * * *`, every day of the week, plus a
  manual run button. The minute is off the hour because scheduled runs can be delayed under heavy load, which is
  worst at the top of the hour (owner, 2026-11-15). Schedules run in UTC and only on the default branch ([[github]]). Secrets: `FRED_API_KEY`, `INGEST_DATABASE_URL`.
- A failed run exits non-zero, so GitHub marks it failed and emails the owner ([[github]]).
- Migrations in `supabase/migrations/` are applied to the live project by a GitHub Actions workflow after a merge to
  `main`, with `SUPABASE_ACCESS_TOKEN` and `SUPABASE_DB_PASSWORD` in GitHub Secrets — never from a laptop.

## Alternatives considered

- **Everything in the `public` schema.** Simpler setup. Not chosen: [[intent]] §1 asks for one module per domain;
  moving tables between schemas later means rewriting policies and queries.
- **Daily job writes with the Supabase service-role key.** One fewer role to manage. Not chosen: that key bypasses
  row-level security entirely, so a bug in the job could change or delete anything; `ingest_writer` can only insert.
- **FRED's vintage (ALFRED) parameters for revisions.** Exact historical vintages. Not chosen for SPEC-0001: re-fetching
  the last 30 days and storing changed values meets REQ-001 with one simple request; vintages can be added later
  without changing the table.
- **Refusing the 6th viewer at account creation (trigger raises an error).** Not chosen: SPEC-0001 AC-008 specifies a
  roleless account that reads nothing.

## Consequences

- + Every rule of SPEC-0001's access criteria is a database rule, so it holds even when someone calls the API
  directly; the tests of AC-007 to AC-009 run against these exact policies in CI.
- + Revisions never overwrite history; the chart shows the newest value per date.
- + New domains are new schemas with the same pattern.
- − Exposing custom schemas and setting login options are dashboard steps for the owner on the live project; the plan
  lists them as explicit owner steps.
- − Scheduled jobs in a public repository stop after 60 days without repository activity ([[github]]); a disabled
  schedule sends no failure email, so the stale badge is the only signal. Regular PRs keep it active; the plan adds a
  monthly check by the owner.
- − Supabase may pause the free project after a week of too little activity; daily writes count, but it is not
  guaranteed ([[supabase-free-plan]]).
- − Supabase's docs say a custom role can log in through the shared pooler ([[supabase]]); it is not yet proven live
  for this project. The plan's first database task is the live proof. If it fails, a superseding ADR chooses another
  write path.

## Verification

- Database tests in CI (SPEC-0001 AC-007, AC-008, AC-009): anonymous, roleless, viewer, owner, `ai_reader` and
  `ingest_writer` each try to read, insert, update and delete in every table; every result matches the table above.
- A catalog test lists all tables in `core`, `markets` and `public` and fails on any without row-level security.
- An append-only test: `UPDATE` and `DELETE` on `markets.observations` and `core.job_runs` fail for every role.
- Live proof, the plan's first database task: from a GitHub-hosted runner, `ingest_writer` connects through the
  session pooler as `ingest_writer.[PROJECT-REF]`, inserts one row, and its update and delete attempts are refused.
- The first scheduled run on the live project (02:17 UTC) leaves a `core.job_runs` row with result `success`.
