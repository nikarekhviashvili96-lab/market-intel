---
id: SPEC-0001
type: spec
title: Foundation and walking skeleton — US 10Y from FRED to one chart, with auth, RLS and sharing rules
status: review
created: 2026-11-15
updated: 2026-11-15
intent: "[[intent]]"
adrs: []
related:
  - "[[fred]]"
  - "[[supabase-free-plan]]"
  - "[[vercel-hobby]]"
  - "[[github]]"
  - "[[plan]]"
---

# SPEC-0001: Foundation and walking skeleton

## 1. Problem and goal

The old dashboard showed numbers that did not match their source, wrong labels and broken loading states
([[intent]] §1). Before any page of v1 is rebuilt, the whole path has to work end to end on one series and be
provably correct and safe: US 10-year Treasury yield (FRED `DGS10`) → daily job → database → one chart on the
deployed site. The same foundation carries everything after it: the series registry, point-in-time storage,
row-level security on every table, invite-only login with owner and viewer roles, per-source sharing rules, and
a read-only database role for future AI. It serves goals G1, G2, G3, G4, G6, G7, G8 and G9. The remaining v1 pages
(Overview, Economy US/Georgia, News) are SPEC-0002, built on this foundation (owner, 2026-11-15).

Supabase, Vercel, GitHub Actions and Python are the owner's default stack ([[intent]] §5); the binding choices —
the role, sharing and row-level-security model, the point-in-time schema and the scheduler — are stage 3 ADRs.
This spec says what the result must do, not how it is built.

## 2. Users and scenarios

- **Owner, morning check on the phone.** Logs in, opens the page, sees the latest 10Y yield with its date, the
  1-year chart, the source line — and can switch to 5Y or 10Y.
- **Invited viewer.** The owner creates an account for a colleague with a temporary password and passes it on; they
  log in and see the same `DGS10` chart: the owner flagged the source shareable (2026-11-15, [[fred]]). For a source
  that is not shareable they would see the series title and "This data is not available to viewers yet" instead of
  the chart.
- **Bad day — FRED is down or answers nonsense.** The daily job records a failed run and stores nothing from that
  answer; yesterday's data stays; the page shows "stale". Nothing else breaks.
- **Bad day — a holiday.** FRED returns `"."` for the day. Nothing is stored for that date; the chart has no point
  there, never a drop to 0.
- **Bad actor.** Someone takes the public database key from the browser and calls the database API directly: without
  a login they read and write nothing; as a viewer they cannot write and cannot read non-shareable data.

## 3. Scope

- **In:** daily ingestion of `DGS10` (10 years of history on the first run, then new and revised values);
  point-in-time storage; the series registry with one entry; run records and stale status; one chart page;
  invite-only login (email + password) with owner/viewer roles and a change-password page; row-level security on every table; per-source
  sharing flag; read-only AI database role; account removal; CI and main-branch protection; $0 running cost.
- **Out:** Overview, Economy US/Georgia, News and every other series (SPEC-0002); MFA for the owner (SPEC-0002,
  owner 2026-11-15); an in-app admin screen (accounts are managed in the Supabase dashboard); any AI feature (phase
  5 — only the database role, the permission function and their tests exist now); page-speed targets (SPEC-0002);
  replacing a part of the old dashboard (criterion decided in SPEC-0002).

## 4. Requirements

