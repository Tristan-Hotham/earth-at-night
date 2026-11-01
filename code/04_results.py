"""Step 4. data/results.json: every number quoted on the page, in the paper, blog, README, collage and Reddit post.
Rankings use countries with at least a million people (Natural Earth POP_EST) and at least 2,000 light units in 2012,
and cities with at least a million people whose 20 km disc averaged at least 2 nW/cm2/sr in 2012.
Run: python3 code/04_results.py
"""
import numpy as np
from common import *

st = jload(f"{WORK}/stats.json"); gm = jload(f"{WORK}/grid_meta.json"); pm = jload(f"{WORK}/page_meta.json")
iy = {y: k for k, y in enumerate(YEARS)}
W, LAND, LIT = st["world"], st["land"], st["lit_km2"]
CR = st["countries"]; byA = {r["a3"]: r for r in CR}
pct = lambda r: (r - 1) * 100


def crow(r):
    d = r["dip"] or {}
    return dict(a3=r["a3"], name=r["name"], region=r["region"], ratio=r["ratio"], pct=pct(r["ratio"]) if r["ratio"] else None,
                pct3=pct(r["ratio3"]) if r["ratio3"] else None, l0=r["l0"], l1=r["l1"], share0=r["share0"] * 100, share1=r["share1"] * 100,
                pp=r["pp1"] * 100 if r["pp1"] else None, pop_m=(r["pop"] or 0) / 1e6,
                dip=dict(peak_year=d["peak_year"], low_year=d["low_year"], fall=d["fall"] * 100) if d else None)


el = [r for r in CR if (r["pop"] or 0) >= 1e6 and r["l0"] >= 2000]
up = sorted(el, key=lambda r: -r["ratio"])
fell = [r for r in sorted(el, key=lambda r: r["ratio"]) if r["ratio"] < 1]
gain_tot = sum(r["l1"] - r["l0"] for r in CR)
gainers = sorted(CR, key=lambda r: -(r["l1"] - r["l0"]))
pp = sorted([r for r in el if r["pp1"]], key=lambda r: -r["pp1"])
dips = sorted([r for r in CR if r["dip"] and r["dip"]["peak"] >= 10000 and (r["pop"] or 0) >= 1e6], key=lambda r: -r["dip"]["fall"])
regs = {r["name"]: r for r in st["regions"]}
RK = {"East Asia & Pacific": "eap", "Europe & Central Asia": "eca", "Latin America & Caribbean": "lac", "Middle East & North Africa": "mena",
      "North America": "na", "South Asia": "sa", "Sub-Saharan Africa": "ssa"}
RN = {"eap": "East Asia and Pacific", "eca": "Europe and Central Asia", "lac": "Latin America and the Caribbean", "mena": "Middle East and North Africa",
      "na": "North America", "sa": "South Asia", "ssa": "Sub-Saharan Africa"}

# ---- cities ----
CT = st["cities"]
for c in CT:
    s = np.array(c["series"][iy[Y0]:])
    run = np.maximum.accumulate(s); f = 1 - s / np.where(run > 0, run, np.nan)
    j = int(np.nanargmax(f)) if np.isfinite(f).any() else 0
    c["dip"] = dict(peak_year=OBS[int(np.argmax(s[:j + 1]))], low_year=OBS[j], fall=float(f[j]) * 100 if np.isfinite(f[j]) else 0)
cel = [c for c in CT if c["pop"] >= 1e6 and c["mean0"] >= 2]
cup = sorted(cel, key=lambda c: -c["ratio"])
cdown = sorted(cel, key=lambda c: c["ratio"])


def city(c):
    return dict(name=c["name"], country=c["country"], pop_m=c["pop"] / 1e6, ratio=c["ratio"], pct=pct(c["ratio"]), lat=c["lat"], lon=c["lon"],
                l0=c["l0"], l1=c["l1"], series=[round(v) for v in c["series"]], dip=c["dip"])


byC = {}
for c in CT:
    byC.setdefault(c["name"], c)
