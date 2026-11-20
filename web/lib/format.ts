// en-US formatting for every date and number the product shows (REQ-009). Dates are calendar dates
// ("YYYY-MM-DD") and are formatted in UTC so the machine's time zone can never shift the day.

const dateFormat = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
  year: "numeric",
  timeZone: "UTC",
});
const axisFormat = new Intl.DateTimeFormat("en-US", { month: "short", year: "numeric", timeZone: "UTC" });
const valueFormat = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function toUtc(isoDate: string): Date {
  const [y, m, d] = isoDate.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}

/** "2026-11-14" → "Nov 14, 2026" */
export function formatDate(isoDate: string): string {
  return dateFormat.format(toUtc(isoDate));
}

/** "2026-11-14" → "Nov 2026" */
export function formatAxisDate(isoDate: string): string {
  return axisFormat.format(toUtc(isoDate));
}

/** 4.1, "%" → "4.10%" */
export function formatValue(value: number, unitSymbol: string): string {
  return `${valueFormat.format(value)}${unitSymbol}`;
}