| ID | Requirement | Goal | Priority |
|---|---|---|---|
| REQ-001 | A daily job, run every day including weekends, fetches `DGS10` from FRED: the first run loads 10 years of history, later runs re-fetch the last 30 days. Every stored observation has its observation date, value, retrieval time (`as_of`) and source. Storage is append-only: a row is added only when a date is new or its value differs from the latest stored value for that date; old rows stay. A missing value (`"."`) is stored as no observation, never as 0. An answer that is not valid (an error body, a non-numeric value other than `"."`, an empty series, a repeated date) fails the run and stores nothing from it. Every run leaves a run record (start, end, result, rows added) | G1, G3, G4 | must |
| REQ-002 | A series registry holds, for `DGS10`: ID, source, exact definition, units, frequency, transformation (none), stale threshold, citation text, and the source's sharing flag. Every label, unit, description and citation on the page comes from the registry; none is written by hand in the page | G2 | must |
| REQ-003 | A source failure is isolated: the job records the failed run and keeps the stored data, and the run ends as failed so GitHub notifies the owner by its built-in workflow-failure email ([[github]]). A daily series is stale when its latest observation date is more than 2 US business days old — a working assumption until the US federal holiday list and H.15's publication timing are verified and dated in `docs/domain/` at stage 4; weekends and US federal holidays are not business days (holiday list kept in the repository with its source). When stale, the page shows "stale — last observation <date>, last successful update <as_of>"; for a viewer of a non-shareable source it shows only "stale", without the observation date | G4 | must |
| REQ-004 | One chart page, phone-width first: latest value and its observation date; 1Y / 5Y / 10Y range buttons (1Y default); units and description from the registry; the credit line from the registry, "Source: U.S. Treasury via Federal Reserve H.15; retrieved from FRED, Federal Reserve Bank of St. Louis" (owner, 2026-11-15, [[fred]]), with its retrieval date; FRED's API notice, a link to FRED's Terms of Use and the sentence that using the site means accepting them; stale badge when stale; light and dark mode; tap targets at least 44×44 px; text contrast at least 4.5:1 (WCAG AA). Opening the page reads only from the database and never calls an outside API | G6, G8 | must |
| REQ-005 | Login is invite-only and email + password: public sign-up is off on the deployed project; accounts are created only by the owner, by hand in the Supabase dashboard with a temporary password the owner passes on, and the owner resets viewers' passwords (the built-in email reaches only project team members — [[supabase-free-plan]]; an email service only in SPEC-0002 and only if needed — owner, 2026-11-15); each account has a role, `owner` or `viewer`, stored in a table only the server-side role can write; a new account is `viewer`; the owner role is set once by hand; a logged-in user can change their own password on a change-password page; passwords have at least 12 characters; Supabase Auth's built-in login rate limits stay switched on (their values checked and dated in `docs/domain/` at stage 4); the database refuses a 6th viewer (max 5, non-commercial, [[vercel-hobby]]). The only personal data kept is each account's email and role; removing an account in the dashboard deletes its role row too; no analytics or tracking scripts | G9 | must |
| REQ-006 | Row-level security is on for every table from the first migration. Without login nothing is read or written; a logged-in account without a role row reads nothing and writes nothing. Writes come only from the server-side ingestion role. A viewer reads the registry entry (title, units, description, sharing flag) and the run status (result and time of the last run) of every series — this is metadata, not source data — but observations, and anything derived from them such as the last observation date, only of sources whose sharing flag is "shareable". The flag starts as "not shareable"; only the server-side role changes it, and only after the source's terms are verified in `docs/domain/` and the owner confirms. Exception: `DGS10` is shareable by the owner's explicit decision of 2026-11-15, based on the owner's legal reading (17 U.S.C. §105 and the Federal Reserve Board's terms), not on verified Treasury terms ([[fred]]). A viewer of non-shareable data sees "This data is not available to viewers yet". The owner reads everything | G9 | must |
| REQ-007 | A dedicated database role for AI reads what the owner reads and cannot insert, update or delete anything. A database function `ai_run_allowed()` returns true only for a logged-in `owner`; every future AI feature must call it before it starts. No AI feature is built in this spec | G9 | must |
| REQ-008 | CI runs build, tests and gitleaks on every PR; `main` accepts changes only through a PR whose checks are green, for administrators too — the ruleset `main-protection` requires a PR and the `gates` check, forbids force-push and deletion, and has an empty bypass list by the owner's statement ([[github]]); the repository is public, so this costs nothing. No secret is in the repository: the FRED key and the database service key live only in GitHub Secrets and the Vercel environment and never reach the browser. No service has a payment card attached | G7 | must |
| REQ-009 | The product UI is English-only: every label, message, error text, date and number is in English and formatted for en-US (owner, 2026-11-15); no other language appears anywhere in the UI — the chart page, the login and change-password pages, login error messages and the browser tab title (never a framework default such as "Create Next App") | [[intent]] §3, §5 | must |

## 5. Acceptance criteria

