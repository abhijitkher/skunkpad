// Resume-match scorer. Heuristic, not ML: treat the score as a sort order.
//
// Score (0-100):
//   30  title is one of the target titles
//   30  how many boost keywords (trust, identity, fraud...) appear in the posting
//   30  overlap between distinctive resume terms and the posting text
//   10  location fits

const STOP = new Set(
  "the a an and or of to in for with on at by from as is are was were be been this that it its you your we our they their will can may such not but if then than into over per via using use used work working team teams role roles experience years year product manager management".split(" ")
);

const tokenize = (text) =>
  (text.toLowerCase().match(/[a-z][a-z0-9+#.-]{2,}/g) || []).filter((t) => !STOP.has(t));

export function buildResumeTerms(resumeText, limit = 120) {
  const counts = new Map();
  for (const t of tokenize(resumeText)) counts.set(t, (counts.get(t) || 0) + 1);
  return new Set(
    [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, limit).map(([t]) => t)
  );
}

const has = (haystack, needle) => haystack.includes(needle.toLowerCase());

export function passesFilters(job, profile) {
  const title = job.title.toLowerCase();
  if (profile.titles_excluded.some((x) => has(title, x))) return false;
  if (!profile.titles_wanted.some((x) => has(title, x))) return false;
  const loc = (job.location || "").toLowerCase();
  if (!loc) return true; // unknown location: keep, let the human decide
  return profile.locations_wanted.some((x) => has(loc, x));
}

export function scoreJob(job, profile, resumeTerms) {
  const title = job.title.toLowerCase();
  const text = `${job.title} ${job.description}`.toLowerCase();

  const titleScore = profile.titles_wanted.some((x) => has(title, x)) ? 30 : 0;

  const boostHits = profile.keywords_boost.filter((k) => has(text, k)).length;
  const boostScore = Math.min(30, Math.round((boostHits / 6) * 30));

  const postingTerms = new Set(tokenize(text));
  let overlap = 0;
  for (const t of resumeTerms) if (postingTerms.has(t)) overlap++;
  const overlapScore = Math.min(30, Math.round((overlap / 40) * 30));

  const loc = (job.location || "").toLowerCase();
  const locScore = !loc || profile.locations_wanted.some((x) => has(loc, x)) ? 10 : 0;

  return {
    score: titleScore + boostScore + overlapScore + locScore,
    why: { title: titleScore, keywords: boostScore, resume: overlapScore, location: locScore },
  };
}
