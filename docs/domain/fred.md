---
id: fred
type: domain
title: FRED — terms of use, API, series DGS10, missing values
status: living
updated: 2026-11-15
related:
  - "[[SPEC-0001-foundation-walking-skeleton]]"
---

# FRED (Federal Reserve Bank of St. Louis)

Checked 2026-11-15 against the official pages linked under each fact. Re-verify before a source's sharing flag is
changed or before SPEC-0002 adds more FRED series.

## Terms of use

Source: <https://fred.stlouisfed.org/legal/> and <https://fred.stlouisfed.org/docs/api/terms_of_use.html>
(no last-updated date shown on either page).

- FRED serves data "for non-commercial, educational, and personal uses"; commercial use needs the Bank's prior
  written consent.
- Attribution is required for any FRED content: cite the data source and say the data was obtained from FRED.
- An application using the API must prominently display: "This product uses the FRED® API but is not endorsed or
  certified by the Federal Reserve Bank of St. Louis." An application built for other users must also link to the
  FRED Terms of Use and state that using the app means accepting them.
- Copyrighted third-party series carry the word "Copyright" in their notes; for "Copyrighted: Pre-approval
  required" series the data owner's permission is needed for anything beyond personal use.
- An API key is required (32-character lowercase alphanumeric); requests with an invalid key are blocked.
- No per-minute rate limit is published; the Bank may impose bandwidth or transaction limits at its discretion.
  An application may not replicate or replace FRED's essential user experience.

## Series DGS10

Source: <https://fred.stlouisfed.org/series/DGS10>, read 2026-11-15.

- Title: "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, Quoted on an Investment Basis".
- Units: Percent, Not Seasonally Adjusted. Frequency: Daily. Source: Board of Governors of the Federal Reserve
  System (US), release H.15 Selected Interest Rates.
- Suggested citation: "Board of Governors of the Federal Reserve System (US), Market Yield on U.S. Treasury
  Securities at 10-Year Constant Maturity, Quoted on an Investment Basis [DGS10], retrieved from FRED, Federal
  Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/DGS10".
- **Sharing status — conflicting, not resolved.** The page shows "Data in this graph are copyrighted. Please review
  the copyright information in the series notes before sharing.", while the series tags read "Public Domain:
  Citation Requested" and the notes contain no "Copyright" line. Until this is resolved (H.15 terms or the data
  source's answer), the source stays **not shareable** with viewers.

## API: observations

Source: <https://fred.stlouisfed.org/docs/api/fred/series_observations.html>.

- `limit` accepts 1–100000 (default 100000) — 10 years of a daily series fits in one request.
- `realtime_start` / `realtime_end` (default today) and `vintage_dates` select data as it stood on a date (ALFRED
  vintages) — usable for point-in-time revisions.
- **Missing observations are returned as the value `"."`** (e.g. US holidays). Source: the owner (2026-11-15) and
  secondary sources; FRED's own help page uses a holiday (2000-07-04) as its example of a missing daily value and its
  blog says FRED does not impute missing values. The official observations page does not state the marker — it is
  confirmed when the first recorded fixture is captured (stage 4). Rule: `"."` is stored as no observation (skipped
  or null), never as 0.