| ID | Given / When / Then | What you will see or do | What proves it (gate / test / eval) |
|---|---|---|---|
| AC-001 | Given a recorded FRED response with 10 years of `DGS10` that includes a holiday with value `"."`, When the first run ingests it and the page data is read, Then the stored history starts 10 years back, every stored and charted point equals the recorded value for its observation date, and the holiday date has no point (no row, no 0) | On the 1Y chart around a US holiday (e.g. 4 July) the line skips the day — no drop to 0; the 10Y button shows ten years | Test (unit + integration) on the recorded fixture, in the `gates` CI check |
| AC-002 | Given the same recorded response, When the job runs twice, Then no row is added the second time; Given a second recording where a past value differs, When the job runs, Then one row is added, the old row stays and the page shows the newer value; Given a run on a Saturday, Then a run record exists | Not visible on screen — tests prove it | Test (integration, fixture pair, fixed clock) |
| AC-003 | Given FRED is simulated as down, or answers with an error body, a non-numeric value, an empty series or a repeated date, When the job runs, Then the run is recorded as failed, nothing from that answer is stored, earlier data is unchanged and the job ends with a failure exit code (which makes GitHub mark the run failed and email the owner); Given the latest observation is more than 2 US business days old, Then the page shows the stale badge with both dates (for a viewer of a non-shareable source: "stale" without the observation date), and on a weekend or US federal holiday it does not | On a test deployment with FRED switched off you see "stale — last observation …, last successful update …", and GitHub's failure email for that run arrives in your inbox | Test (job with faulty-source fixtures + staleness calendar with fixed dates) |
| AC-004 | Given the registry entry for `DGS10`, When the page is built, Then title, units, description and citation come from the registry, the FRED API notice, the Terms-of-Use link and the acceptance sentence are shown, and a check finds no indicator without a registry entry and no hand-written label; and on the chart page, the login and change-password pages, every login error message and the browser tab title, every date and number is formatted for en-US and no letter from a non-Latin script appears (e.g. none from the Georgian blocks U+10A0–U+10FF and U+1C90–U+1CBF), and the tab title is not a framework default | Under the chart: "Source: U.S. Treasury via Federal Reserve H.15; retrieved from FRED, Federal Reserve Bank of St. Louis" with its retrieval date, "Percent", the FRED notice and the Terms link; dates read like "Nov 14, 2026" | Test (page render + registry lint + en-US format and language check) |
| AC-005 | Given the page opened in a test browser, When every network request is recorded, Then none goes to an outside API — only to the site and the database; and Given the built site's files, When they are searched, Then neither the database service key nor the FRED key (nor their variable names) appears | Not visible on screen — tests prove it | Test (browser test with request log; scan of the build output) in CI |
| AC-006 | Given a phone width of 375 px, When the page opens in light and in dark mode, Then the latest value, its date and the chart are on the first screen, there is no horizontal scrolling, tapping 1Y / 5Y / 10Y changes the range (1Y on load), tap targets are at least 44×44 px and an accessibility check finds no contrast error | On your phone: open the site, switch dark mode on and off, tap 1Y / 5Y / 10Y | Browser test with screenshots at 375×812 in both modes and an automated accessibility check; your own phone at stage 5 |
| AC-007 | Given the public database key and no login, When anyone reads or writes any table, Then it is refused; Given a logged-in account with no role row, When it reads or writes any table, Then it gets no rows and every write is refused; Given a viewer, When they write anything or change a sharing flag, Then it is refused; When a viewer reads observations of a non-shareable source (test database), Then they get no rows and the page shows the title and "This data is not available to viewers yet"; When a viewer reads observations of a shareable source such as `DGS10`, Then they get the rows; When the owner reads, Then they get everything; When the owner, logged in to the site, tries to change a sharing flag, Then it is refused (only the server-side role can); and a catalog check finds no table without row-level security | Logged in as your test viewer you see the same `DGS10` chart as you do as owner; the non-shareable view and the locked sharing flag are proven by tests only | Test (database security tests on a local database, every table) |
| AC-008 | Given the deployed project, When someone tries to sign up without an account made by the owner, Then it is refused; Given a new account, Then its role is `viewer`; When a viewer tries to change any role, Then it is refused; When a 6th viewer account is created, Then the database refuses its role and that account can read nothing (it is left without a role until the owner deletes it); When the owner deletes an account, Then its role row is gone; When a user sets a password shorter than 12 characters, Then it is refused, and a longer one on the change-password page works; When login fails repeatedly in a short time, Then further attempts are temporarily refused | Try to sign up with a new email on the live login page — it is refused; change your own password on the change-password page | Test (auth and role tests, local) + one smoke test against the deployed project's sign-up |
| AC-009 | Given the AI database role, When it tries to insert, update or delete in any table, Then each is refused and reading works; When `ai_run_allowed()` is called as a viewer or without login, Then it returns false, and as the owner true | Not visible on screen — tests prove it | Test (database role tests) |
| AC-010 | Given a PR whose CI check fails (a failing test or a planted fake secret caught by gitleaks), When merge into `main` is attempted, Then GitHub refuses it; a direct push to `main` is refused | On GitHub, a test PR shows a red check and a blocked merge button | GitHub PR status on one demonstration PR; the `gates` and gitleaks CI checks |

## 6. Success measures and evals

| ID | Measure | Threshold | Where it is measured | When |
|---|---|---|---|---|
| M-001 | Correctness: each charted `DGS10` point equals FRED's latest value for its observation date; `"."` never becomes 0 | 100% of points | Fixture test (AC-001, AC-002); from stage 6 a live comparison against FRED | Every change; at stage 6 weekly |
| M-002 | Freshness: the daily job succeeds; when it does not, the page says so | ≥ 95% of days successful; stale shown within 2 US business days of the last observation | Run records in the database; AC-003 for the stale display | Stage 6, weekly |
| M-003 | Access: rows read or written without login; non-shareable rows reaching a viewer; writes by the AI role | 0 / 0 / 0 | Database security and role tests (AC-007, AC-008, AC-009) | Every change |
| M-004 | Cost | $0 per month; no payment card attached to any service | Billing pages of Supabase, Vercel and GitHub — checked by the owner by hand (FRED has no billing) | Stage 6, monthly |

