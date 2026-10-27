// GET /api/pool?city=<name>  ->  { city, state, center, items:[...] }
// Builds a city's place pool on first request, caches it in Blob, then serves the cache.
// After the pool exists, all filtering happens client-side; this runs once per city.
let blob = null;
try { blob = require('@vercel/blob'); } catch (e) { blob = null; }

const INTERESTS = "hotsprings, hiking, scenicdrive, trains, skitown, wildlife, adventure, museums, art, food, brewery, sports, markets, history, gardens, family, relax, nightlife";
const SIXTY_DAYS = 60 * 24 * 60 * 60 * 1000;

module.exports = async (req, res) => {
  const raw = String((req.query && req.query.city) || '').trim();
  if (!raw) return res.status(400).json({ error: 'Missing city.' });
  const slug = raw.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const key = 'cities/' + slug + '.json';

  // 1. serve from cache if fresh
  if (blob) {
    try {
      const h = await blob.head(key).catch(() => null);
      if (h && h.url) {
        const age = Date.now() - new Date(h.uploadedAt || 0).getTime();
        if (age < SIXTY_DAYS) {
          const r = await fetch(h.url);
          if (r.ok) { const cached = await r.json(); cached.cached = true; return res.status(200).json(cached); }
        }
      }
    } catch (e) {}
  }

  // 2. build it
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return res.status(500).json({ error: 'ANTHROPIC_API_KEY is not set. Add it in Vercel -> Settings -> Environment Variables, then redeploy.' });
  const model = process.env.ANTHROPIC_MODEL || 'claude-3-5-haiku-latest';

  let data;
  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model, max_tokens: 8000, messages: [{ role: 'user', content: buildPrompt(raw) }] })
    });
    data = await r.json().catch(() => null);
    if (!r.ok) return res.status(502).json({ error: (data && data.error && data.error.message) || ('Model API error (' + r.status + ').') });
  } catch (e) { return res.status(502).json({ error: 'Could not reach the model API.' }); }

  const text = ((data && data.content) || []).map(b => b.text || '').join('').trim();
  const pool = parseJson(text);
  if (!pool || !Array.isArray(pool.items)) return res.status(502).json({ error: 'The city pool came back unparseable. Try again.' });

  // 3. normalize: fill defaults, compute distance + overnight from the city center
  const c = pool.center || {};
  const items = [];
  pool.items.forEach((it, i) => {
    if (!it || typeof it.lat !== 'number' || typeof it.lng !== 'number' || !it.name) return;
    const d = miles(c.lat, c.lng, it.lat, it.lng);
    it.id = 'g' + String(i + 1).padStart(2, '0');
    it.distMi = Math.round(d * 10) / 10;
    if (d > 120) it.overnight = true;
    it.durMin = Number(it.durMin) || 90;
    it.cost = (typeof it.cost === 'number') ? it.cost : 1;
    it.local = (typeof it.local === 'number') ? it.local : 50;
    it.kid = (typeof it.kid === 'number') ? it.kid : 1;
    it.type = it.type || 'activity';
    it.area = it.area || pool.city || raw;
    it.note = it.note || '';
    if (!Array.isArray(it.interests)) it.interests = [];
    items.push(it);
  });
  pool.items = items;
  pool.count = items.length;
  pool.source = 'AI-generated for ' + (pool.city || raw) + '; verify places, hours and prices before booking';

  // 4. cache for next time
  if (blob) { try { await blob.put(key, JSON.stringify(pool), { access: 'public', contentType: 'application/json', allowOverwrite: true }); } catch (e) {} }

  return res.status(200).json(pool);
};

function miles(la1, lo1, la2, lo2) {
  if ([la1, lo1, la2, lo2].some(v => typeof v !== 'number')) return 0;
  const R = 3958.8, r = Math.PI / 180, dp = (la2 - la1) * r, dl = (lo2 - lo1) * r;
  const x = Math.sin(dp / 2) ** 2 + Math.cos(la1 * r) * Math.cos(la2 * r) * Math.sin(dl / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(x));
}

function buildPrompt(city) {
  return [
    "You are building a places database for a trip planner. City: " + city + ".",
    "Return ONLY one JSON object: {\"city\":\"\",\"state\":\"\",\"center\":{\"lat\":0,\"lng\":0},\"items\":[...]}.",
    "center = the real lat/lng of the city center.",
    "items = 28 to 36 real, notable places in and around " + city + ", reaching out to about 200 miles for standout day trips and scenic or mountain/coastal spots.",
    "Each item: {\"name\",\"type\",\"area\",\"lat\",\"lng\",\"local\",\"kid\",\"interests\",\"durMin\",\"cost\",\"note\",\"veg\"(food only, 0-2),\"seasonNote\"(short, only if seasonal),\"openMonths\"(array of month numbers 1-12, only if access is seasonal)}.",
    "type is exactly one of: museum, activity, landmark, park, food, stadium, scenic.",
    "lat and lng: the real coordinates of that place (approximate is fine, but it must be the real location).",
    "local: 0 (famous tourist icon) to 100 (offbeat and local). kid: 0 (not for kids) to 2 (great for kids). cost: 0 free to 3 pricey. durMin: typical minutes to spend.",
    "interests: choose ONLY from this exact list: " + INTERESTS + ".",
    "Give a real spread: top sights, museums, a few food spots (some veg-forward, set veg), parks/gardens, and whatever this region is actually known for (hot springs, scenic trains, beaches, stadiums, mountain towns, wine, etc.). Use the specific tags (hotsprings, trains, hiking, beach is not in the list so use relax/water-style tags that exist) rather than vague ones.",
    "Do NOT include distMi or id fields. Output nothing except the JSON object."
  ].join("\n");
}

function parseJson(t) {
  if (!t) return null;
  try { return JSON.parse(t); } catch (e) {}
  const f = t.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (f) { try { return JSON.parse(f[1]); } catch (e) {} }
  const s = t.indexOf('{'), e = t.lastIndexOf('}');
  if (s >= 0 && e > s) { try { return JSON.parse(t.slice(s, e + 1)); } catch (e2) {} }
  return null;
}
