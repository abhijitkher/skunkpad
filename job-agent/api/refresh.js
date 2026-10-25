import { runPipeline } from "../src/pipeline.js";
import { refreshFeed } from "../src/store.js";

export const config = { maxDuration: 60 };

// Refresh endpoint, used by the Vercel Cron schedule (vercel.json) and by hand.
// Vercel Cron sends "Authorization: Bearer $CRON_SECRET" when CRON_SECRET is set.
// Manual runs: /api/refresh?token=<RUN_TOKEN> (when RUN_TOKEN is set).
// With neither variable set the endpoint is open, which is fine for a personal
// feed since a run only recomputes the list.
export async function GET(request) {
  const cronSecret = process.env.CRON_SECRET;
  const runToken = process.env.RUN_TOKEN;
  if (cronSecret || runToken) {
    const viaCron = cronSecret && request.headers.get("authorization") === `Bearer ${cronSecret}`;
    const viaToken = runToken && new URL(request.url).searchParams.get("token") === runToken;
    if (!viaCron && !viaToken) {
      return Response.json({ error: "unauthorized" }, { status: 401 });
    }
  }
  const feed = await refreshFeed(runPipeline);
  console.log(`feed updated: ${feed.shown} shown of ${feed.totalFetched} fetched, ${feed.errors.length} board errors`);
  return Response.json({
    ok: true,
    generatedAt: feed.generatedAt,
    totalFetched: feed.totalFetched,
    shown: feed.shown,
    errors: feed.errors,
  });
}
