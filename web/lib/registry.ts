// The series registry entry for DGS10 (REQ-002). Every label, unit, description and credit line on the page comes
// from here, never from the page itself. T2 stand-in: from T7 the page reads the same fields from the database's
// registry (ADR-0101); the texts below are the ones recorded in docs/domain/fred.md (2026-11-15).

export type SeriesEntry = {
  id: string;
  /** FRED's full series title. */
  title: string;
  /** The short heading shown above the chart. */
  shortTitle: string;
  units: string;
  unitSymbol: string;
  frequency: string;
  description: string;
  creditLine: string;
  sourceUrl: string;
};

export const DGS10: SeriesEntry = {
  id: "DGS10",
  title:
    "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity, Quoted on an Investment Basis",
  shortTitle: "US 10-Year Treasury Yield",
  units: "Percent",
  unitSymbol: "%",
  frequency: "Daily",
  description:
    "Daily yield, not seasonally adjusted, from the Federal Reserve's H.15 Selected Interest Rates release.",
  creditLine:
    "Source: U.S. Treasury via Federal Reserve H.15; retrieved from FRED, Federal Reserve Bank of St. Louis",
  sourceUrl: "https://fred.stlouisfed.org/series/DGS10",
};

// FRED's API terms (docs/domain/fred.md): the notice, a link to the Terms of Use and the acceptance statement.
export const FRED_API_NOTICE =
  "This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.";
export const FRED_TERMS_URL = "https://fred.stlouisfed.org/docs/api/terms_of_use.html";
export const TERMS_ACCEPTANCE = "By using this site you accept the";
