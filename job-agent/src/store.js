// Tiny JSON store on Vercel Blob (private). Needs BLOB_READ_WRITE_TOKEN, which
// Vercel sets automatically when a Blob store is connected to the project.
import { get, put } from "@vercel/blob";

export async function readJSON(pathname, fallback = null) {
  try {
    const res = await get(pathname, { access: "private", useCache: false });
    if (!res || res.statusCode !== 200) return fallback;
    return JSON.parse(await new Response(res.stream).text());
  } catch {
    return fallback;
  }
}

export async function writeJSON(pathname, value) {
  await put(pathname, JSON.stringify(value), {
    access: "private",
    contentType: "application/json",
    addRandomSuffix: false,
    allowOverwrite: true,
  });
}

// Runs the pipeline against stored state and saves the result.
export async function refreshFeed(runPipeline) {
  const previousSeen = await readJSON("job-agent/seen.json", {});
  const { feed, seen } = await runPipeline(previousSeen);
  await writeJSON("job-agent/feed.json", feed);
  await writeJSON("job-agent/seen.json", seen);
  return feed;
}
