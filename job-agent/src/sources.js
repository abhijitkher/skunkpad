// One adapter per ATS. Each returns jobs in a common shape:
// { id, company, title, location, url, description, postedAt, comp }
// All three use the public, documented job board endpoints. No scraping.

const TIMEOUT_MS = 8000;

async function getJson(url) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, { signal: ctrl.signal });
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

const strip = (html = "") =>
  html.replace(/<[^>]*>/g, " ").replace(/&[a-z#0-9]+;/gi, " ").replace(/\s+/g, " ").trim();

async function greenhouse({ slug, name }) {
  const data = await getJson(`https://boards-api.greenhouse.io/v1/boards/${slug}/jobs?content=true`);
  return (data.jobs || []).map((j) => ({
    id: `gh-${slug}-${j.id}`,
    company: name,
    title: j.title,
    location: j.location?.name || "",
    url: j.absolute_url,
    description: strip(j.content),
    postedAt: j.updated_at || null,
    comp: null,
  }));
}

async function lever({ slug, name }) {
  const data = await getJson(`https://api.lever.co/v0/postings/${slug}?mode=json`);
  return (data || []).map((j) => ({
    id: `lv-${slug}-${j.id}`,
    company: name,
    title: j.text,
    location: j.categories?.location || "",
    url: j.hostedUrl,
    description: j.descriptionPlain || "",
    postedAt: j.createdAt ? new Date(j.createdAt).toISOString() : null,
    comp: null,
  }));
}

async function ashby({ slug, name }) {
  const data = await getJson(`https://api.ashbyhq.com/posting-api/job-board/${slug}?includeCompensation=true`);
  return (data.jobs || []).map((j) => ({
    id: `ab-${slug}-${j.id}`,
    company: name,
    title: j.title,
    location: j.location || "",
    url: j.jobUrl,
    description: j.descriptionPlain || strip(j.descriptionHtml),
    postedAt: j.publishedAt || null,
    comp: j.compensation?.compensationTierSummary || null,
  }));
}

const ADAPTERS = { greenhouse, lever, ashby };

// Fetch every company in parallel. A failing board never sinks the run.
export async function fetchAll(companies) {
  const results = await Promise.allSettled(
    companies.map((c) => {
      const adapter = ADAPTERS[c.source];
      if (!adapter) return Promise.reject(new Error(`unknown source ${c.source}`));
      return adapter(c);
    })
  );
  const jobs = [];
  const errors = [];
  results.forEach((r, i) => {
    if (r.status === "fulfilled") jobs.push(...r.value);
    else errors.push({ company: companies[i].name, error: String(r.reason?.message || r.reason) });
  });
  return { jobs, errors };
}
