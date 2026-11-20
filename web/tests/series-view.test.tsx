// REQ-002 / REQ-004 / REQ-009, AC-004 and AC-006 (unit side): the page's words come from the registry,
// FRED's notice and terms are shown, 1Y is the default range and the text is English only.
import { readFileSync } from "node:fs";
import path from "node:path";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import SeriesView from "@/app/components/SeriesView";
import { parseFredAnswer } from "@/lib/observations";
import { DGS10, FRED_API_NOTICE, FRED_TERMS_URL, TERMS_ACCEPTANCE } from "@/lib/registry";

const recording = JSON.parse(
  readFileSync(path.resolve(__dirname, "../../tests/fixtures/fred_dgs10.json"), "utf-8"),
);
const series = parseFredAnswer(recording);
// Georgian (both blocks named in AC-004), Cyrillic, Greek, Arabic, CJK.
const NON_LATIN = /[Ⴀ-ჿᲐ-ᲿЀ-ӿͰ-Ͽ؀-ۿ一-鿿]/;

afterEach(cleanup);

function renderView() {
  return render(<SeriesView entry={DGS10} points={series.points} retrievedOn={series.retrievedOn} />);
}

describe("the chart page", () => {
  it("shows the credit line from the registry with its retrieval date", () => {
    renderView();
    expect(DGS10.creditLine).toBe(
      "Source: U.S. Treasury via Federal Reserve H.15; retrieved from FRED, Federal Reserve Bank of St. Louis",
    );
    expect(screen.getByText(DGS10.creditLine, { exact: false })).toBeTruthy();
    expect(screen.getByText("Retrieved Nov 15, 2026", { exact: false })).toBeTruthy();
  });

  it("shows FRED's API notice, the Terms of Use link and the acceptance sentence", () => {
    renderView();
    expect(screen.getByText(FRED_API_NOTICE)).toBeTruthy();
    const link = screen.getByRole("link", { name: "FRED Terms of Use" });
    expect(link.getAttribute("href")).toBe(FRED_TERMS_URL);
    expect(screen.getByText(TERMS_ACCEPTANCE, { exact: false })).toBeTruthy();
  });

  it("takes title, units and description from the registry", () => {
    renderView();
    expect(screen.getByRole("heading", { name: DGS10.shortTitle })).toBeTruthy();
    expect(screen.getByText(DGS10.title)).toBeTruthy();
    expect(screen.getByText(`Units: ${DGS10.units}`, { exact: false })).toBeTruthy();
    expect(screen.getByText(DGS10.description)).toBeTruthy();
  });

  it("shows the latest value and its date in en-US form", () => {
    renderView();
    const last = series.points[series.points.length - 1];
    expect(screen.getByTestId("latest-value").textContent).toBe(`${last.value.toFixed(2)}%`);
    // The recording's newest row is 2026-11-12 (11 Nov, Veterans Day, is ".").
    expect(last).toEqual({ date: "2026-11-12", value: 5.1 });
    expect(screen.getByTestId("latest-date").textContent).toBe("Nov 12, 2026");
  });

  it("starts on 1Y and switches range on tap", () => {
    renderView();
    const pressed = () => screen.getAllByRole("button", { pressed: true }).map((b) => b.textContent);
    expect(pressed()).toEqual(["1Y"]);
    fireEvent.click(screen.getByRole("button", { name: "5Y" }));
    expect(pressed()).toEqual(["5Y"]);
    fireEvent.click(screen.getByRole("button", { name: "10Y" }));
    expect(pressed()).toEqual(["10Y"]);
  });

  it("holds no letter from a non-Latin script", () => {
    const { container } = renderView();
    expect(container.textContent ?? "").not.toMatch(NON_LATIN);
  });
});
