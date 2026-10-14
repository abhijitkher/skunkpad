import { getStore } from "@netlify/blobs";
import { runPipeline } from "../../src/pipeline.js";

// Scheduled function. Weekdays at 14:00 UTC (7am Pacific during daylight time).
// Writes the ranked feed into Netlify Blobs; netlify/functions/feed.mjs serves it.
export default async () => {
  const store = getStore("job-agent");
  const previousSeen = (await store.get("seen", { type: "json" })) || {};
  const { feed, seen } = await runPipeline(previousSeen);
  await store.setJSON("feed", feed);
  await store.setJSON("seen", seen);
  console.log(`feed updated: ${feed.shown} shown of ${feed.totalFetched} fetched, ${feed.errors.length} board errors`);
};

export const config = { schedule: "0 14 * * 1-5" };
