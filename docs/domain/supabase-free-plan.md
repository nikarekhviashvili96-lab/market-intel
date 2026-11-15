---
id: supabase-free-plan
type: domain
title: Supabase Free plan — limits and inactivity pause
status: living
updated: 2026-11-15
related:
  - "[[SPEC-0001-foundation-walking-skeleton]]"
---

# Supabase Free plan

Checked 2026-11-15. Neither page shows a last-updated date.

## Inactivity pause

Source: <https://supabase.com/kb/faqs/platform/free-project-pausing>.

- Only Free projects are paused: "If a Free project gets too little database activity over a week, Supabase
  pauses it."
- What counts: "Opening the project in the dashboard or sending real requests from your app both count as
  activity." — so the daily job's database writes are real requests and count.
- No guarantee: "A few requests a day is usually enough to keep a project running, though that isn't a guarantee."
  The exact threshold is not published.
- Warning: an email about a week before a pause, and another when it happens.
- A paused project keeps all its data and settings; it can be restored (separate restore guide).
- Supabase's advice: if people rely on the project, upgrade to a paid plan.

Consequence for this project: the daily job runs every day (weekends included) and writes at least its run record,
so there is database activity daily; the owner's warning email is the backstop.

## Built-in email (invites, password reset)

Source: <https://supabase.com/docs/guides/auth/auth-smtp> (no last-updated date shown), read 2026-11-15.

- Rate limit: "Currently this value is set to 2 messages per hour" — may change without notice.
- "Supabase Auth will refuse to deliver messages to addresses that are not part of the project's team." Sending to
  anyone else needs a custom SMTP server.
- "Not meant for production use"; no SLA.

Consequence: invite and reset emails reach only the owner (a team member); viewers need another path or a custom
SMTP service.

## Limits

Source: <https://supabase.com/docs/guides/platform/billing-on-supabase>.

- Two free projects (counted across organisations where you are Owner or Administrator); paused projects do not
  count toward the limit.
- Per project: 500 MB database, 50,000 monthly active users, 5 GB egress, 1 GB storage, 500,000 Edge Function
  invocations.
