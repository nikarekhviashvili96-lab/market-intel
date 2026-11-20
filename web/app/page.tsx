import SeriesView from "./components/SeriesView";
import { loadFixtureSeries } from "@/lib/fixture";
import { DGS10 } from "@/lib/registry";

export default function Home() {
  const series = loadFixtureSeries();
  return (
    <main>
      <SeriesView entry={DGS10} points={series.points} retrievedOn={series.retrievedOn} />
    </main>
  );
}
