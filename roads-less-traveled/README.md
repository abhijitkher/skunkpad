# roads-less-traveled

Pick a city, set your style and how far you'll roam, and it instantly routes a
day-by-day trip plan. No model call per plan: each city is a cached pool of real,
tagged places (names and coordinates from Google Places), and every filter just
reshapes a view over that one pool, so planning, re-filtering and swapping are
free and immediate.

**Live:** https://skunkpad-roads-less-traveled.vercel.app/

## How it works
- Each city is a JSON pool of places, each tagged with type, a touristy-to-local
  score, kid-friendliness, veg suitability, interests, duration, cost, neighborhood,
  lat/lng, distance from the city, and seasonal opening months.
- The filters (dates, party, veg/non-veg, distance 10-500 mi, travel style, pace,
  interests, budget) select from the pool. The assembler clusters each day by
  geography, routes it nearest-first with real travel times, drops out-of-season
  spots for the trip's month, and weaves in meals matching the veg mix.
- One URL per city. Today the seeded city is Denver; more are added as they're searched.

## Status
Denver is seeded (49 places, Rocky Mountain NP to Ouray). The new-city generation
pipeline and browser-notification-on-ready are the next layer.
