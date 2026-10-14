// Runs the pipeline once locally and writes public/feed.json for previewing.
import { writeFile } from "node:fs/promises";
import { runPipeline } from "../src/pipeline.js";

const { feed } = await runPipeline();
await writeFile(new URL("../public/feed.json", import.meta.url), JSON.stringify(feed, null, 2));
console.log(`wrote public/feed.json: ${feed.shown} shown of ${feed.totalFetched} fetched`);
for (const e of feed.errors) console.log(`  board error: ${e.company}: ${e.error}`);
