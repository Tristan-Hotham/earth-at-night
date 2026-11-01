"""Step 3. Map layers and page data.

- data/tiles/lights_<year>.png: one Web Mercator image per year (2000 to 2024) from the 15 km grid, 2700 px wide,
  latitude 75.1 N to 62 S (north of 75.1 N there are no observations); 8-bit palette, the palette index is the
  radiance in whole nW/cm2/sr (255 = 255 or more), so the colours are fixed and the files small.
- data/tiles/lights_<year>_7km.png: 2012 and 2024 from the 7 km grid (5400 px wide), used when zoomed in.
- data/tiles/change_7km.png: change 2012 to 2024 on the 7 km grid in seven classes, three strengths each.
- data/tiles/dmsp_avg.png: the DMSP-style 1 km average over 1992 to 2024, block-averaged to 1/15 degree.
- data/page/cells/<block>.json: yearly values of every cell (15 km grid) that was ever lit, in 10 degree blocks,
  loaded when someone clicks the map.
- data/page/borders.json: Natural Earth 1:50m country outlines, simplified, keyed by ADM0_A3.
- data/page/cities.json and data/page/countries.json: city and country summaries for popups, search and charts.
Run: python3 code/03_page_data.py
"""
import numpy as np
from PIL import Image
from shapely.geometry import shape, mapping
from common import *

TD = os.path.join(DATA, "tiles"); os.makedirs(TD, exist_ok=True)
CD = os.path.join(PAGE, "cells"); os.makedirs(CD, exist_ok=True)
NORTH = 75.1                                   # observed layers stop here

# ---- the night palette: index = whole nW (0 transparent) ----
STOPS = [(0.5, (52, 38, 112, 120)), (1, (78, 48, 140, 170)), (3, (142, 62, 160, 215)), (8, (218, 92, 96, 240)), (20, (248, 152, 52, 252)),
         (50, (255, 206, 92, 255)), (120, (255, 238, 170, 255)), (255, (255, 255, 245, 255))]


def night_rgba(v):
    v = np.asarray(v, float); out = np.zeros(v.shape + (4,))
    xs = np.log([s[0] for s in STOPS]); cs = np.array([s[1] for s in STOPS], float)
    lv = np.log(np.maximum(v, .01))
    for k in range(4):
        out[..., k] = np.interp(lv, xs, cs[:, k])
    out[v < .5] = 0
    return out


PAL = night_rgba(np.arange(256)).round().astype(np.uint8)
jsave(dict(stops=STOPS), f"{WORK}/palette.json")


def merc_rows(h_src, top, bot, width, north=NORTH, south=BOT):
    """Source row for every output row of a Web Mercator image of the given width covering north..south."""
    y = lambda la: np.log(np.tan(np.pi / 4 + np.radians(la) / 2))
    s = width / (2 * np.pi)
    y0, y1 = y(north), y(south)
    H = int(round((y0 - y1) * s))
    yc = y0 - (np.arange(H) + .5) / s
    lat = np.degrees(2 * np.arctan(np.exp(yc)) - np.pi / 2)
    r = np.floor((top - lat) / (top - bot) * h_src).astype(int)
    return np.clip(r, 0, h_src - 1), H


def save_pal(idx, path, pal=PAL):
    im = Image.fromarray(idx.astype(np.uint8), "P")
    im.putpalette(pal[:, :3].ravel().tolist())
    im.info["transparency"] = bytes(pal[:, 3].tolist())
    im.save(path, optimize=True, transparency=bytes(pal[:, 3].tolist()))


S = np.load(f"{WORK}/viirs_2700.npy")
nod = np.isnan(S[YEARS.index(Y0)])
rows27, H27 = merc_rows(1120, TOP, BOT, 2700)
sizes = {}
for k, y in enumerate(YEARS):
    v = np.nan_to_num(S[k]); v[nod] = 0
    idx = np.clip(np.round(v), 0, 255)[rows27]
    save_pal(idx, f"{TD}/lights_{y}.png"); sizes[y] = os.path.getsize(f"{TD}/lights_{y}.png")
