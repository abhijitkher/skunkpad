# job-agent

A daily job feed that scores every opening against my own resume, so I see the best-matched roles first instead of scrolling boards.

## What it does

1. **Pulls** open roles each weekday from company hiring systems (Greenhouse, Lever, Ashby public APIs).
2. **Filters** to the levels and locations I care about (Principal/Staff PM, Head of Product, Director; Bay Area or remote US).
3. **Scores** each role against my resume by keyword and skill overlap, 0 to 100.
4. **Publishes** a ranked feed as a static page, newest and best-matched first, deduped against previous days.

## How it's built

- **`api/refresh.js`**: the refresh job. A Vercel Cron (weekdays, 14:00 UTC, set in `vercel.json`) calls it. It fetches the ATS feeds, scores, and stores the result in a private Vercel Blob. You can also hit `/api/refresh` by hand.
- **`api/feed.js`**: serves the stored feed at `/api/feed`.
- **`src/store.js`**: reads and writes the feed and the "seen" list in Vercel Blob.
- **`src/sources.js`**: one adapter per ATS. Each company is a `{ source, slug }` entry in `companies.json`.
- **`src/score.js`**: the resume-match scorer. Heuristic, not ML. The score is directional.
- **`src/pipeline.js`**: fetch, filter, score, dedupe, and flag what is new since the last run.
- **`public/index.html`**: the feed page. Ranked list with search, sort, and a "new today" filter.
- **`profile.json`** and **`companies.json`**: your targeting and target list.

## Honest limitations

- **Match score is a heuristic.** Keyword and skill overlap against resume text. It surfaces likely-relevant roles; it does not understand seniority nuance or read between lines. Treat it as a sort order, not a verdict.
- **Coverage is ATS-only by design.** Greenhouse, Lever, and Ashby have clean public endpoints. LinkedIn, Indeed, and others are deliberately excluded, their terms restrict scraping, and a visible scraper is the wrong look. A company not on one of these three will not show up.
- **Comp data is not in here.** Levels.fyi and similar are crowd-sourced; those figures live in a separate research step, not this automated feed, so nothing unverified gets presented as fact.

## Status

The scoring and filtering logic is tested. The live calls to Greenhouse, Lever, and Ashby, and the company slugs in `companies.json`, have not been run against the real boards yet. Verify each slug against the company's careers page before trusting results. A wrong slug just shows up in the feed's `errors` list.

## Setup

1. `npm install`
2. Locally: save your resume text as `resume.txt` (gitignored). On Vercel: set the `RESUME_TEXT` environment variable. The resume never goes in the repo.
3. Edit `companies.json` and `profile.json` to taste.
4. Deploy: in Vercel, Add New Project, import this repo, set Root Directory to `job-agent`, framework Other. Then Storage, create a private Blob store and connect it to the project (this adds `BLOB_READ_WRITE_TOKEN`). The schedule lives in `vercel.json`.
5. Optional: set `CRON_SECRET` (Vercel then signs cron calls) and `RUN_TOKEN` (lets you run `/api/refresh?token=...` by hand). With neither set the refresh endpoint is open.

## Local run

```
npm run refresh   # runs the fetch + score once, writes public/feed.json
npm run serve     # serves public/ locally
```
