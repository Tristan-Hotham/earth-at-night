"""Step 2. Totals for the world, regions, countries and cities.

Light is summed as radiance times area: a cell of A km2 averaging v nW/cm2/sr adds v * A 'light units' (one unit is one
square kilometre shining at 1 nW/cm2/sr). Observed years (VIIRS, 2012 to 2024) carry every headline; the modelled years
2000 to 2011 are summed the same way over the same area (north of 75.1 N is missing in the observed layers, so it is left
out of every year) and reported separately.
- countries: every year, change 2012 to 2024 and between the three-year means 2012 to 2014 and 2022 to 2024 (a check
  on single-year noise), share of world light, light per person (Natural Earth POP_EST, about 2019) and the deepest fall
  from an earlier peak.
- regions: World Bank regions from Natural Earth.
- cities: Natural Earth populated places with at least 500,000 people (pop_max); light within 20 km of the point on the
  7 km grid (2012 and 2024 only) and on the 15 km grid for the yearly series.
Outputs: data/countries.csv, data/regions.csv, data/cities.csv, data/world_series.csv, WORK/stats.json
Run: python3 code/02_stats.py
"""
import csv
import numpy as np
from common import *

S = np.load(f"{WORK}/viirs_2700.npy")
C = np.load(f"{WORK}/cty_2700.npy")
CS = jload(f"{WORK}/countries.json")
A = cell_area(1120)[:, None]
nod = np.isnan(S[YEARS.index(Y0)])
S[:, nod] = np.nan
V = np.nan_to_num(S) * A                      # light units per cell, every year
n = len(CS)
iy = {y: k for k, y in enumerate(YEARS)}

# ---- world ----
world = V.sum(axis=(1, 2))
land = np.array([V[k][C > 0].sum() for k in range(len(YEARS))])
lit_km2 = np.array([A[:, 0][:, None].repeat(2700, 1)[(np.nan_to_num(S[k]) >= 1) & (C > 0)].sum() for k in range(len(YEARS))])
land_km2 = float(np.broadcast_to(A, C.shape)[C > 0].sum())
with open(f"{DATA}/world_series.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["year", "status", "light_units_all", "light_units_land", "lit_land_km2"])
    for k, y in enumerate(YEARS):
        w.writerow([y, "observed" if y in OBS else "modelled", round(world[k]), round(land[k]), round(lit_km2[k])])
print("world 2012", world[iy[Y0]] / 1e6, "2024", world[iy[Y1]] / 1e6, "x", world[iy[Y1]] / world[iy[Y0]])

# ---- countries ----
T = np.zeros((len(YEARS), n))
for k in range(len(YEARS)):
    T[k] = np.bincount(C.ravel(), weights=V[k].ravel(), minlength=n)
LIT = np.zeros((len(YEARS), n))
for k in range(len(YEARS)):
    LIT[k] = np.bincount(C.ravel(), weights=(np.broadcast_to(A, C.shape) * (np.nan_to_num(S[k]) >= 1)).ravel(), minlength=n)
AREA = np.bincount(C.ravel(), weights=np.broadcast_to(A, C.shape).ravel(), minlength=n)
tot_land = {y: T[iy[y], 1:].sum() for y in YEARS}
pop_world = sum(c["pop"] for c in CS[1:] if c["pop"] and c["pop"] > 0)
rows = []
for c in CS[1:]:
    i = c["i"]
    t = T[:, i]
    t0, t1 = t[iy[Y0]], t[iy[Y1]]
    m0 = t[iy[2012]:iy[2014] + 1].mean(); m1 = t[iy[2022]:iy[2024] + 1].mean()
    obs = t[iy[Y0]:]
    run = np.maximum.accumulate(obs)
    fall = 1 - obs / np.where(run > 0, run, np.nan)
    j = int(np.nanargmax(fall)) if np.isfinite(fall).any() and np.nanmax(fall) > 0 else None
    dip = None
    if j is not None:
        pk = int(np.argmax(obs[:j + 1]))
        dip = dict(peak_year=OBS[pk], low_year=OBS[j], fall=float(fall[j]), peak=float(obs[pk]), low=float(obs[j]))
    pop = c["pop"] if c["pop"] and c["pop"] > 0 else None
    rows.append(dict(a3=c["a3"], iso=c["iso"], name=c["name"], admin=c["admin"], type=c["type"], region=c["region"], continent=c["continent"],
                     pop=pop, pop_year=c["pop_year"], area_km2=float(AREA[i]), series=[float(x) for x in t],
                     l0=float(t0), l1=float(t1), ratio=float(t1 / t0) if t0 > 0 else None,
                     ratio3=float(m1 / m0) if m0 > 0 else None,
                     share0=float(t0 / tot_land[Y0]), share1=float(t1 / tot_land[Y1]),
                     pp1=(float(t1 / pop) / (tot_land[Y1] / pop_world)) if pop else None,
                     lit0=float(LIT[iy[Y0], i]), lit1=float(LIT[iy[Y1], i]), dip=dip))
with open(f"{DATA}/countries.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["adm0_a3", "iso_a3", "name", "region_wb", "continent", "population_est", "population_year", "land_km2",
                "light_2012", "light_2024", "change_2012_2024", "change_3yr_means", "share_of_world_2012", "share_of_world_2024",
                "light_per_person_index_2024", "lit_km2_2012", "lit_km2_2024", "deepest_fall", "deepest_fall_from", "deepest_fall_to"]
               + [f"light_{y}" + ("_modelled" if y in MODEL else "") for y in YEARS])
    for r in sorted(rows, key=lambda r: -r["l1"]):
        d = r["dip"] or {}
        w.writerow([r["a3"], r["iso"], dash(r["name"]), r["region"], r["continent"], r["pop"] or "", r["pop_year"], round(r["area_km2"]),
                    round(r["l0"]), round(r["l1"]), "" if r["ratio"] is None else round(r["ratio"] - 1, 4),
                    "" if r["ratio3"] is None else round(r["ratio3"] - 1, 4), round(r["share0"], 6), round(r["share1"], 6),
                    "" if r["pp1"] is None else round(r["pp1"] * 100, 1), round(r["lit0"]), round(r["lit1"]),
                    round(d["fall"], 4) if d else "", d.get("peak_year", ""), d.get("low_year", "")] + [round(x) for x in r["series"]])