No AI feature exists in this spec, so no eval set is written now; the AI role's limits are proven by tests (M-003).

## 7. Non-functional requirements

- **Security:** row-level security on every table; the database service key and the FRED key never reach the browser
  (only the public database key does, and it is safe only because of row-level security); secrets only in GitHub
  Secrets and the Vercel environment; gitleaks locally and in CI.
- **Personal data:** only account emails and roles; kept while the account exists; the owner deletes an account on a
  viewer's request; no analytics, cookies beyond login, or tracking.
- **Cost:** $0 per month on free tiers. Supabase Free pauses a project after a week of too little database activity;
  the daily job's writes count, but Supabase does not guarantee it ([[supabase-free-plan]]); the owner gets a warning
  email a week before.
- **Licensing:** FRED is for non-commercial, educational and personal use, with attribution and the API notice
  ([[fred]]); Vercel Hobby is for personal or non-commercial use only ([[vercel-hobby]]).
- **Language:** English-only UI with en-US dates and numbers (REQ-009; [[intent]] §3 and §5).
- **Not applicable here:** the language-model and untrusted-text invariants of `REVIEW.md` — no model and no outside
  text in this spec; they return with SPEC-0002 (News) and phase 5.

## 8. Risks and assumptions

| Risk / assumption | Effect | Mitigation |
|---|---|---|
| The shareable flag for `DGS10` rests on the owner's legal reading (17 U.S.C. §105, Board terms), not on Treasury's own site terms, which were not found; FRED's own series page also shows "Data in this graph are copyrighted" while its tags say "Public Domain: Citation Requested" ([[fred]]) | A reuse condition could be missed | Non-commercial, at most 5 viewers, full credit line and FRED notice on the page; the owner can flip the flag back at any time |
| Supabase's built-in email reaches only project team members, 2 per hour ([[supabase-free-plan]]) | Viewers get no invite or reset email | Owner creates viewer accounts by hand with a temporary password and resets them (owner, 2026-11-15); the owner's own reset email works |
| Supabase's pause threshold is not published | The project pauses and the page shows nothing | Daily writes; warning email; data kept and the project can be resumed |
| The US federal holiday list and H.15 publication delay are not yet verified | Wrong stale badge on a holiday | Holiday list from an official source, dated in `docs/domain/` at stage 4; AC-003 tests it |
| Free-tier limits and terms change | Cost or access changes | Facts dated in `docs/domain/`; re-checked before SPEC-0002 |
| Viewer use drifts toward commercial use | Breach of Vercel and FRED terms | Max 5 viewers enforced by the database; anything more needs a new ADR |

## 9. ღია კითხვები — Open questions

- FRED's missing-value marker `"."` is confirmed by the owner and secondary sources, not by FRED's API page.
  Resolution: the first recorded fixture (stage 4) confirms it; AC-001 and AC-003 fail on any other non-numeric value.

## Change history

- 2026-11-15 — Owner applied the round-2 medium findings and low #8: `DGS10` named as an explicit owner exception
  (REQ-006) with FRED's banner conflict in the risks; viewer metadata vs data defined; change-password page,
  12-character minimum and login rate limits (REQ-005, AC-008); REQ-009 covers login pages, errors and the tab title
  with a defined script check and traces to intent §3/§5; the 2-day stale rule marked a working assumption; failed
  runs email the owner (REQ-003, AC-003); owner-cannot-change-flag case (AC-007); ruleset recorded in [[github]].
- 2026-11-15 — Spec review round 2: an account without a role reads and writes nothing (REQ-006, AC-007, AC-008);
  retrieval date shown with the credit line; FRED dropped from the billing check.
- 2026-11-15 — Owner's decisions: `DGS10` flagged shareable with the credit line "Source: U.S. Treasury via Federal
  Reserve H.15; retrieved from FRED, Federal Reserve Bank of St. Louis"; English-only UI with en-US formats (REQ-009).
- 2026-11-15 — Owner's answers: viewer accounts created and reset by hand by the owner; G9 widened in the intent;
  H.15 / Federal Reserve Board terms checked and recorded in [[fred]].
- 2026-11-15 — Revised after the spec review (11 findings) and the builder check (5 questions): positive viewer path,
  AI permission function, validation of bad answers, stale threshold, citation and Terms sentence, accessibility
  numbers, personal data, deployed sign-up check, 6th-viewer refusal, key scan of the build.
- 2026-11-15 — First version, from the owner's answers to interview groups 1 and 2.