NAMED = ["Kharkiv", "Aleppo", "Sanaa", "Khartoum", "Beirut", "Mosul", "Caracas", "Kathmandu", "Kumasi", "Addis Ababa", "Phnom Penh",
         "Baghdad", "Basra", "Paris", "London", "The Hague", "Kyiv", "Damascus", "Donetsk", "Zaporizhzhia", "Odesa", "Accra", "Lima",
         "Dar es Salaam", "Abidjan", "Nairobi", "Dhaka", "Delhi", "Lagos", "Kinshasa", "Kabul", "Maracaibo", "Rotterdam"]

ch = pm["change"]["cells"]; nlit = sum(ch.values())
sea = gm["sea_share_2024"]
R = dict(
    meta=dict(page=PAGE_URL, repo=REPO, slug=SLUG, y0=Y0, y1=Y1, years=YEARS, observed=OBS, modelled=MODEL),
    grid=dict(km15=360 / 2700 * 111.32, km7=360 / 5400 * 111.32, north=gm["nodata_north_of"], scale_ratio=gm["scale_ratio_2022_2021"],
              scale_cells=gm["n_ratio_cells"], sea_pct=sea * 100, dmsp_corr=gm["dmsp_corr"], n_cells_page=None, radius_km=st["radius_km"]),
    world=dict(l0=W[iy[Y0]] / 1e6, l1=W[iy[Y1]] / 1e6, pct=pct(W[iy[Y1]] / W[iy[Y0]]),
               pct3=pct(np.mean(W[iy[2022]:]) / np.mean(W[iy[2012]:iy[2014] + 1])),
               land0=LAND[iy[Y0]] / 1e6, land1=LAND[iy[Y1]] / 1e6,
               lit0=LIT[iy[Y0]] / 1e6, lit1=LIT[iy[Y1]] / 1e6, lit_pct=pct(LIT[iy[Y1]] / LIT[iy[Y0]]),
               lit_share0=LIT[iy[Y0]] / st["land_km2"] * 100, lit_share1=LIT[iy[Y1]] / st["land_km2"] * 100,
               m2000=W[0] / 1e6, m2011=W[iy[2011]] / 1e6, m_pct=pct(W[iy[2011]] / W[0]), jump=pct(W[iy[2012]] / W[iy[2011]]),
               pct_2013=pct(W[iy[2013]] / W[iy[2012]]), pct_2017=pct(W[iy[2017]] / W[iy[2016]]),
               series=[round(w / 1e6, 3) for w in W], fell_years=[y for y in OBS[1:] if W[iy[y]] < W[iy[y] - 1]]),
    reg={RK[k]: dict(name=RN[RK[k]], l0=v["l0"] / 1e6, l1=v["l1"] / 1e6, pct=pct(v["ratio"]), pct3=pct(v["ratio3"]), share0=v["share0"] * 100,
                     share1=v["share1"] * 100, pop_share=v["pop"] / st["pop_world"] * 100, pp=v["pp1"] * 100,
                     series=[round(x) for x in v["series"]]) for k, v in regs.items()},
    n=dict(eligible=len(el), with_light=sum(1 for r in CR if r["l0"] > 0), doubled=sum(r["ratio"] >= 2 for r in el), fell=len(fell),
           fell3=sum(r["ratio3"] < 1 for r in el), disagree=sum((r["ratio"] < 1) != (r["ratio3"] < 1) for r in el),
           tripled=sum(r["ratio"] >= 3 for r in el), fell10=sum(round(pct(r["ratio"])) <= -10 for r in el), obs_years=len(OBS), cities=len(CT), cities_el=len(cel), cities_fell=sum(c["ratio"] < 1 for c in cel)),
    up=[crow(r) for r in up[:20]],
    down=[crow(r) for r in fell],
    dis=[crow(r) for r in el if (r["ratio"] < 1) != (r["ratio3"] < 1)],
    gain=dict(chn_ind=(byA["CHN"]["l1"] - byA["CHN"]["l0"] + byA["IND"]["l1"] - byA["IND"]["l0"]) / gain_tot * 100,
              top=[dict(name=r["name"], share=(r["l1"] - r["l0"]) / gain_tot * 100) for r in gainers[:10]], total_m=gain_tot / 1e6),
    pp=dict(top=[crow(r) for r in pp[:10]], bottom=[crow(r) for r in pp[::-1][:10]], n=len(pp)),
    dips=[crow(r) for r in dips[:15]],
    c={a3: crow(byA[a3]) for a3 in ["CHN", "IND", "USA", "NPL", "KHM", "GHA", "TZA", "CIV", "SEN", "KEN", "ETH", "UKR", "YEM", "SYR", "FRA", "NLD",
                                     "GBR", "LBN", "VEN", "AFG", "IRQ", "SDN", "RUS", "NGA", "BGD", "DEU", "BEL", "CHE", "IRN", "GAB", "MMR",
                                     "COD", "ITA", "ESP", "JPN", "QAT", "LBY", "PAK", "BRA", "EST", "SAU", "UGA", "MWI", "NER"]},
    cup=[city(c) for c in cup[:20]],
    cdown=[city(c) for c in cdown[:20]],
    city={n: city(byC[n]) for n in NAMED},
    change=dict(cells=ch, n=nlit, up_share=(ch["up1"] + ch["up2"] + ch["up3"]) / nlit * 100, down_share=(ch["dark"] + ch["dim2"] + ch["dim1"]) / nlit * 100,
                dark_share=ch["dark"] / nlit * 100, same_share=ch["same"] / nlit * 100),
    retrieved="2026",
)
# Venezuela: light from the Monagas oil fields (box 64.5 to 62.5 W, 8.8 to 10.2 N), where the brightest cells are gas flares
S = np.load(f"{WORK}/viirs_2700.npy"); C = np.load(f"{WORK}/cty_2700.npy"); A = cell_area(1120)[:, None]
la, lo = row_lat(1120)[:, None], col_lon(2700)[None, :]
box = (lo >= -64.5) & (lo <= -62.5) & (la >= 8.8) & (la <= 10.2)
ven = C == [c for c in jload(f"{WORK}/countries.json")[1:] if c["a3"] == "VEN"][0]["i"]
vv = lambda y, m: float((np.nan_to_num(S[iy[y]]) * A)[m].sum())
R["ven"] = dict(monagas_share0=vv(Y0, ven & box) / vv(Y0, ven) * 100, monagas_share1=vv(Y1, ven & box) / vv(Y1, ven) * 100,
                rest_pct=pct(vv(Y1, ven & ~box) / vv(Y0, ven & ~box)), monagas_ratio=vv(Y1, ven & box) / vv(Y0, ven & box))
