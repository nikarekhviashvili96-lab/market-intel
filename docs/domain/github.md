---
id: github
type: domain
title: GitHub — main-protection ruleset and workflow failure notifications
status: living
updated: 2026-11-15
related:
  - "[[SPEC-0001-foundation-walking-skeleton]]"
---

# GitHub

## Ruleset `main-protection` (this repository)

Read 2026-11-15 from GitHub's public REST API without a login
(`GET /repos/nikarekhviashvili96-lab/market-intel/rulesets/27259134` and `.../rules/branches/main`).

- Ruleset `main-protection` (id 27259134), enforcement **active**, target: the default branch (`~DEFAULT_BRANCH`),
  created 2026-11-14.
- Rules: `deletion` (main cannot be deleted), `non_fast_forward` (no force-push), `pull_request` (changes only through
  a PR; 0 required approvals), `required_status_checks` with the check `gates`.
- **Bypass list — not verified by the agent.** GitHub's docs: "the bypass_actors property is only returned if the user
  making the API request has write access to the ruleset" (<https://docs.github.com/en/rest/repos/rules>), and the
  agent's request had no login. The owner states (2026-11-15) that the bypass list is empty, so the rules also apply
  to administrators. Confirmed in practice by AC-010 of [[SPEC-0001-foundation-walking-skeleton]] (a direct push to
  `main` is refused) or by `gh api repos/nikarekhviashvili96-lab/market-intel/rulesets/27259134` once `gh` is logged in.

## Scheduled workflows

Read 2026-11-15.

- Source: <https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows> —
  "The `schedule` event can be delayed during periods of high loads of GitHub Actions workflow runs."; "The shortest
  interval you can run scheduled workflows is once every 5 minutes."; "Scheduled workflows will only run on the
  default branch."; "By default, scheduled workflows run in UTC."
- Source: <https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows> —
  "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred
  in 60 days."

## Notifications for failed workflow runs

Source: <https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs>, read
2026-11-15.

- With email or web notifications for Actions enabled, a user is notified when workflow runs they triggered complete;
  they can choose to be notified only when a run has failed. The page does not say which setting is the default.
- "Notifications for scheduled workflows are sent to the user who initially created the workflow." If another user
  changes the cron syntax, later notifications go to that user; if a disabled scheduled workflow is re-enabled, they
  go to the user who re-enabled it.
