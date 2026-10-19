import { getStore } from "@netlify/blobs";
import { runPipeline } from "../../src/pipeline.js";

// On-demand refresh at /api/refresh?token=RUN_TOKEN. Same work as the scheduled
// refresh-feed, but HTTP-triggered so a run does not depend on the dashboard.
// Token-gated so it is not wide open. Returns the run summary (counts + the
// board errors) as JSON so you can see immediately what happened.
export default async (req) => {
  const token = new URL(req.url).searchParams.get("token");
  if (!process.env.RUN_TOKEN || token !== process.env.RUN_TOKEN) {
    return new Response(JSON.stringify({ error: "unauthorized" }), {
      status: 401,
      headers: { "content-type": "application/json" },
    });
  }
  const store = getStore("job-agent");
  const previousSeen = (await store.get("seen", { type: "json" })) || {};
  const { feed, seen } = await runPipeline(previousSeen);
  await store.setJSON("feed", feed);
  await store.setJSON("seen", seen);
  return new Response(
    JSON.stringify(
      {
        ok: true,
        generatedAt: feed.generatedAt,
        totalFetched: feed.totalFetched,
        shown: feed.shown,
        errors: feed.errors,
      },
      null,
      2
    ),
    { headers: { "content-type": "application/json" } }
  );
};

export const config = { path: "/api/refresh" };