R["grid"]["km15r"] = round(R["grid"]["km15"]); R["grid"]["km7r"] = f"{R['grid']['km7']:.1f}"
R["gap"] = dict(na_ssa=int(R["reg"]["na"]["pp"] // R["reg"]["ssa"]["pp"]))
# ssa and the rest of the world
R["ssa_gap"] = R["reg"]["ssa"]["pop_share"] / R["reg"]["ssa"]["share1"]
jsave(R, f"{DATA}/results.json", indent=1)
print("world", round(R["world"]["pct"], 1), "3yr", round(R["world"]["pct3"], 1), "lit", round(R["world"]["lit_pct"], 1))
print("up", [(c["name"], round(c["ratio"], 2)) for c in R["up"][:10]])
print("down", [(c["name"], round(c["pct"])) for c in R["down"]])
print("cities up", [(c["name"], round(c["ratio"], 2)) for c in R["cup"][:12]])
print("cities down", [(c["name"], round(c["pct"])) for c in R["cdown"][:16]])
print("n", R["n"], "gain chn+ind", R["gain"]["chn_ind"])
print("change", {k: round(v, 1) for k, v in R["change"].items() if k != "cells"})
print("city dips", {n: (c["dip"]["peak_year"], c["dip"]["low_year"], round(c["dip"]["fall"])) for n, c in R["city"].items()})