print("year images", H27, "px tall,", sum(sizes.values()) // 1024, "KB")
rows54, H54 = merc_rows(2240, TOP, BOT, 5400)
for y in (Y0, Y1):
    v = np.nan_to_num(np.load(f"{WORK}/viirs_5400_{y}.npy"))
    save_pal(np.clip(np.round(v), 0, 255)[rows54], f"{TD}/lights_{y}_7km.png")

# ---- change 2012 to 2024 (7 km) ----
a = np.nan_to_num(np.load(f"{WORK}/viirs_5400_{Y0}.npy")); b = np.nan_to_num(np.load(f"{WORK}/viirs_5400_{Y1}.npy"))
CH = [  # key, label, lower bound of ratio (exclusive of the next), colour
    ("dark", "Went dark: fell by three quarters or more", 0, (214, 40, 160)),
    ("dim2", "Fell by half to three quarters", .25, (236, 102, 190)),
    ("dim1", "Fell by a fifth to a half", .5, (240, 170, 220)),
    ("same", "Within a fifth of 2012", .8, (150, 156, 170)),
    ("up1", "Rose by a fifth to double", 1.2, (255, 226, 140)),
    ("up2", "Doubled to quadrupled", 2, (255, 190, 50)),
    ("up3", "More than quadrupled, or new light", 4, (255, 140, 0)),
]
ratio = (b + .5) / (a + .5)
cls = np.digitize(ratio, [c[2] for c in CH[1:]])            # 0..6
peak = np.maximum(a, b)
strength = np.digitize(peak, [6, 30])                       # 0: 2 to 5 nW, 1: 6 to 29, 2: 30+
show = peak >= 2
cidx = np.where(show, 1 + cls * 3 + strength, 0)
cpal = np.zeros((256, 4), np.uint8)
for i, c in enumerate(CH):
    for s, al in enumerate((120, 190, 255)):
        cpal[1 + i * 3 + s] = (*c[3], al)
save_pal(cidx[rows54], f"{TD}/change_7km.png", cpal)
chg = dict(classes=[dict(key=c[0], label=c[1], lo=c[2], rgb=c[3]) for c in CH], min_nw=2,
           cells={c[0]: int(((cls == i) & show).sum()) for i, c in enumerate(CH)})
print("change classes", chg["cells"])

# ---- DMSP average ----
dm = np.load(f"{WORK}/dmsp_5400.npy")
rowsd, Hd = merc_rows(2100, DTOP, DBOT, 5400, north=min(NORTH, DTOP), south=BOT)
DST = [(1, (40, 70, 110, 90)), (4, (60, 120, 170, 160)), (12, (110, 180, 210, 210)), (30, (190, 230, 240, 245)), (63, (255, 255, 255, 255))]
dpal = np.zeros((256, 4))
xs = np.log([s[0] for s in DST]); cs = np.array([s[1] for s in DST], float)
for k in range(4):
    dpal[1:64, k] = np.interp(np.log(np.arange(1, 64)), xs, cs[:, k])
dpal = dpal.round().astype(np.uint8)
di = np.clip(np.round(dm), 0, 63)
di[di < 1] = 0
save_pal(di[rowsd], f"{TD}/dmsp_avg.png", dpal)
jsave(dict(stops=DST), f"{WORK}/dmsp_palette.json")
merc_meta = dict(north=NORTH, south=BOT, dmsp_north=min(NORTH, DTOP))

# ---- cells for clicks ----
lat2, lon2 = row_lat(1120), col_lon(2700)
Vi = np.nan_to_num(S).round().astype(np.int32)
Vi[:, nod] = -1
ever = (Vi[YEARS.index(Y0):] >= 1).any(0)
n_blocks = 0
for la0 in range(-70, 80, 10):
    for lo0 in range(-180, 180, 10):
        rr = np.where((lat2 >= la0) & (lat2 < la0 + 10))[0]; cc = np.where((lon2 >= lo0) & (lon2 < lo0 + 10))[0]
        if not len(rr): continue
        sub = ever[np.ix_(rr, cc)]
        if not sub.any(): continue
        out = []
        for r, c in zip(*np.where(sub)):
            out.append([int(rr[r]), int(cc[c])] + Vi[:, rr[r], cc[c]].tolist())
        jsave(out, f"{CD}/{la0}_{lo0}.json"); n_blocks += 1
print("cell blocks", n_blocks, "cells", int(ever.sum()))

# ---- borders ----
F = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]
feats = []
for f in F:
    p = f["properties"]
    if p["ADM0_A3"] == "ATA": continue
    g = shape(f["geometry"]).simplify(.03, preserve_topology=True)
    gj = mapping(g)
    rnd = lambda x: [round(x[0], 3), round(x[1], 3)]
    if gj["type"] == "Polygon":
        co = [[rnd(q) for q in ring] for ring in gj["coordinates"]]
    else:
        co = [[[rnd(q) for q in ring] for ring in poly] for poly in gj["coordinates"]]
    feats.append(dict(type="Feature", properties=dict(a3=p["ADM0_A3"]), geometry=dict(type=gj["type"], coordinates=co)))
jsave(dict(type="FeatureCollection", features=feats), f"{PAGE}/borders.json")

# ---- countries and cities for the page ----
st = jload(f"{WORK}/stats.json")
pc = {}
for r in st["countries"]:
    if r["l0"] <= 0 and r["l1"] <= 0: continue
    pc[r["a3"]] = dict(n=r["name"], r=r["region"], p=r["pop"], s=[round(x) for x in r["series"]], c=r["ratio"], c3=r["ratio3"],
                       sh=round(r["share1"], 5), pp=round(r["pp1"] * 100, 1) if r["pp1"] else None,
                       d=[r["dip"]["peak_year"], r["dip"]["low_year"], round(r["dip"]["fall"], 3)] if r["dip"] else None)
jsave(pc, f"{PAGE}/countries.json")
cit = [[c["name"], c["country"], round(c["lat"], 3), round(c["lon"], 3), c["pop"], round(c["l0"]), round(c["l1"]), [round(v) for v in c["series"]]] for c in st["cities"]]
jsave(cit, f"{PAGE}/cities.json")
jsave(dict(merc=merc_meta, change=chg, H27=H27, H54=H54, Hd=Hd, sizes=sizes), f"{WORK}/page_meta.json")
print("page files:", {f: os.path.getsize(f"{PAGE}/{f}") // 1024 for f in os.listdir(PAGE) if f.endswith(".json")})
