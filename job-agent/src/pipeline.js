import { readFile } from "node:fs/promises";
import { fetchAll } from "./sources.js";
import { buildResumeTerms, passesFilters, scoreJob } from "./score.js";

const readJson = async (path) => JSON.parse(await readFile(new URL(path, import.meta.url), "utf8"));

// Resume text comes from the RESUME_TEXT env var (use this on Netlify, the file
// is gitignored so it is never deployed), then resume.txt, then the example.
async function loadResume() {
  if (process.env.RESUME_TEXT) return process.env.RESUME_TEXT;
  for (const f of ["../resume.txt", "../resume.example.txt"]) {
    try {
      return await readFile(new URL(f, import.meta.url), "utf8");
    } catch {}
  }
  return "";
}

// previousSeen: { [jobId]: firstSeenISO } so each run can flag what is new.
export async function runPipeline(previousSeen = {}) {
  const [profile, { companies }, resume] = await Promise.all([
    readJson("../profile.json"),
    readJson("../companies.json"),
    loadResume(),
  ]);

  const resumeTerms = buildResumeTerms(resume);
  const { jobs, errors } = await fetchAll(companies);
  const now = new Date().toISOString();
  const seen = { ...previousSeen };

  const ranked = jobs
    .filter((j) => passesFilters(j, profile))
    .map((j) => {
      const { score, why } = scoreJob(j, profile, resumeTerms);
      if (!seen[j.id]) seen[j.id] = now;
      return {
        id: j.id,
        company: j.company,
        title: j.title,
        location: j.location,
        url: j.url,
        comp: j.comp,
        postedAt: j.postedAt,
        firstSeen: seen[j.id],
        isNew: seen[j.id] === now,
        score,
        why,
      };
    })
    .filter((j) => j.score >= profile.min_score_to_show)
    .sort((a, b) => b.score - a.score);

  return {
    feed: {
      generatedAt: now,
      totalFetched: jobs.length,
      shown: ranked.length,
      resumeLoaded: resume.length > 0,
      errors,
      jobs: ranked,
    },
    seen,
  };
}
