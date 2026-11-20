// T2 only: the page draws the T1 recording of FRED's answer (tests/fixtures/fred_dgs10.json). Read on the server;
// from T7 the page reads the database instead and this file goes (PLAN-0001 T2, T7).
import { readFileSync } from "node:fs";
import path from "node:path";
import { parseFredAnswer, type FredSeries } from "./observations";

export function loadFixtureSeries(): FredSeries {
  // `npm --prefix web run …` runs with web/ as the working directory.
  const file = path.join(process.cwd(), "..", "tests", "fixtures", "fred_dgs10.json");
  return parseFredAnswer(JSON.parse(readFileSync(file, "utf-8")));
}
