#!/usr/bin/env python3
"""Hand-curated Solvang, CA pool. Names/coordinates from Google Places; hours, closures and seasons checked
Nov 15 2026 against venue sites, Visit Solvang, county/state park pages and local guides (theynez.com).
Run: python3 tools/gen_solvang.py pools"""
import json, math, os, sys
ROAD = 1.3
C = (34.5950, -120.1390)  # Solvang Village Square
def hav(a, b):
    R = 3958.8; p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(b[1]-a[1])/2)**2
    return 2*R*math.asin(math.sqrt(h))
V, S, L = "Solvang Village", "Santa Ynez Valley", "Lake Cachuma"
I = [
 # ---------------- sights
 ("Old Mission Santa Inés", 34.59476, -120.13646, "landmark", V, 55, 1, ["history","museums"], 60, 1,
  "1804 mission, the 19th of California's 21, with a church, museum and gardens. Still an active parish; self-guided tours 9 to 4:30.",
  {"seasonNote": "Closed New Year's Day, Easter, July 4, Thanksgiving and Christmas."}),
 ("Elverhøj Museum of History & Art", 34.59231, -120.14311, "museum", V, 70, 1, ["museums","history","art"], 60, 1,
  "The best short answer to why a Danish town is in California: local history, Danish-American stories and an art gallery.",
  {"seasonNote": "Open Thu to Mon 11 to 5, closed Tue and Wed. Closed Thanksgiving, Dec 24, 25, 31 and Jan 1. Wiinblad exhibit through Jan 10, 2027."}),
 ("Hans Christian Andersen Museum", 34.59575, -120.13876, "museum", V, 45, 2, ["museums","family"], 30, 0,
  "Small museum above The Book Loft on Mission Drive about the fairy-tale author. Open daily 10 to 5; admission not posted."),
 ("Solvang Viking Museum", 34.5946, -120.1393, "museum", V, 65, 2, ["museums","history","family"], 45, 1,
  "California's only Viking museum, with two reproduction ships, weapons and rune stones. Open daily. Coordinates approximate (1660 Copenhagen Dr)."),
 ("Solvang Windmills & Village Walk", 34.59415, -120.13859, "landmark", V, 10, 2, ["family","markets"], 45, 0,
  "The postcard stop on Copenhagen Drive: windmills, shops and bakeries. Touristy but free and walkable."),
 ("Solvang Julefest (lights, parade, light and music show)", 34.59585, -120.1402, "activity", V, 50, 2, ["family","markets"], 90, 0,
  "Month-long Danish Christmas: nightly light and music shows in Solvang Park, tree lighting Dec 4 at 5:30pm, parade Dec 5 at 11am.",
  {"openMonths": [11,12,1], "best": [11,12], "seasonNote": "Runs Nov 27, 2026 to Jan 3, 2027. Light shows on the hour 5 to 9pm."}),
 ("Hans Christian Andersen Park", 34.60026, -120.14141, "park", V, 55, 2, ["family","hiking","relax"], 60, 0,
  "Playground, shaded trails and the Little Mermaid statue just north of the village."),
 ("Solvang Trolley & Carriage Tours", 34.59525, -120.14121, "activity", V, 10, 2, ["family"], 40, 1,
  "Narrated horse-drawn trolley ride around the village behind Belgian draft horses."),
 ("OstrichLand USA", 34.60625, -120.17657, "activity", S, 65, 2, ["family","wildlife"], 45, 1,
  "Feed 80-plus ostriches and 70 emus from a bowl on a 32-acre farm. Open daily 9 to 6.",
  {"seasonNote": "Emu eggs in winter, ostrich eggs in spring and summer."}),
 ("Nojoqui Falls Park", 34.53373, -120.17743, "park", S, 70, 2, ["hiking","family","relax"], 60, 0,
  "Easy, shaded 0.65-mile walk to a seasonal waterfall of roughly 80 feet, plus picnic lawns and a playground.",
  {"best": [12,1,2,3,4], "seasonNote": "Falls run best after winter rain (Dec to Apr) and shrink to a trickle in summer and fall."}),
 ("Santa Ynez Chumash Museum & Cultural Center", 34.61126, -120.08352, "museum", S, 85, 1, ["museums","history"], 90, 2,
  "The Santa Ynez Band of Chumash tell their own story here (opened 2025). Buy tickets online ahead.",
  {"seasonNote": "Open Thu to Sun 10 to 5; closed Mon to Wed."}),
 ("Santa Ynez Valley Historical Museum & Carriage House", 34.6129, -120.0813, "museum", S, 80, 1, ["museums","history"], 60, 1,
  "Stagecoaches and horse-drawn carriages plus regional saddlery in the town of Santa Ynez. Coordinates approximate (3596 Sagunto St).",
  {"seasonNote": "Open Wed to Sat noon to 4 only."}),
 ("Cachuma Lake Recreation Area", 34.57543, -119.9588, "park", L, 60, 2, ["wildlife","hiking","family"], 120, 1,
  "Reservoir about 12 miles east on Hwy 154 with boat and kayak rentals, a nature center and trails. No swimming (drinking water).",
  {"seasonNote": "Naturalist lake cruises out of service until further notice (Oct 2026). Day use $10 a car, closed Christmas."}),
 ("Figueroa Mountain Road & wildflower fields", 34.73486, -119.98585, "scenic", "Figueroa Mountain", 85, 1, ["scenicdrive","hiking"], 180, 0,
  "Winding climb from Los Olivos into Los Padres National Forest; poppies and lupine in spring, big valley views year-round.",
  {"rd": 22, "best": [2,3,4], "seasonNote": "Wildflowers usually Feb to Apr. Storms and snow can close the road; fire restrictions were in force in Oct 2026. Check Los Padres alerts."}),
 ("La Purísima Mission State Historic Park", 34.66977, -120.42062, "landmark", "Lompoc", 75, 2, ["history","museums","hiking"], 120, 1,
  "California's most completely restored mission: gardens, a church, and corrals with burros and longhorns. $6 a car.",
  {"rd": 29, "seasonNote": "Buildings 9 to 4; tours Wed to Sun at 1pm (Sat also 11am). Closed Thanksgiving, Christmas and New Year's Day."}),
 # ---------------- wineries
 ("Alma Rosa Winery tasting room (Solvang)", 34.59633, -120.14091, "activity", V, 60, 0, ["food","relax"], 60, 2,
  "Tasting room in the village for a Santa Rita Hills producer; an easy first tasting on foot."),
 ("Rideau Vineyard", 34.62785, -120.11457, "activity", S, 80, 0, ["food","relax"], 75, 2,
  "Winery and vineyard tasting room on Alamo Pintado Road toward Los Olivos."),
 ("Brave & Maiden Estate", 34.60033, -120.09913, "activity", S, 85, 0, ["food","relax"], 75, 2,
  "Estate winery and farm on N Refugio Road in Santa Ynez."),
 ("Roblar Winery & Vineyards", 34.64987, -120.09635, "activity", S, 85, 0, ["food","relax"], 75, 2,
  "Winery and vineyard on Roblar Avenue north of Santa Ynez."),
 ("Gainey Vineyard", 34.60807, -120.06515, "activity", S, 70, 0, ["food","relax"], 75, 2,
  "Estate winery and tasting room on Hwy 246 east of Santa Ynez."),
 # ---------------- food
 ("peasants FEAST", 34.59561, -120.14223, "food", V, 80, 1, ["food"], 75, 2,
  "Michelin Bib Gourmand farm-driven comfort food: Solvang Hot Chicken, mushroom tacos, beet grilled cheese. No reservations.",
  {"veg": 2, "seasonNote": "Open Wed to Sun 11 to 6; closed Mon and Tue.", "meals": ["L"], "closedDays": [1, 2]}),
 ("Mad & Vin at The Landsby", 34.59574, -120.14295, "food", V, 50, 1, ["food"], 75, 2,
  "Wine-country New American with vegetarian and vegan options; breakfast and dinner daily.", {"veg": 1}),
 ("Whiskey 'N Rye Smokehouse", 34.59479, -120.14212, "food", V, 55, 2, ["food"], 60, 2,
  "Smokehouse barbecue on Atterdag Road."),
 ("Solvang Restaurant", 34.59462, -120.13951, "food", V, 45, 2, ["food"], 60, 1,
  "Danish meatballs and waffles; busy and no online reservations.", {"meals": ["L"]}),
 ("KANOK Thai Cuisine", 34.59425, -120.13903, "food", V, 50, 1, ["food"], 60, 2,
  "Thai kitchen on Alisal Road, a break from the Danish menus.", {"veg": 1}),
 ("The Gathering Table", 34.59629, -120.14321, "food", V, 55, 1, ["food"], 60, 2,
  "Asian-fusion dining room on Mission Drive.", {"veg": 1}),
 ("Café Dolce", 34.59532, -120.13988, "food", V, 40, 2, ["food"], 45, 1,
  "Coffee, breakfast, panini and acai bowls with vegan options; open early and late.", {"veg": 2, "meals": ["L"]}),
 ("brekkies by chomp", 34.59614, -120.13959, "food", V, 55, 2, ["food"], 60, 1,
  "Brunch spot on Mission Drive.", {"veg": 1, "meals": ["L"]}),
 ("Birkholm's Bakery & Cafe", 34.59488, -120.13832, "food", V, 50, 2, ["food"], 45, 1,
  "Bakery, coffee and sandwiches on Alisal Road.", {"veg": 1, "meals": ["L"]}),
 ("Olsen's Danish Village Bakery", 34.59626, -120.14422, "food", V, 40, 2, ["food"], 30, 1,
  "Danish pastries and aebleskiver, a Solvang ritual.", {"veg": 1, "meals": ["L"]}),
 ("Mortensen's Danish Bakery", 34.59577, -120.14199, "food", V, 45, 2, ["food"], 30, 1,
  "Danish bakery on Mission Drive.", {"veg": 1, "meals": ["L"]}),
 ("Solvang Bakery", 34.59426, -120.13855, "food", V, 65, 2, ["food"], 30, 1,
  "Pastries and cakes on Alisal Road.", {"veg": 1, "meals": ["L"]}),
 ("The Baker's Table", 34.61276, -120.08105, "food", S, 80, 2, ["food"], 45, 1,
  "Bakery and cafe on Sagunto Street in Santa Ynez.", {"veg": 1, "meals": ["L"]}),
 ("S.Y. Kitchen", 34.6134, -120.07982, "food", S, 75, 1, ["food"], 80, 2,
  "Italian kitchen in Santa Ynez.", {"veg": 1}),
 ("Brothers Restaurant at the Red Barn", 34.61304, -120.08214, "food", S, 70, 1, ["food"], 90, 3,
  "Special-occasion American dining in Santa Ynez."),
 ("Los Olivos Café", 34.66495, -120.11524, "food", S, 65, 1, ["food"], 75, 2,
  "California wine-country cafe on Grand Avenue with a patio and a big local wine list.", {"veg": 1}),
 ("Lucky Penny", 34.66568, -120.11348, "food", S, 80, 2, ["food"], 50, 1,
  "Casual pizza in Los Olivos.", {"veg": 1}),
 ("Vega Vineyard and Farm", 34.59858, -120.19396, "food", S, 85, 0, ["food","relax"], 90, 2,
  "Farm, winery and restaurant in Buellton.", {"veg": 1}),
]
def build():
    out = []
    for i, it in enumerate(I, 1):
        name, lat, lng, typ, area, local, kid, ints, dur, cost, note = it[:11]
        ex = dict(it[11]) if len(it) > 11 else {}
        rd = ex.pop("rd", None)
        if rd is None: rd = hav(C, (lat, lng)) * ROAD
        d = {"id": f"s{i:02d}", "name": name, "type": typ, "area": area, "lat": round(lat,5), "lng": round(lng,5),
             "distMi": round(rd,1), "local": local, "kid": kid, "interests": ints, "durMin": dur, "cost": cost, "note": note}
        d.update(ex); out.append(d)
    return {"city": "Solvang", "state": "CA", "center": {"lat": C[0], "lng": C[1]},
            "source": "Hand-curated Nov 15 2026. Names and coordinates from Google Places; hours, closures and seasons checked against venue sites, Visit Solvang, county and state park pages. Verify before booking. distMi is approximate road miles from Solvang Village Square.",
            "road": ROAD, "tripShare": 0.34, "count": len(out), "items": out}
if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "pools"
    p = build(); names = [x["name"] for x in p["items"]]; assert len(names) == len(set(names))
    json.dump(p, open(os.path.join(d, "solvang.json"), "w"), separators=(",", ":"), ensure_ascii=False)
    print(p["count"], "items")
