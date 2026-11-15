---
id: supabase
type: domain
title: Supabase — connecting to Postgres (direct vs. shared pooler, custom roles)
status: living
updated: 2026-11-15
related:
  - "[[ADR-0101-data-and-access-model]]"
  - "[[supabase-free-plan]]"
---

# Supabase — connecting to Postgres

Source: <https://supabase.com/docs/guides/database/connecting-to-postgres>, read 2026-11-15 (no last-updated date
shown). Plan limits and the inactivity pause: [[supabase-free-plan]].

## Direct connection

- "Direct connections are on IPv6, or on IPv4 if the project has the IPv4 add-on." The add-on is available on the Pro
  plan and above — so on the Free plan a direct connection is IPv6-only.

## Shared pooler (Supavisor)

- The shared pooler is the option "when you connect from an IPv4-only network".
- "The shared pooler is IPv4-only on every plan, in both session and transaction mode."
- Session mode uses port `5432`. The username is `postgres.[PROJECT-REF]` for the default role instead of plain
  `postgres`. Copy the host from the project's Connect dialog; don't build it from the region, because "`[INDEX]` in
  the shared pooler host is a pooler cluster index".
- **Custom roles:** "If you connect as a custom role through the shared pooler, the username is
  `[ROLE].[PROJECT-REF]`." For this project the daily job logs in as `ingest_writer.[PROJECT-REF]` through the session
  pooler ([[ADR-0101-data-and-access-model]]).

## Not yet proven live

The docs say a custom role can log in through the shared pooler. The live proof is the first database task of
PLAN-0001: from a GitHub-hosted runner, `ingest_writer` connects through the session pooler, inserts one row into a
test table, and its update and delete attempts are refused.
