import { getStore } from "@netlify/blobs";

// Serves the latest feed at /api/feed (see netlify.toml).
export default async () => {
  const feed = await getStore("job-agent").get("feed", { type: "json" });
  return new Response(JSON.stringify(feed || { jobs: [], generatedAt: null }), {
    headers: { "content-type": "application/json", "cache-control": "public, max-age=300" },
  });
};

export const config = { path: "/api/feed" };
