// TEMPORARY: finds working ATS slugs for companies that 404. Delete after use.
import companiesData from "../companies.json" with { type: "json" };

export const config = { maxDuration: 60 };

const FAILED = ["Persona","AI21 Labs","Aleph Alpha","Twelve Labs","Contextual AI","Goodfire","Writer","Moveworks","Cognigy","Cursor (Anysphere)","Windsurf","Hebbia","Pallet","Ironclad","HeyGen","Bolt.new (StackBlitz)","Cline","11x","Forethought","Anyscale","Replicate","Together AI","Weights & Biases","Pinecone","Groq","Cerebras","Lambda","Crusoe","Hugging Face","Modular","Helicone","Braintrust","fal","Cleanlab","Unstructured","Boston Dynamics","Sanctuary AI","Covariant","Genesis AI","Bedrock Robotics","Skild AI","Wayve","Applied Intuition","Waabi","Aurora Innovation","Sunday Robotics","Zipline"];
const EXTRA = {
  "Persona":["withpersona","persona-identities"],"Cursor (Anysphere)":["anysphere","cursor"],"Windsurf":["codeium","windsurf"],
  "Bolt.new (StackBlitz)":["stackblitz","bolt"],"Lambda":["lambda","lambdalabs","lambda-labs"],"Weights & Biases":["wandb","weightsandbiases","weights-biases"],
  "Together AI":["togetherai","together-ai","together"],"Cerebras":["cerebrassystems","cerebras-systems"],"Pinecone":["pinecone-io","pineconeio","pinecone"],
  "Unstructured":["unstructuredio","unstructured-io"],"Zipline":["flyzipline","zipline"],"fal":["fal-ai","falai","fal"],"11x":["11x-ai","11xai","elevenx"],
  "Skild AI":["skildai","skild-ai"],"Sunday Robotics":["sunday","sunday-robotics"],"Aurora Innovation":["aurora","aurora-innovation","aurorainnovation"],
  "Crusoe":["crusoe-energy","crusoeenergy","crusoe"],"Modular":["modularml","modular-inc","modular"],"Braintrust":["braintrust","braintrustdata","braintrust-data"],
  "AI21 Labs":["ai21","ai21labs","ai21-labs"],"Aleph Alpha":["aleph-alpha","alephalpha"],"Sanctuary AI":["sanctuary","sanctuary-ai"],
  "Genesis AI":["genesis-ai","genesisai","genesis"],"Bedrock Robotics":["bedrock","bedrock-robotics","bedrockrobotics"],
  "Twelve Labs":["twelvelabs","twelve-labs"],"Goodfire":["goodfire","goodfire-ai"],"Pallet":["pallet","pallet-ai","palletai"],
  "Writer":["writer","writerinc","writer-inc"],"Hugging Face":["huggingface","hugging-face"],"Applied Intuition":["appliedintuition","applied-intuition"],
};
const slugify = (n) => n.toLowerCase().replace(/\(.*?\)/g, "").trim();
const sep = (n, s) => slugify(n).replace(/[^a-z0-9]+/g, s).replace(new RegExp(`^${s}|${s}$`, "g"), "");
const ATS = {
  greenhouse: (s) => `https://boards-api.greenhouse.io/v1/boards/${s}/jobs`,
  lever: (s) => `https://api.lever.co/v0/postings/${s}?mode=json`,
  ashby: (s) => `https://api.ashbyhq.com/posting-api/job-board/${s}`,
};
async function probe(source, slug) {
  try {
    const c = new AbortController(); const t = setTimeout(() => c.abort(), 6000);
    const r = await fetch(ATS[source](slug), { signal: c.signal }); clearTimeout(t);
    if (!r.ok) return null;
    const d = await r.json();
    const n = Array.isArray(d) ? d.length : (d.jobs || []).length;
    return n;
  } catch { return null; }
}
export async function GET() {
  const out = await Promise.all(FAILED.map(async (name) => {
    const slugs = [...new Set([...(EXTRA[name] || []), sep(name, ""), sep(name, "-"), sep(name, "") + "ai", sep(name, "") + "hq"])];
    const hits = [];
    await Promise.all(slugs.flatMap((s) => Object.keys(ATS).map(async (src) => {
      const n = await probe(src, s); if (n !== null) hits.push({ source: src, slug: s, jobs: n });
    })));
    return { name, hits };
  }));
  return Response.json(out);
}
