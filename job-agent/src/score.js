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

// Best-effort work-arrangement classifier from the posting's location + text.
// Conservative by design: returns remote/hybrid/onsite only when the text says
// so, else "unknown". hybridDays is set only when an in-office cadence is
// explicitly stated near an office/hybrid cue; it is never guessed.
const WORD_NUM = { one: 1, two: 2, three: 3, four: 4, five: 5 };

function extractHybridDays(text) {
  const num = "(\\d+|one|two|three|four|five)";
  const office = "(?:office|in[\\s-]*person|on[\\s-]*site|onsite|hybrid)";
  const res = [
    new RegExp(`${num}\\s*\\+?\\s*days?\\s*(?:per|a|/)\\s*week[^.]{0,40}?${office}`, "i"),
    new RegExp(`${office}[^.]{0,40}?${num}\\s*\\+?\\s*days?\\s*(?:per|a|/)?\\s*week`, "i"),
    new RegExp(`hybrid[^.]{0,40}?${num}\\s*\\+?\\s*days?`, "i"),
  ];
  for (const re of res) {
    const m = text.match(re);
    if (m) {
      const n = WORD_NUM[m[1].toLowerCase()] || parseInt(m[1], 10);
      if (n >= 1 && n <= 6) return n;
    }
  }
  return null;
}

export function classifyWorkMode(job) {
  const loc = (job.location || "").toLowerCase();
  const desc = (job.description || "").toLowerCase();
  const all = `${loc}\n${desc}`;

  const hybrid = /\bhybrid\b/.test(all);
  const remote =
    /\bremote\b/.test(loc) ||
    /(fully remote|remote[- ]first|100% remote|work from anywhere|remote[- ]eligible|open to remote|remote,?\s*(?:us|usa|united states))/.test(desc);
  const onsite = /\b(on[\s-]?site|onsite|in[\s-]?person|in[\s-]?office|in the office)\b/.test(all);

  const days = extractHybridDays(all);

  let workMode = "unknown";
  if (hybrid || days) workMode = "hybrid";
  else if (remote) workMode = "remote";
  else if (onsite) workMode = "onsite";

  return { workMode, hybridDays: workMode === "hybrid" ? days || null : null };
}
