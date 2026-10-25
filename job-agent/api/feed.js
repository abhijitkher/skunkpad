import { readJSON } from "../src/store.js";

// Serves the latest stored feed at /api/feed.
export async function GET() {
  const feed = (await readJSON("job-agent/feed.json")) || { jobs: [], generatedAt: null };
  return new Response(JSON.stringify(feed), {
    headers: { "content-type": "application/json", "cache-control": "public, max-age=300" },
  });
}
