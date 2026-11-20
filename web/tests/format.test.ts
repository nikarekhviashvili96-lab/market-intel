// REQ-009, AC-004: every date and number on the page is formatted for en-US.
import { describe, expect, it } from "vitest";
import { formatAxisDate, formatDate, formatValue } from "@/lib/format";

describe("en-US formatting", () => {
  it("writes a date like Nov 14, 2026", () => {
    expect(formatDate("2026-11-14")).toBe("Nov 14, 2026");
    expect(formatDate("2016-01-04")).toBe("Jan 4, 2016");
  });

  it("does not shift the day by the machine's time zone", () => {
    expect(formatDate("2026-01-01")).toBe("Jan 1, 2026");
    expect(formatDate("2025-12-31")).toBe("Dec 31, 2025");
  });

  it("writes axis dates as month and year", () => {
    expect(formatAxisDate("2026-11-14")).toBe("Nov 2026");
  });

  it("writes values with two decimals, en-US separators and the unit symbol", () => {
    expect(formatValue(4.1, "%")).toBe("4.10%");
    expect(formatValue(1234.5, "")).toBe("1,234.50");
    expect(formatValue(-0.25, "%")).toBe("-0.25%");
  });
});
