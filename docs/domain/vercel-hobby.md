---
id: vercel-hobby
type: domain
title: Vercel Hobby plan — use restriction and limits
status: living
updated: 2026-11-15
related:
  - "[[SPEC-0001-foundation-walking-skeleton]]"
---

# Vercel Hobby plan

Checked 2026-11-15.

## Use restriction

Source: Vercel Terms of Service, section 4, <https://vercel.com/legal/terms> (last updated 2026-10-19).

- "You shall only use the Services under a Hobby plan for your personal or non-commercial use." The terms do not
  define commercial use.
- Owner's decision (2026-11-15): at most 5 invited viewers, non-commercial use. More viewers or any commercial use is
  a new decision with its own ADR.

## Limits

Source: <https://vercel.com/docs/plans/hobby> and <https://vercel.com/docs/limits/fair-use-guidelines> (both last
updated 2026-11-12).

- Function maximum duration: 300 s.
- Included per month: 1,000,000 function invocations, 4 active CPU-hours, 100 GB fast data transfer, 1,000,000 CDN
  requests.
- No spend management on Hobby: when a limit is exceeded the feature is generally unavailable until 30 days have
  passed — there is no bill.
- Deployment Protection on Hobby: Vercel Authentication for preview and production deployments.
