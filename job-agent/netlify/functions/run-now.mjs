import { getStore } from "@netlify/blobs";
import { runPipeline } from "../../src/pipeline.js";

// On-demand refresh at /api/refresh. Runs the same work as the scheduled
// refresh-feed but HTTP-triggered, so a run never depends on the dashboard.
// Returns the run summary (counts + board errors) as JSON so you see what
// happened immediately.
//
// Optional lock: set a RUN_TOKEN env var in Netlify and this endpoint will
// then require ?token=<that value>. With no RUN_TOKEN set, it is open, which
// is fine for a personal feed since a run only recomputes the list.
export default async (req) => {
  const required = process.env.RUN_TOKEN;
  if (required) {
    const token = new URL(req.url).searchParams.get("token");
    if (token !== required) {
      return new Response(JSON.stringify({ error: "unauthorized" }), {
        status: 401,
        headers: { "content-type": "application/json" },
      });
    }
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
