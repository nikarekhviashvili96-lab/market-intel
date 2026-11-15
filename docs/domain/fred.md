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
- **FRED's own signals conflict.** The page shows "Data in this graph are copyrighted. Please review the copyright
  information in the series notes before sharing.", while the series tags read "Public Domain: Citation Requested"
  and the notes contain no "Copyright" line.

## Origin of DGS10: Federal Reserve H.15 and U.S. Treasury

Checked 2026-11-15 on the official pages, at the owner's request.

- Federal Reserve Board website terms, <https://www.federalreserve.gov/disclaimer.htm> (last update 2024-08-02):
  "Unless otherwise indicated, information on Board's website is in the public domain and may be copied and
  distributed without permission. Please cite to the Board as the source of the information." Material identified
  as belonging to a non-Board source (e.g. under copyright) needs that source's permission: "Permission to use
  copyrighted materials must be obtained from the original source and cannot be obtained from the Board."
- H.15 release page, <https://www.federalreserve.gov/releases/h15/>: no copyright notice. Footnote for Treasury
  nominal constant maturities: "Source: U.S. Treasury." Yields "are interpolated by the U.S. Treasury from the daily
  yield curve"; market yields come from "composites of quotations obtained by the Federal Reserve Bank of New York."
- **Not verified:** the U.S. Treasury's own reuse terms for its yield-curve data — the official home.treasury.gov
  policy page was not found (the URL tried returned 404). A different Treasury site, Fiscal Data
  (<https://fiscaldata.treasury.gov/about-us/>), allows commercial and non-commercial reuse, but that is a different
  dataset and is only a secondary indication.
- The Board's terms allow redistribution with credit to the Board; the series is credited to the U.S. Treasury,
  whose own site terms were not found on 2026-11-15.

## Sharing decision for DGS10 — shareable

**Owner's decision, 2026-11-15:** `DGS10` is flagged **shareable** with invited viewers. Rationale, as the owner
gave it (source: owner — the legal reading is the owner's, not verified by the agent):

- U.S. Treasury data is a work of the U.S. federal government and is not subject to copyright under
  17 U.S.C. §105.
- The Federal Reserve Board's terms allow copying and distribution with citation (above).
- Use is non-commercial, with at most 5 invited viewers ([[vercel-hobby]]).

Required on the chart (owner, 2026-11-15):

- Credit line: "Source: U.S. Treasury via Federal Reserve H.15; retrieved from FRED, Federal Reserve Bank of
  St. Louis".
- FRED's API notice: "This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank
  of St. Louis.", a link to FRED's Terms of Use, and the statement that using the site means accepting them.

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