# ---- regions ----
regs = {}
for r in rows:
    g = regs.setdefault(r["region"], dict(name=r["region"], series=np.zeros(len(YEARS)), pop=0))
    g["series"] += np.array(r["series"]); g["pop"] += r["pop"] or 0
reg_rows = []
for g in regs.values():
    s = g["series"]
    if s[iy[Y0]] <= 0:                          # Antarctic islands: no light
        continue
    reg_rows.append(dict(name=g["name"], series=s.tolist(), l0=float(s[iy[Y0]]), l1=float(s[iy[Y1]]), ratio=float(s[iy[Y1]] / s[iy[Y0]]),
                         ratio3=float(s[iy[2022]:].mean() / s[iy[2012]:iy[2014] + 1].mean()),
                         share0=float(s[iy[Y0]] / tot_land[Y0]), share1=float(s[iy[Y1]] / tot_land[Y1]), pop=g["pop"],
                         pp1=float(s[iy[Y1]] / g["pop"] / (tot_land[Y1] / pop_world)) if g["pop"] else None))
reg_rows.sort(key=lambda r: -r["l1"])
with open(f"{DATA}/regions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region_wb", "light_2012", "light_2024", "change_2012_2024", "change_3yr_means", "share_2012", "share_2024", "population_est", "light_per_person_index_2024"]
               + [f"light_{y}" + ("_modelled" if y in MODEL else "") for y in YEARS])
    for r in reg_rows:
        w.writerow([r["name"], round(r["l0"]), round(r["l1"]), round(r["ratio"] - 1, 4), round(r["ratio3"] - 1, 4), round(r["share0"], 5), round(r["share1"], 5),
                    r["pop"], round(r["pp1"] * 100, 1) if r["pp1"] else ""] + [round(x) for x in r["series"]])
