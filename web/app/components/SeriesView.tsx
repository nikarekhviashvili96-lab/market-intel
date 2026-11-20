"use client";

// One series: latest value and date, 1Y / 5Y / 10Y buttons (1Y first), the chart, and the registry's units,
// description and credit line with FRED's notice and terms (REQ-004). Every word comes from the registry entry.
import { useState } from "react";
import SeriesChart from "./SeriesChart";
import { formatDate, formatValue } from "@/lib/format";
import { pointsInRange, RANGES, type Point, type RangeKey } from "@/lib/observations";
import { FRED_API_NOTICE, FRED_TERMS_URL, TERMS_ACCEPTANCE, type SeriesEntry } from "@/lib/registry";

type Props = { entry: SeriesEntry; points: Point[]; retrievedOn: string };

export default function SeriesView({ entry, points, retrievedOn }: Props) {
  const [range, setRange] = useState<RangeKey>("1Y");
  const latest = points[points.length - 1];
  const shown = pointsInRange(points, range);

  return (
    <article className="flex flex-col gap-4">
      <header className="flex flex-col gap-1">
        <h1 className="text-lg font-semibold">{entry.shortTitle}</h1>
        <p className="text-sm text-muted">{entry.title}</p>
        <p className="mt-2 flex items-baseline gap-3">
          <span data-testid="latest-value" className="text-4xl font-semibold tabular-nums">
            {formatValue(latest.value, entry.unitSymbol)}
          </span>
          <span data-testid="latest-date" className="text-sm text-muted">
            {formatDate(latest.date)}
          </span>
        </p>
      </header>

      <div role="group" aria-label="Chart range" className="flex gap-2">
        {RANGES.map((key) => (
          <button
            key={key}
            type="button"
            aria-pressed={range === key}
            onClick={() => setRange(key)}
            className="min-h-11 min-w-11 rounded-md border border-line px-3 text-sm font-medium aria-pressed:bg-accent aria-pressed:text-on-accent aria-pressed:border-accent"
          >
            {key}
          </button>
        ))}
      </div>

      <SeriesChart points={shown} unitSymbol={entry.unitSymbol} />

      <section className="flex flex-col gap-2 text-sm">
        <p>
          Units: {entry.units} · {entry.frequency}
        </p>
        <p className="text-muted">{entry.description}</p>
      </section>

      <footer className="flex flex-col gap-2 border-t border-line pt-4 text-xs text-muted">
        <p>
          {entry.creditLine}. Retrieved {formatDate(retrievedOn)}.
        </p>
        <p>{FRED_API_NOTICE}</p>
        <p>
          {TERMS_ACCEPTANCE}{" "}
          <a href={FRED_TERMS_URL} className="underline" rel="noopener noreferrer">
            FRED Terms of Use
          </a>
          .
        </p>
      </footer>
    </article>
  );
}
