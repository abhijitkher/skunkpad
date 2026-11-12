#!/usr/bin/env python3
"""Apply seasonal tags (openMonths / best / seasonNote) to the hand-built pools.
Run after gen_pools.py:  python3 tools/season_tags.py pools
Sources: NPS Zion + Bryce pages, park alerts, Springdale restaurant sites (checked Nov 2026)."""
import json,sys,os
d=sys.argv[1] if len(sys.argv)>1 else "pools"
Z={
 "z05":dict(seasonNote="Paved walk is open all year but sections can close for ice in winter."),
 "z06":dict(best=[5,6,7,8,9,10],seasonNote="Closed when the river runs above 150 cfs or on flash flood warnings (closed in early Nov 2026). Winter means drysuit territory."),
 "z07":dict(best=[3,4,5,9,10,11],seasonNote="Permit needed year-round (lottery; winter is day-before lottery only). Chains get icy in winter; Scout Lookout needs no permit."),
 "z11":dict(seasonNote="Zion Canyon route closed after a rockfall (Nov 2026); reachable only from the east side (East Mesa Trail)."),
 "z19":dict(seasonNote="Dinner only. Daily March to Thanksgiving, then Thursday to Sunday in winter; closed Thanksgiving and Christmas."),
 "z16":dict(seasonNote="Known as one of the reliable year-round spots in Springdale."),
 "z18":dict(seasonNote="Known as one of the reliable year-round spots in Springdale; winter hours can vary."),
 "z26":dict(seasonNote="Kolob Canyons Road is open most of the year but closes often for snow or ice in winter."),
 "z27":dict(seasonNote="Kolob Canyons Road is open most of the year but closes often for snow or ice in winter."),
 "z33":dict(best=[10,11,12,1,2,3,4]),
 "z41":dict(best=[3,4,5,9,10,11],seasonNote="Sand gets very hot midday in summer."),
}
B={
 "b06":dict(seasonNote="Wall Street side closes every winter, and in Nov 2026 both Navajo Loop sides were closed until further notice. Queen's Garden stays open."),
 "b07":dict(seasonNote="Bryce Connector Trail (Bryce Point to Peekaboo) closed until further notice as of Nov 2026."),
 "b08":dict(seasonNote="Fairyland Point road closes to cars all winter; walking in adds about a mile."),
 "b09":dict(seasonNote="Road closes to cars for the whole winter once snow needs plowing; walk, ski or snowshoe in."),
 "b11":dict(openMonths=[3,4,5,6,7,8,9,10,11],seasonNote="Lodge season runs March 1 to Nov 30; dining room has no winter hours."),
 "b12":dict(seasonNote="Southern drive closes temporarily after winter storms; check NPS."),
 "b13":dict(seasonNote="Southern drive closes temporarily after winter storms; check NPS."),
 "b15":dict(seasonNote="Waterfall flows seasonally; the cave fills with icicles in winter."),
 "b19":dict(seasonNote="Hours: Nov to Dec noon to 8, closed mid-Jan to mid-Feb, otherwise daily (breakfast Apr to Oct)."),
 "b26":dict(seasonNote="Shuttle runs to Nov 28; none Nov 29 to Dec 25 (you can drive the canyon yourself); holiday shuttle Dec 26 to Jan 2."),
}
for f,T in (("zion-national-park.json",Z),("bryce-canyon-national-park.json",B)):
    p=os.path.join(d,f);j=json.load(open(p))
    for it in j["items"]:
        if it["id"] in T: it.update(T[it["id"]])
    json.dump(j,open(p,"w"),separators=(",",":"),ensure_ascii=False)
    print(f,sum(1 for i in j["items"] if i["id"] in T),"tagged")
