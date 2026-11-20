"use client";

// The line chart (Recharts, SVG — ADR-0100). Missing days simply have no point: the line joins the neighbouring
// days and never drops to 0 (AC-001). Colours come from the theme's CSS variables, so dark mode follows.
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatAxisDate, formatDate, formatValue } from "@/lib/format";
import type { Point } from "@/lib/observations";

type Props = { points: Point[]; unitSymbol: string };

export default function SeriesChart({ points, unitSymbol }: Props) {
  return (
    <div className="h-60 w-full" data-testid="series-chart">
      <ResponsiveContainer width="100%" height="100%" initialDimension={{ width: 343, height: 240 }}>
        <LineChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="var(--line)" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatAxisDate}
            minTickGap={48}
            tick={{ fill: "var(--muted)", fontSize: 12 }}
            stroke="var(--line)"
          />
          <YAxis
            domain={["auto", "auto"]}
            width={48}
            tickFormatter={(v: number) => formatValue(v, unitSymbol)}
            tick={{ fill: "var(--muted)", fontSize: 12 }}
            stroke="var(--line)"
          />
          <Tooltip
            labelFormatter={(label) => formatDate(String(label))}
            formatter={(v) => [formatValue(Number(v), unitSymbol), "Yield"]}
            contentStyle={{ background: "var(--background)", borderColor: "var(--line)", color: "var(--foreground)" }}
          />
          <Line
            type="linear"
            dataKey="value"
            stroke="var(--accent)"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