for r in reg_rows:
    print(f"{r['name']:28s} {r['l0']/1e6:6.2f} {r['l1']/1e6:6.2f} x{r['ratio']:.2f} 3yr x{r['ratio3']:.2f} share {r['share0']:.3f}->{r['share1']:.3f}")

# ---- cities ----
a = np.nan_to_num(np.load(f"{WORK}/viirs_5400_{Y0}.npy")); b = np.nan_to_num(np.load(f"{WORK}/viirs_5400_{Y1}.npy"))
A5 = cell_area(2240, w=5400)[:, None]
lat5, lon5, lat2, lon2 = row_lat(2240), col_lon(5400), row_lat(1120), col_lon(2700)


def disc(lon, lat, latv, lonv, r0, c0, k):
    rr = np.arange(r0 - k, r0 + k + 1); cc = np.arange(c0 - k, c0 + k + 1) % len(lonv)
    rr = rr[(rr >= 0) & (rr < len(latv))]
    LA = np.radians(latv[rr])[:, None]; LO = np.radians(lonv[cc])[None, :]
    d = 6371 * np.arccos(np.clip(np.sin(LA) * np.sin(np.radians(lat)) + np.cos(LA) * np.cos(np.radians(lat)) * np.cos(LO - np.radians(lon)), -1, 1))
    return rr, cc, d


RAD = 20.0
CITY_NAMES = {"Zaporizhzhya": "Zaporizhzhia", "Odessa": "Odesa", "Kiev": "Kyiv", "Ho Chi Minh City": "Ho Chi Minh City"}
P = [p["properties"] for p in jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"] if (p["properties"]["pop_max"] or 0) >= 5e5]
cities = []
for p in P:
    lon, lat = p["longitude"], p["latitude"]
    if lat > 75 or lat < BOT: continue
    r, c = rc(lon, lat, 5400, 2240)
    rr, cc, d = disc(lon, lat, lat5, lon5, r, c, 5)
    m = d <= RAD
    s0 = float((a[np.ix_(rr, cc)] * A5[rr])[m].sum()); s1 = float((b[np.ix_(rr, cc)] * A5[rr])[m].sum())
    area = float(np.broadcast_to(A5[rr], d.shape)[m].sum())
    r2, c2 = rc(lon, lat)
    rr2, cc2, d2 = disc(lon, lat, lat2, lon2, r2, c2, 3)
    m2 = d2 <= RAD
    ser = [float(V[k][np.ix_(rr2, cc2)][m2].sum()) for k in range(len(YEARS))]
    cty = int(C[r2, c2]) or None
    cities.append(dict(name=CITY_NAMES.get(p["name"], p["name"]), country=p["adm0name"], a3=p["adm0_a3"], pop=int(p["pop_max"]), lat=lat, lon=lon,
                       l0=s0, l1=s1, ratio=s1 / s0 if s0 > 0 else None, area=area, mean0=s0 / area, mean1=s1 / area, series=ser,
                       capital=bool(p["adm0cap"]), megacity=bool(p["megacity"])))
cities.sort(key=lambda x: -x["pop"])
with open(f"{DATA}/cities.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "country", "adm0_a3", "population_max", "lat", "lon", "light_2012", "light_2024", "change_2012_2024",
                "mean_radiance_2012", "mean_radiance_2024"] + [f"light15km_{y}" + ("_modelled" if y in MODEL else "") for y in YEARS])
    for x in cities:
        w.writerow([dash(x["name"]), dash(x["country"]), x["a3"], x["pop"], round(x["lat"], 4), round(x["lon"], 4), round(x["l0"]), round(x["l1"]),
                    "" if x["ratio"] is None else round(x["ratio"] - 1, 4), round(x["mean0"], 2), round(x["mean1"], 2)] + [round(v) for v in x["series"]])
print("cities", len(cities))

stats = dict(world=world.tolist(), land=land.tolist(), lit_km2=lit_km2.tolist(), land_km2=land_km2, pop_world=pop_world,
             countries=rows, regions=reg_rows, cities=cities, radius_km=RAD)
jsave(stats, f"{WORK}/stats.json")
