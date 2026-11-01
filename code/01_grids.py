"""Step 1. Harmonised yearly grids, the country grid and the DMSP long-term average.

- Checks the extent of the VIIRS layers (city points from Natural Earth fall on the brightest offset) and the scale
  break between 2021 (tenths of a nW) and 2022 (whole nW), then writes every year 2000 to 2024 at 2700 x 1120
  (about 15 km at the equator) in whole nW/cm2/sr, and 2012 and 2024 at 5400 x 2240 (about 7 km).
- Rasterises Natural Earth 10m countries at 4 x 4 (2700 grid) or 2 x 2 (5400 grid) sub-cells and gives each cell to
  the country holding most of its land; cells with no land (sea, boats, platforms) belong to no country.
- Block-averages the 1 km DMSP 1992 to 2024 average to 5400 x 2100 and checks its extent (75 N to 65 S) against VIIRS.
Outputs (WORK): viirs_2700.npy (25 x 1120 x 2700), viirs_5400_2012.npy, viirs_5400_2024.npy, cty_2700.npy,
cty_5400.npy, countries.json, dmsp_5400.npy, grid_meta.json
Run: python3 code/01_grids.py
"""
import numpy as np
import rasterio.features, rasterio.transform
from shapely.geometry import shape
from common import *

meta = {}
# ---- scale break check ----
a21 = read_raw(raw_file("average_viirs", 2021)).astype(np.float64)
a22 = read_raw(raw_file("average_viirs", 2022)).astype(np.float64)
m = (a21 > 50) & (a22 > 0)
ratio = np.median(a22[m] / a21[m])
print("median 2022/2021 on bright cells", ratio)
assert .095 < ratio < .105
meta["scale_ratio_2022_2021"] = float(ratio)
meta["n_ratio_cells"] = int(m.sum())

# ---- extent check: Natural Earth cities with pop_max > 500,000 should sit on light ----
P = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]
pts = np.array([(p["properties"]["longitude"], p["properties"]["latitude"]) for p in P if (p["properties"]["pop_max"] or 0) > 5e5])
v12 = year_nw(2012, 5400)
best = None
for top in (87.17, 87.27, 87.37, 87.47, 87.57):
    r, c = rc(pts[:, 0], pts[:, 1], 5400, 2240, top, BOT)
    ok = (r >= 0) & (r < 2240)
    s = float(np.nanmean(np.log1p(v12[r[ok], c[ok]])))
    if best is None or s > best[1]: best = (top, s)
print("extent check: best top edge", best)
assert best[0] == TOP

# ---- yearly grids ----
stack = np.stack([year_nw(y) for y in YEARS]).astype(np.float32)
np.save(f"{WORK}/viirs_2700.npy", stack)
for y in (Y0, Y1):
    np.save(f"{WORK}/viirs_5400_{y}.npy", year_nw(y, 5400))
meta["nodata_rows_2700"] = int(np.isnan(stack[YEARS.index(2012)]).all(1).sum())
meta["nodata_north_of"] = float(row_lat(1120)[meta["nodata_rows_2700"]] + (TOP - BOT) / 1120 / 2)
print("observed years: rows of nodata at the top", meta["nodata_rows_2700"], "north of", meta["nodata_north_of"])

# ---- countries ----
F = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")["features"]
NAMES = {"People's Republic of China": "China", "United States of America": "United States", "Republic of the Congo": "Congo",
         "Democratic Republic of the Congo": "DR Congo", "The Bahamas": "Bahamas", "Ivory Coast": "Côte d'Ivoire",
         "The Gambia": "Gambia", "Republic of China": "Taiwan", "Federated States of Micronesia": "Micronesia",
         "East Timor": "Timor-Leste", "Kingdom of the Netherlands": "Netherlands"}
countries = [None]
shapes = []
for f in F:
    p = f["properties"]
    if p["ADM0_A3"] == "ATA":
        continue
    countries.append(dict(i=len(countries), a3=p["ADM0_A3"], iso=p["ISO_A3_EH"] if p["ISO_A3_EH"] != "-99" else p["ADM0_A3"],
                          name=NAMES.get(p["NAME_EN"] or p["NAME"], p["NAME_EN"] or p["NAME"]), short=p["NAME"], admin=p["ADMIN"], sov=p["SOVEREIGNT"],
                          type=p["TYPE"], pop=p["POP_EST"], pop_year=p["POP_YEAR"], region=p["REGION_WB"],
                          continent=p["CONTINENT"], subregion=p["SUBREGION"], income=p["INCOME_GRP"]))
    shapes.append((shape(f["geometry"]), len(countries) - 1))
jsave(countries, f"{WORK}/countries.json")


def country_grid(w, h, k):
    W, H = w * k, h * k
    T = rasterio.transform.from_bounds(-180, BOT, 180, TOP, W, H)
    fine = rasterio.features.rasterize(shapes, out_shape=(H, W), transform=T, fill=0, dtype="int16")
    sub = fine.reshape(h, k, w, k).transpose(0, 2, 1, 3).reshape(h, w, k * k)
    out = np.zeros((h, w), np.int16); best = np.zeros((h, w), np.int8)
    for q in range(k * k):
        v = sub[..., q]
        cnt = (sub == v[..., None]).sum(-1)
        take = (v > 0) & (cnt > best)
        out[take] = v[take]; best[take] = cnt[take]
    return out


c27 = country_grid(2700, 1120, 4); np.save(f"{WORK}/cty_2700.npy", c27)
c54 = country_grid(5400, 2240, 2); np.save(f"{WORK}/cty_5400.npy", c54)
print("country cells", int((c27 > 0).sum()), int((c54 > 0).sum()))
# light at sea (boats, platforms, coastal spill) on the 2700 grid, 2024
lit = np.nan_to_num(stack[YEARS.index(Y1)]) * cell_area(1120)[:, None]
meta["sea_share_2024"] = float(lit[c27 == 0].sum() / lit.sum())
print("share of 2024 light outside any country", meta["sea_share_2024"])

# ---- DMSP average, 1 km -> 1/15 degree ----
W, H = 43201, 16801
g = gzip.open(raw_file("average_dmsp", None, 43201))
dm = np.zeros((2100, 5400), np.float32)
for b in range(2100):
    blk = np.frombuffer(g.read(W * 2 * 8), "<u2").reshape(8, W)[:, :43200].astype(np.float32)
    dm[b] = blk.reshape(8, 5400, 8).mean(axis=(0, 2))
np.save(f"{WORK}/dmsp_5400.npy", dm)
v = np.nan_to_num(v12); v[v < 0] = 0
res = (TOP - BOT) / 2240
scores = {}
for top in (74.5, 75.0, 75.5):
    lat = top - (np.arange(2100) + .5) / 15
    i = np.round((TOP - lat) / res - .5).astype(int); ok = (i >= 0) & (i < 2240)
    scores[top] = float(np.corrcoef(np.log1p(dm[ok]).ravel(), np.log1p(v[i[ok]]).ravel())[0, 1])
print("DMSP extent check (correlation with VIIRS 2012 by top edge)", scores)
assert max(scores, key=scores.get) == DTOP
meta["dmsp_corr"] = scores[DTOP]
meta["dmsp_max_dn"] = float(dm.max())
# the DMSP std file in this extract is corrupt after ~2,900 rows (gzip 'invalid block type'), so it is not used
jsave(meta, f"{WORK}/grid_meta.json", indent=1)
