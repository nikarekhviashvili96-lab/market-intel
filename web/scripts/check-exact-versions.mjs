// ADR-0100: every npm version is exact. `web/.npmrc` (save-exact=true) cannot be written by the agent — the
// harness treats .npmrc as a possible secrets file — so this check holds the rule instead: any range in
// package.json (^, ~, *, x, >, <, ||, a tag such as "latest") fails `npm run lint`.
import { readFileSync } from "node:fs";

const pkg = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf-8"));
const EXACT = /^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$/;
const bad = [];
for (const field of ["dependencies", "devDependencies", "optionalDependencies", "peerDependencies"]) {
  for (const [name, version] of Object.entries(pkg[field] ?? {})) {
    if (!EXACT.test(version)) bad.push(`${field}: ${name}@${version}`);
  }
}
if (bad.length) {
  console.error(`not an exact version (ADR-0100):\n  ${bad.join("\n  ")}`);
  process.exit(1);
}
console.log("exact versions: ok");
