import json, math, os, sys

ROAD = 1.3  # straight-line -> road-mile circuity used for in-area legs

def hav(a, b):
    R = 3958.8
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1
    dl = math.radians(b[1] - a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

ALL = list(range(1, 13))
WARM = [3,4,5,6,7,8,9,10,11]

def build(prefix, center, city, state, area_base, items, source):
    out = []
    for i, it in enumerate(items, 1):
        (name, lat, lng, typ, area, local, kid, interests, dur, cost, note) = it[:11]
        ex = it[11] if len(it) > 11 else {}
        ex = dict(ex)
        rd = ex.pop('rd', None)
        if rd is None:
            if area in area_base:
                base, anchor = area_base[area]
                rd = base + hav(anchor, (lat, lng)) * ROAD
            else:
                rd = hav(center, (lat, lng)) * ROAD
        d = {
            "id": f"{prefix}{i:02d}", "name": name, "type": typ, "area": area,
            "lat": round(lat, 5), "lng": round(lng, 5), "distMi": round(rd, 1),
            "local": local, "kid": kid, "interests": interests, "durMin": dur,
            "cost": cost, "note": note,
        }
        if rd > 120:
            d["overnight"] = True
        d.update(ex)
        out.append(d)
    return {"city": city, "state": state, "center": {"lat": center[0], "lng": center[1]},
            "source": source, "road": ROAD, "tripShare": 0.34, "count": len(out), "items": out}

# ---------------------------------------------------------------- ZION
ZC = (37.2000925, -112.9869847)
Z_BASE = {
    "Kolob Canyons": (40, (37.4534, -113.2254)),
    "Cedar City & Cedar Breaks": (57, (37.677, -113.063)),
    "St. George & Snow Canyon": (45, (37.1095, -113.5784)),
    "Kanab": (40, (37.0475, -112.5295)),
    "Page, AZ": (118, (36.9147, -111.4558)),
}
Z = [
 # ---- Zion Canyon (shuttle area)
 ("Pa'rus Trail", 37.20182, -112.98678, "park", "Zion Canyon", 30, 2, ["hiking","family","relax"], 60, 0,
  "Flat, paved 3.5-mile riverside path from the visitor center; walkers and bikes share it, no shuttle needed."),
 ("Zion Human History Museum", 37.20954, -112.98033, "museum", "Zion Canyon", 40, 1, ["museums","history","family"], 45, 0,
  "Small NPS museum on the canyon road with a terrace view of the Towers of the Virgin.",
  {"openMonths": WARM, "seasonNote": "NPS lists fall hours (10-5) through Nov 28; confirm winter schedule."}),
 ("Weeping Rock", 37.27168, -112.93655, "park", "Zion Canyon", 40, 1, ["hiking","family"], 45, 0,
  "Short, steep paved climb to a dripping alcove and hanging gardens (shuttle stop 7). The old trail beyond it to Hidden Canyon and Observation Point stays closed."),
 ("Emerald Pools (Lower)", 37.24848, -112.95873, "park", "Zion Canyon", 25, 1, ["hiking","family"], 90, 0,
  "Easy shaded walk behind a seasonal waterfall, from Zion Lodge (shuttle stop 5). Flow is thin in dry months."),
 ("Riverside Walk & Temple of Sinawava", 37.28428, -112.94683, "scenic", "Zion Canyon", 20, 2, ["hiking","family","relax"], 90, 0,
  "Paved 1-mile-each-way riverside path at the end of the canyon road (last shuttle stop) and the start of The Narrows."),
 ("The Narrows (bottom-up)", 37.2850, -112.9480, "activity", "Zion Canyon", 20, 0, ["hiking","adventure"], 240, 1,
  "Wade the Virgin River between canyon walls. Closes when flow tops 150 cfs or on a flash-flood warning; NPS also warns against submerging your head (cyanobacteria). Rent neoprene or a drysuit in Springdale in cold months.",
  {"seasonNote": "Cold water and short days Nov-Mar: drysuit territory. Check the USGS gauge and NPS alerts the morning of."}),
 ("Angels Landing", 37.25924, -112.95126, "activity", "Zion Canyon", 10, 0, ["hiking","adventure"], 300, 0,
  "Famous chain-assisted ridge hike (Grotto, shuttle stop 6). NPS permit via lottery is required for the chained section; Scout Lookout is the no-permit turnaround."),
 ("Red Rock Grill (Zion Lodge)", 37.2512, -112.95596, "food", "Zion Canyon", 30, 1, ["food","relax"], 75, 2,
  "Dining room inside the park at Zion Lodge, handy between Emerald Pools and the Narrows."),
 # ---- East Zion (Zion-Mt. Carmel Highway)
 ("Canyon Overlook Trail", 37.21364, -112.94333, "park", "East Zion", 45, 1, ["hiking","scenicdrive"], 60, 0,
  "1-mile round trip to a ledge over Pine Creek Canyon; trailhead is on SR-9 just east of the tunnel, with a tiny lot. SR-9 reopened Oct 9, 2026 after a rockfall, with a temporary gravel stretch; oversize vehicles are restricted."),
 ("Checkerboard Mesa Viewpoint", 37.22457, -112.88017, "scenic", "East Zion", 55, 2, ["scenicdrive"], 25, 0,
  "Roadside pullout on the Zion-Mount Carmel Highway facing the crosshatched sandstone mesa."),
 ("Observation Point (East Mesa Trail)", 37.29699, -112.90014, "activity", "East Zion", 55, 0, ["hiking","adventure"], 240, 0,
  "About 7 miles round trip to a rim higher than Angels Landing. Reachable only from the East Mesa trailhead outside the park (the Weeping Rock route is closed); the last stretch is rough dirt, and a paid shuttle runs from Zion Ponderosa."),
 # ---- Kolob Terrace / west
 ("Lava Point Overlook (Kolob Terrace)", 37.38398, -113.02898, "scenic", "Kolob Terrace", 85, 1, ["scenicdrive","hiking"], 150, 0,
  "High-country overlook at ~7,900 ft reached by the long Kolob Terrace Road; the last couple of miles are gravel.",
  {"openMonths": [5,6,7,8,9,10], "seasonNote": "Kolob Terrace Road closes for snow from fall to spring; Lava Point campground closed for winter Oct 5.", "rd": 42}),
 ("Grafton Ghost Town", 37.16741, -113.08183, "landmark", "Rockville & Grafton", 90, 1, ["history"], 60, 0,
  "Restored 1860s Mormon settlement and cemetery off a dirt road near Rockville; the signed walking tour takes about an hour."),
 # ---- Springdale culture
 ("Worthington Gallery", 37.18907, -112.99672, "museum", "Springdale", 70, 0, ["art"], 40, 0,
  "Springdale gallery of Southwest landscape painting and sculpture."),
 ("David J. West Gallery", 37.18897, -112.99684, "museum", "Springdale", 70, 0, ["art"], 40, 0,
  "Local landscape-photography gallery on Zion Park Blvd."),
 # ---- Springdale food
 ("Oscar's Cafe", 37.18901, -113.00028, "food", "Springdale", 55, 1, ["food"], 75, 2,
  "Big-portion Southwest and Mexican plates on a patio. Vegetarian items are marked on the menu and vegan swaps are available.", {"veg": 1}),
 ("Thai Sapa", 37.19807, -112.99178, "food", "Springdale", 60, 1, ["food"], 75, 2,
  "Small Thai spot; stir-fries, curries and noodles are easy to order plant-based.", {"veg": 1}),
 ("Whiptail Grill", 37.19427, -112.9927, "food", "Springdale", 70, 1, ["food"], 70, 2,
  "Converted gas station with a patio; tofu or veggie burrito, salads and chips with guac.", {"veg": 1}),
 ("Bit & Spur Restaurant & Saloon", 37.18468, -113.00311, "food", "Springdale", 60, 1, ["food","nightlife"], 80, 2,
  "Longtime Southwest-Mexican saloon; vegetarian, vegan and dairy-free dishes are labeled on the menu.", {"veg": 1}),
 ("Spotted Dog Cafe", 37.1947, -112.99324, "food", "Springdale", 50, 1, ["food"], 80, 2,
  "Restaurant and bar at Flanigan's Inn with a few vegan options.", {"veg": 1}),
 ("Zion Canyon Brew Pub", 37.19932, -112.98904, "food", "Springdale", 45, 2, ["food","brewery"], 75, 2,
  "Brewpub next to the park entrance; lists some vegetarian and vegan dishes.", {"veg": 1}),
 ("MeMe's Cafe", 37.18842, -113.00007, "food", "Springdale", 55, 2, ["food"], 60, 1,
  "Breakfast all day and lunch; vegan options are limited (oatmeal, a house vegan meatloaf, sandwich swaps).", {"veg": 1}),
 ("Wild Thyme Bistro at Trees Ranch", 37.16213, -113.01745, "food", "Springdale", 60, 1, ["food"], 90, 2,
  "Garden-fed bistro on the edge of town; menu marks vegetarian (VG) and vegan (V) dishes such as black bean sliders and yellow curry.", {"veg": 1}),
 ("FeelLove Coffee (Springdale)", 37.18635, -113.00162, "food", "Springdale", 65, 2, ["food","relax"], 45, 1,
  "Coffee, breakfast and brunch; Google lists it as a vegan and vegetarian restaurant.", {"veg": 2}),
 ("Bonrue Bakery", 37.18954, -112.9976, "food", "Springdale", 65, 2, ["food"], 30, 1,
  "Bakery and donut counter on Zion Park Blvd."),
 # ---- Kolob Canyons
 ("Kolob Canyons Scenic Drive", 37.43523, -113.2012, "scenic", "Kolob Canyons", 70, 2, ["scenicdrive","hiking"], 90, 0,
  "5-mile paved road to Kolob Canyons Viewpoint off I-15 exit 40, up to ~1,000 ft under red fins. Closes in winter for snow or ice, and walking the road is not allowed during plowing."),
 ("Timber Creek Overlook Trail", 37.42791, -113.20399, "park", "Kolob Canyons", 75, 2, ["hiking","family"], 45, 0,
  "About 1 mile round trip with little climbing to a panorama of Kolob Canyons, the Pine Valley Mountains and Kolob Terrace; good for little legs."),
 # ---- Cedar City & Cedar Breaks
 ("Cedar Breaks National Monument (Point Supreme)", 37.61498, -112.83855, "scenic", "Cedar City & Cedar Breaks", 70, 1, ["scenicdrive","hiking"], 120, 1,
  "Red-rock amphitheater above 10,000 ft with a 5-mile road of overlooks and wildflower meadows.",
  {"openMonths": [5,6,7,8,9,10], "seasonNote": "UT-148 is closed by snow outside roughly late May to October.", "rd": 85}),
 ("Utah Shakespeare Festival", 37.6766, -113.06444, "activity", "Cedar City & Cedar Breaks", 55, 1, ["art","nightlife"], 180, 3,
  "Repertory theater with a free Greenshow before evening performances.",
  {"openMonths": [6,7,8,9,10], "seasonNote": "Summer and fall seasons only; check the schedule for dates."}),
 ("Parowan Gap Petroglyphs", 37.90937, -112.98423, "landmark", "Cedar City & Cedar Breaks", 95, 1, ["history"], 75, 0,
  "Ancient rock-art panels in a wind gap north of Cedar City; open 24 hours, no fee."),
 ("Namaste America Indian Cuisine", 37.71563, -113.06147, "food", "Cedar City & Cedar Breaks", 60, 1, ["food"], 75, 2,
  "Indian restaurant that Google lists as vegetarian and vegan friendly.", {"veg": 1}),
 ("Centro Woodfired Pizzeria", 37.67757, -113.06276, "food", "Cedar City & Cedar Breaks", 55, 2, ["food"], 70, 2,
  "Woodfired pizza and Italian on Center Street, two blocks from the Shakespeare Festival."),
 # ---- St. George & Snow Canyon
 ("Snow Canyon State Park", 37.21781, -113.6396, "park", "St. George & Snow Canyon", 65, 2, ["hiking","family","scenicdrive"], 180, 1,
  "Red and white Navajo sandstone against black lava; easy picks are Jenny's Canyon, the lava tubes and the Petrified Dunes. Enter from the south end for the best drive."),
 ("Tuacahn Amphitheatre", 37.19014, -113.65865, "activity", "St. George & Snow Canyon", 50, 1, ["art","nightlife"], 150, 3,
  "Broadway-style musicals in an open-air theater inside a red-rock canyon near Ivins.",
  {"seasonNote": "Main shows run roughly spring through fall; check the schedule."}),
 ("Quail Creek State Park", 37.191, -113.38637, "park", "St. George & Snow Canyon", 60, 2, ["relax","family"], 120, 1,
  "Warm reservoir near Hurricane with paddling and rentals; free life jackets are available."),
 ("The Hearty Beet Cafe", 37.12497, -113.52345, "food", "St. George & Snow Canyon", 55, 2, ["food"], 60, 1,
  "Cafe listed as vegan and vegetarian in St. George.", {"veg": 2}),
 ("Cafe FeelLove (St. George)", 37.11079, -113.58398, "food", "St. George & Snow Canyon", 65, 2, ["food","relax"], 60, 1,
  "Downtown brunch cafe listed as vegan and vegetarian.", {"veg": 2}),
 ("Mint Indian Bistro", 37.12424, -113.52777, "food", "St. George & Snow Canyon", 50, 1, ["food"], 75, 2,
  "North Indian restaurant that Google lists as vegetarian and vegan friendly.", {"veg": 1}),
 ("Mixed Greens", 37.11018, -113.56927, "food", "St. George & Snow Canyon", 45, 2, ["food"], 40, 1,
  "Salad, acai and juice counter for a quick lunch.", {"veg": 1}),
 # ---- Kanab
 ("Best Friends Animal Sanctuary", 37.12579, -112.54379, "activity", "Kanab", 80, 2, ["family","relax"], 120, 0,
  "Largest no-kill animal sanctuary in Angel Canyon; free tours, a welcome center and views. Reviewers mention a free 90-minute guided tour.",
  {"rd": 46}),
 ("Coral Pink Sand Dunes State Park", 37.03774, -112.71443, "park", "Kanab", 65, 2, ["adventure","family"], 150, 1,
  "Coral-colored dunes with sandboard rentals; a state-park fee applies and national park passes are not accepted.",
  {"rd": 50}),
 ("Peekaboo Canyon Wood Fired Kitchen", 37.04788, -112.53344, "food", "Kanab", 70, 1, ["food","nightlife"], 80, 2,
  "Kanab's all-vegetarian-and-vegan restaurant: wood-fired pizza plus Impossible and Beyond dishes. Closed Mondays.", {"veg": 2}),
 ("Angel Village Cafe", 37.14085, -112.5432, "food", "Kanab", 85, 2, ["food"], 60, 1,
  "Plant-based buffet lunch at Best Friends, served 11:30 to 1 daily.", {"veg": 2}),
 ("Rocking V Cafe", 37.04796, -112.5305, "food", "Kanab", 70, 1, ["food","art"], 80, 2,
  "Art-filled eatery in an 1892 mercantile; slow food from meats to vegan plates.", {"veg": 1}),
 ("Wild Thyme Cafe (Kanab)", 37.04492, -112.52672, "food", "Kanab", 55, 1, ["food"], 80, 2,
  "Beef, fish and chicken plus ample vegan and vegetarian selections.", {"veg": 1}),
 # ---- Page, AZ
 ("Horseshoe Bend Overlook", 36.87917, -111.51063, "scenic", "Page, AZ", 20, 1, ["scenicdrive"], 90, 1,
  "Short walk to the rim above the Colorado River's horseshoe meander. Long day trip: roughly 2.5 hours from Zion each way."),
 ("Lower Antelope Canyon (guided tour)", 36.90132, -111.41026, "activity", "Page, AZ", 20, 1, ["adventure"], 120, 3,
  "Navajo-guided slot canyon tours; booking is required and tours cancel for flash-flood risk."),
]
Z_SOURCE = ("Hand-curated Nov 2026. Names and coordinates from Google Places; tags and notes editorial. "
            "Closures and seasonal facts checked against NPS notices and local reports as of Nov 10, 2026 and change often: "
            "verify with NPS (nps.gov/zion) before booking. distMi is approximate road miles from the Zion Canyon Visitor Center.")

# ---------------------------------------------------------------- BRYCE
BC = (37.6404299, -112.169587)
B_BASE = {
    "Zion National Park": (85, (37.2001, -112.987)),
    "Cedar Breaks": (56, (37.615, -112.8386)),
    "Kanab": (78, (37.0475, -112.5295)),
}
B = [
 # ---- Bryce Amphitheater
 ("Bryce Canyon Visitor Center", 37.6404, -112.1696, "museum", "Bryce Amphitheater", 20, 2, ["museums","history","family"], 45, 0,
  "Start here for ranger programs, the park film and the current trail and road conditions."),
 ("Sunrise Point", 37.62826, -112.163, "scenic", "Bryce Amphitheater", 30, 2, ["scenicdrive","hiking"], 45, 0,
  "First-light rim view; the Queen's Garden and Fairyland trails drop from here."),
 ("Sunset Point", 37.62335, -112.16721, "scenic", "Bryce Amphitheater", 30, 2, ["scenicdrive","hiking"], 45, 0,
  "Evening rim view and the head of the Navajo Loop; a paved rim path links it to Sunrise Point."),
 ("Inspiration Point", 37.61369, -112.16888, "scenic", "Bryce Amphitheater", 40, 1, ["scenicdrive","hiking"], 40, 0,
  "Three-tier overlook; the short climb to the upper level gives the widest view of the amphitheater."),
 ("Bryce Point", 37.60439, -112.15655, "scenic", "Bryce Amphitheater", 40, 1, ["scenicdrive","hiking"], 40, 0,
  "Highest viewpoint in the main amphitheater and the south end of the Rim Trail; parking fills up."),
 ("Navajo Loop & Queen's Garden Trails", 37.61851, -112.16217, "activity", "Bryce Amphitheater", 25, 1, ["hiking","family"], 150, 0,
  "The classic 3-mile combo into the hoodoos from Sunrise or Sunset Point, with a steep climb back. Sections close for ice or rockfall in winter; check NPS."),
 ("Peekaboo Loop", 37.61757, -112.15833, "activity", "Bryce Amphitheater", 40, 0, ["hiking","adventure"], 210, 0,
  "Roller-coaster loop through tunnels and windows; shared with horse rides, hiked clockwise (about 5.5 miles from Bryce Point with the Connecting Trail)."),
 ("Fairyland Loop Trail & Tower Bridge", 37.63191, -112.16268, "activity", "Bryce Amphitheater", 60, 0, ["hiking","adventure"], 300, 0,
  "8-mile loop with steady climbs and fewer people; Tower Bridge is a short side spur."),
 ("Fairyland Point", 37.64914, -112.14738, "scenic", "Bryce Amphitheater", 65, 2, ["scenicdrive"], 30, 0,
  "Quiet overlook at the north end with a short rim walk; starting point of the Fairyland Loop."),
 ("Guided horse or mule ride (Canyon Trail Rides)", 37.6266, -112.1670, "activity", "Bryce Amphitheater", 45, 1, ["adventure","family"], 150, 3,
  "NPS concessioner rides into the amphitheater: 2-hour ($75) and 3-hour ($100) outings; ages 7+ for the 2-hour ride, 10+ for the 3-hour. Meeting point near the Lodge.",
  {"openMonths": [4,5,6,7,8,9,10], "seasonNote": "Guided rides typically run April through October 31, weather permitting."}),
 ("The Lodge at Bryce Canyon Restaurant", 37.62708, -112.16794, "food", "Bryce Amphitheater", 35, 1, ["food","relax"], 80, 2,
  "Historic lodge dining room with a quinoa bowl and trout; reviewers call vegetarian options limited but present.",
  {"veg": 1, "openMonths": [4,5,6,7,8,9,10], "seasonNote": "Lodge dining is typically seasonal (spring to fall); verify before counting on it."}),
 # ---- Scenic drive south
 ("Natural Bridge", 37.53214, -112.26005, "scenic", "Bryce Scenic Drive", 45, 2, ["scenicdrive"], 25, 0,
  "A red-rock arch visible from the road, one of several pullouts along the 18-mile Scenic Drive."),
 ("Farview Point", 37.54459, -112.24695, "scenic", "Bryce Scenic Drive", 55, 2, ["scenicdrive"], 25, 0,
  "Wide southern panorama with a short walk to a higher viewpoint and restrooms at the lot."),
 ("Rainbow Point & Yovimpa Point", 37.47594, -112.24071, "scenic", "Bryce Scenic Drive", 60, 2, ["scenicdrive","hiking"], 75, 0,
  "End of the road at ~9,100 ft, two views 80+ miles to Navajo Mountain; Bristlecone Loop starts here.",
  {"seasonNote": "Snow can close the southern end of the Scenic Drive in winter; check NPS."}),
 # ---- Bryce Canyon City / Tropic
 ("Mossy Cave Trail", 37.66572, -112.11035, "activity", "Tropic Ditch", 55, 2, ["hiking","family"], 60, 0,
  "Under-a-mile stream-side walk to a small waterfall and a shallow overhang, on SR-12 east of the park road; reviewers say there is no entrance gate.",
  {"seasonNote": "The waterfall flows seasonally."}),
 ("Canyon Diner (Ruby's Inn)", 37.67443, -112.15669, "food", "Bryce Canyon City", 20, 2, ["food","family"], 50, 1,
  "Counter-service pizza, burgers and rice bowls; a garden pizza and cheese pizza are on the menu.", {"veg": 1}),
 ("Ruby's Inn Cowboy's Buffet & Steak Room", 37.67369, -112.157, "food", "Bryce Canyon City", 25, 2, ["food","family"], 75, 2,
  "Log-cabin dining room with a lunch/dinner buffet and a large salad bar; a vegetarian burger is on the menu.", {"veg": 1}),
 ("The Pizza Place (Tropic)", 37.62413, -112.08205, "food", "Tropic Ditch", 65, 2, ["food","family"], 75, 2,
  "Crisp-crust pizza and local beer in Tropic; build-your-own and margherita options.", {"veg": 1}),
 ("Bryce Canyon Pines Restaurant", 37.7099, -112.2104, "food", "Bryce Canyon City", 55, 2, ["food","family"], 70, 2,
  "Roadside diner on SR-12 known for pie; salads and steamed sides if you skip the elk burger."),
 # ---- Kodachrome / Red Canyon / Panguitch
 ("Kodachrome Basin State Park", 37.51776, -111.99396, "park", "Kodachrome Basin", 75, 2, ["hiking","family","scenicdrive"], 180, 1,
  "Stone spires, Panorama Trail and Indian Cave, with showers and a small shop; paved road in.",
  {"rd": 24}),
 ("Red Canyon & Thunder Mountain arches", 37.74043, -112.29781, "scenic", "Red Canyon & Panguitch", 60, 2, ["scenicdrive","hiking"], 90, 0,
  "Hand-cut road tunnels on Scenic Byway 12 with short hikes and a bike path in Dixie National Forest.", {"rd": 14}),
 ("Red Canyon Visitor Center", 37.74613, -112.31939, "museum", "Red Canyon & Panguitch", 45, 2, ["museums","family"], 30, 0,
  "Dixie National Forest visitor center with short trails behind it.",
  {"seasonNote": "Google lists 10-3 hours now; may be seasonal.", "rd": 16}),
 ("Cowboy's Smokehouse Cafe", 37.82402, -112.43549, "food", "Red Canyon & Panguitch", 70, 2, ["food"], 70, 2,
  "Barbecue, steaks and breakfast on Panguitch's main street."),
 ("The Flying Goat", 37.81321, -112.4359, "food", "Red Canyon & Panguitch", 75, 2, ["food","relax"], 50, 1,
  "Panguitch coffee and breakfast diner with a bakery counter."),
 # ---- Cedar Breaks
 ("Cedar Breaks National Monument (Point Supreme)", 37.61498, -112.83855, "scenic", "Cedar Breaks", 70, 1, ["scenicdrive","hiking"], 120, 1,
  "Red-rock amphitheater above 10,000 ft; about 56 road miles west of Bryce via Panguitch and UT-143.",
  {"openMonths": [5,6,7,8,9,10], "seasonNote": "UT-148 is closed by snow outside roughly late May to October.", "rd": 56}),
 # ---- Zion from the east
 ("Zion Canyon Scenic Drive (by shuttle)", 37.28428, -112.94683, "scenic", "Zion National Park", 20, 2, ["scenicdrive","hiking"], 240, 0,
  "Zion Canyon's famous 6-mile corridor, ridden by shuttle in season. Riverside Walk at Temple of Sinawava is the easy pick.",
  {"seasonNote": "Shuttle schedule changes by season: 2026 service runs to Nov 28, pauses Nov 29 to Dec 25, resumes Dec 26 to Jan 2.", "rd": 92}),
 ("Canyon Overlook Trail (Zion)", 37.21364, -112.94333, "park", "Zion National Park", 45, 1, ["hiking","scenicdrive"], 60, 0,
  "1-mile round trip just east of the Mount Carmel tunnel, the first Zion stop from Bryce. SR-9 reopened Oct 9, 2026 after a rockfall, with a temporary gravel stretch.",
  {"rd": 76}),
 ("Checkerboard Mesa Viewpoint (Zion)", 37.22457, -112.88017, "scenic", "Zion National Park", 55, 2, ["scenicdrive"], 25, 0,
  "Roadside pullout on SR-9 near the East Entrance.", {"rd": 66}),
 # ---- Kanab
 ("Best Friends Animal Sanctuary", 37.12579, -112.54379, "activity", "Kanab", 80, 2, ["family","relax"], 120, 0,
  "Largest no-kill animal sanctuary in Angel Canyon, ~1.5 hours south of Bryce; free tours."),
 ("Coral Pink Sand Dunes State Park", 37.03774, -112.71443, "park", "Kanab", 65, 2, ["adventure","family"], 150, 1,
  "Coral-colored dunes with sandboard rentals; national park passes are not accepted."),
 ("Peekaboo Canyon Wood Fired Kitchen", 37.04788, -112.53344, "food", "Kanab", 70, 1, ["food","nightlife"], 80, 2,
  "Kanab's all-vegetarian-and-vegan restaurant with wood-fired pizza. Closed Mondays.", {"veg": 2}),
 ("Angel Village Cafe", 37.14085, -112.5432, "food", "Kanab", 85, 2, ["food"], 60, 1,
  "Plant-based buffet lunch at Best Friends, 11:30 to 1 daily.", {"veg": 2}),
 ("Rocking V Cafe", 37.04796, -112.5305, "food", "Kanab", 70, 1, ["food","art"], 80, 2,
  "Art-filled eatery in an 1892 mercantile; meats to vegan plates.", {"veg": 1}),
]
B_SOURCE = ("Hand-curated Nov 2026. Names and coordinates from Google Places; tags and notes editorial. "
            "Seasonal facts checked against NPS pages (Bryce shuttle runs early April to mid-October; guided rides April to Oct 31) "
            "and local reports as of Nov 10, 2026: verify with NPS (nps.gov/brca) before booking. "
            "distMi is approximate road miles from the Bryce Canyon Visitor Center.")

if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    zp = build("z", ZC, "Zion National Park", "UT", Z_BASE, Z, Z_SOURCE)
    bp = build("b", BC, "Bryce Canyon National Park", "UT", B_BASE, B, B_SOURCE)
    for slug, p in (("zion-national-park", zp), ("bryce-canyon-national-park", bp)):
        with open(os.path.join(outdir, slug + ".json"), "w") as f:
            json.dump(p, f, ensure_ascii=False, separators=(",", ":"))
        names = [i["name"] for i in p["items"]]
        assert len(names) == len(set(names)) or slug.startswith("bryce"), slug
        print(slug, p["count"], "items;",
              "food", sum(i["type"] == "food" for i in p["items"]),
              "veg>=1", sum(i.get("veg", 0) >= 1 for i in p["items"]),
              "far(>20)", sum(i["distMi"] > 20 for i in p["items"]),
              "overnight", sum(bool(i.get("overnight")) for i in p["items"]))
