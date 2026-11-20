// REQ-001, AC-001 (fixture side): "." is no observation, never 0; a broken answer is refused.
// The same rules as ingest/fred.py, applied to the T1 recording the page draws in T2.
import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { FredAnswerError, parseFredAnswer, pointsInRange } from "@/lib/observations";

const fixturePath = path.resolve(__dirname, "../../tests/fixtures/fred_dgs10.json");
const recording = JSON.parse(readFileSync(fixturePath, "utf-8"));

function answer(rows: Array<{ date: string; value: string }>) {
  return { realtime_start: "2026-11-15", count: rows.length, observations: rows };
}

describe("the FRED recording", () => {
  const series = parseFredAnswer(recording);

  it("keeps every numeric value and drops every missing-value date", () => {
    const rows = recording.observations as Array<{ date: string; value: string }>;
    const numeric = rows.filter((r) => r.value !== ".");
    const missing = rows.filter((r) => r.value === ".");
    expect(missing.length).toBeGreaterThan(0);
    expect(series.points).toHaveLength(numeric.length);
    const dates = new Set(series.points.map((p) => p.date));
    for (const r of missing) expect(dates.has(r.date)).toBe(false);
    numeric.forEach((r, i) => {
      expect(series.points[i]).toEqual({ date: r.date, value: Number(r.value) });
    });
  });

  it("has no point on 4 July 2025 and no zero anywhere", () => {
    expect(series.points.find((p) => p.date === "2025-07-04")).toBeUndefined();
    expect(series.points.some((p) => p.value === 0)).toBe(false);
  });

  it("reads the retrieval date of the recording", () => {
    expect(series.retrievedOn).toBe("2026-11-15");
  });
});

describe("a broken answer is refused", () => {
  it.each([
    ["an error body", { error_code: 400, error_message: "Bad Request" }],
    ["an empty series", answer([])],
    ["a non-numeric value", answer([{ date: "2026-11-13", value: "n/a" }])],
    ["a repeated date", answer([{ date: "2026-11-13", value: "4.1" }, { date: "2026-11-13", value: "4.2" }])],
    ["an out-of-order date", answer([{ date: "2026-11-13", value: "4.1" }, { date: "2026-11-12", value: "4.2" }])],
    ["an invalid date", answer([{ date: "2026-02-30", value: "4.1" }])],
    ["only missing values", answer([{ date: "2026-11-13", value: "." }])],
    ["a count that does not match", { ...answer([{ date: "2026-11-13", value: "4.1" }]), count: 2 }],
  ])("%s", (_name, payload) => {
    expect(() => parseFredAnswer(payload)).toThrow(FredAnswerError);
  });
});

describe("range buttons", () => {
  const points = [
    { date: "2015-11-13", value: 1 },
    { date: "2021-11-12", value: 2 },
    { date: "2021-11-14", value: 3 },
    { date: "2025-11-13", value: 4 },
    { date: "2025-11-14", value: 5 },
    { date: "2026-11-13", value: 6 },
  ];

  it("1Y keeps the last year before the newest observation", () => {
    expect(pointsInRange(points, "1Y").map((p) => p.value)).toEqual([5, 6]);
  });

  it("5Y keeps the last five years", () => {
    expect(pointsInRange(points, "5Y").map((p) => p.value)).toEqual([3, 4, 5, 6]);
  });

  it("10Y keeps the last ten years", () => {
    expect(pointsInRange(points, "10Y").map((p) => p.value)).toEqual([2, 3, 4, 5, 6]);
  });

  it("handles 29 February", () => {
    const leap = [
      { date: "2023-02-28", value: 1 },
      { date: "2023-03-01", value: 2 },
      { date: "2024-02-29", value: 3 },
    ];
    expect(pointsInRange(leap, "1Y").map((p) => p.value)).toEqual([2, 3]);
  });
});
