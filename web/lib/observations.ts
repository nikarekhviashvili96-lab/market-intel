// Read a FRED observations answer into chart points (REQ-001 rules, the same as ingest/fred.py):
// "." is FRED's missing-value marker — no point, never 0; an error body, a non-numeric value, an empty series,
// a repeated or out-of-order date, an invalid date or a wrong count refuses the whole answer.
// T2 draws the T1 recording through this; from T7 the page reads stored observations instead.

export type Point = { date: string; value: number };
export type FredSeries = { points: Point[]; retrievedOn: string };

export const RANGES = ["1Y", "5Y", "10Y"] as const;
export type RangeKey = (typeof RANGES)[number];
const RANGE_YEARS: Record<RangeKey, number> = { "1Y": 1, "5Y": 5, "10Y": 10 };

const MISSING = ".";
const NUMBER = /^-?\d+(\.\d+)?$/;
const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})$/;

export class FredAnswerError extends Error {}

function isRecord(x: unknown): x is Record<string, unknown> {
  return typeof x === "object" && x !== null && !Array.isArray(x);
}

function checkDate(text: unknown, what: string): string {
  const m = typeof text === "string" ? ISO_DATE.exec(text) : null;
  if (!m) throw new FredAnswerError(`${what} has no valid date`);
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const back = new Date(Date.UTC(y, mo - 1, d));
  if (back.getUTCFullYear() !== y || back.getUTCMonth() !== mo - 1 || back.getUTCDate() !== d) {
    throw new FredAnswerError(`${what} has an invalid date ${String(text)}`);
  }
  return text as string;
}

export function parseFredAnswer(payload: unknown): FredSeries {
  if (!isRecord(payload)) throw new FredAnswerError("answer is not a JSON object");
  if ("error_code" in payload || "error_message" in payload) {
    throw new FredAnswerError(`FRED returned an error: ${payload.error_code} ${payload.error_message}`);
  }
  const rows = payload.observations;
  if (!Array.isArray(rows)) throw new FredAnswerError("answer has no observations list");
  if (rows.length === 0) throw new FredAnswerError("empty series: no observations");
  if (payload.count !== undefined && payload.count !== rows.length) {
    throw new FredAnswerError(`count says ${payload.count} observations, answer holds ${rows.length}`);
  }
  const retrievedOn = checkDate(payload.realtime_start, "the answer's retrieval date");

  const points: Point[] = [];
  let previous: string | null = null;
  rows.forEach((row: unknown, i: number) => {
    if (!isRecord(row)) throw new FredAnswerError(`observation ${i} is not an object`);
    const date = checkDate(row.date, `observation ${i}`);
    if (previous !== null && date <= previous) {
      throw new FredAnswerError(`${date === previous ? "repeated" : "out-of-order"} date ${date}`);
    }
    previous = date;
    if (row.value === MISSING) return;
    if (typeof row.value !== "string" || !NUMBER.test(row.value)) {
      throw new FredAnswerError(`non-numeric value on ${date}`);
    }
    points.push({ date, value: Number(row.value) });
  });
  if (points.length === 0) throw new FredAnswerError("empty series: every value is missing");
  return { points, retrievedOn };
}

/** The date `years` before `isoDate`; 29 February falls back to 28 February. */
function yearsBefore(isoDate: string, years: number): string {
  const [y, m, d] = isoDate.split("-").map(Number);
  const back = new Date(Date.UTC(y - years, m - 1, d));
  if (back.getUTCMonth() !== m - 1) back.setUTCDate(0);
  return back.toISOString().slice(0, 10);
}

/** The points within the range, counted back from the newest observation (points are oldest first). */
export function pointsInRange(points: Point[], range: RangeKey): Point[] {
  if (points.length === 0) return [];
  const cutoff = yearsBefore(points[points.length - 1].date, RANGE_YEARS[range]);
  return points.filter((p) => p.date > cutoff);
}
