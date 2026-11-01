"""Reddit collage: 'The Earth at night, 2012 to 2024'. A dark map panel of change in light inside a light paper page.
Sea labels point at coastal places with short leaders; inland or crowded places get numbered rings and a key on the
paper. Render-time checks (the script fails if any is broken): every label box, grown by 25 km, clears Natural Earth
50m land and every lit dot; no labels or rings overlap; no leader crosses another label or ring or runs more than 150 km
over land. Every number comes from data/results.json. Run: python3 reddit/collage.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import numpy as np
import matplotlib, matplotlib.patheffects as pe
from matplotlib.patches import Rectangle, FancyBboxPatch
from matplotlib.transforms import Bbox
from figlib import *

R = jload(f"{DATA}/results.json"); c, ci, w = R["c"], R["city"], R["world"]
S = np.load(f"{WORK}/viirs_2700.npy")
s12, s24 = np.nan_to_num(S[YEARS.index(Y0)]), np.nan_to_num(S[YEARS.index(Y1)])
land5 = load_land(5400, 2240)
x1 = lambda v: f"×{v:.1f}"
pc = lambda v: f"-{abs(round(v))}%"
W, H = 24, 31
fig = plt.figure(figsize=(W, H), dpi=110, facecolor=BG)

# ---- title ----
fig.text(.045, .962, "The Earth at night", fontproperties=DISP, fontsize=96, color=FG, va="top")
fig.text(.045, .903, "Where the world lit up, and where it went dark: satellite night lights, 2012 to 2024", fontsize=27, color=FG, family=SER, va="top")
stats = [(f"+{w['pct']:.0f}%", "more light seen from space\nin 2024 than in 2012", GOLD),
         (x1(c["NPL"]["ratio"]), "Nepal, the fastest\nbrightening country", GOLD),
         (f"{pc(c['UKR']['pct'])}", "Ukraine and Yemen:\nhalf their light gone", MAG),
         (f"{pc(c['FRA']['pct'])}", "France: new LED lamps and lights\nswitched off after midnight", MAG)]
for i, (b, t, col) in enumerate(stats):
    x = .045 + i * .235
    fig.text(x, .868, b, fontproperties=DISP, fontsize=58, color=col, va="top")
    fig.text(x, .826, t, fontsize=17, color=FG, va="top", linespacing=1.35)

# ---- the map panel ----
LATMIN, LATMAX = -50, 80
ee, ext, fwd = equal_earth(base_night(land5), TOP, BOT, 3200, lat_min=LATMIN, lat_max=LATMAX, bg=hex2rgb(BG))
# north of the observations (75.1 N) the panel is plain sea: paint the land there in sea colour too, so labels sit on sea
ax = fig.add_axes([.02, .43, .96, .335])
ax.imshow(ee, extent=ext, interpolation="lanczos"); ax.axis("off")
draw_change_dots(ax, fwd, s12, s24, scale=1.25)
ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
fig.text(.045, .418, "Change in light, 2012 to 2024: one dot for every 15 km cell that averaged at least 3 nW/cm²/sr in either year; bigger dots are brighter places",
         fontsize=15, color=MUT, va="top")

# Labels on open sea point at coastal places with short leaders; inland or crowded places get a small numbered ring
# and an entry in the key on the paper above the map. Checked below: every label box, grown by 25 km, clears
# Natural Earth 50m land and every lit dot; labels and rings do not overlap; no leader crosses another label or
# runs more than 150 km over land.
LAB = [  # text, coastal target(s) lon/lat, left-middle of the label lon/lat
    (f"France {pc(c['FRA']['pct'])}\nUK {pc(c['GBR']['pct'])}\nLEDs, lights\noff at night", [(-4.4, 48.4), (-5.2, 50.1)], (-40, 49)),
    (f"Yemen {pc(c['YEM']['pct'])}", [(49.2, 14.6)], (53, 10)),
    (f"India {x1(c['IND']['ratio'])}\nBangladesh\n{x1(c['BGD']['ratio'])}", [(77.5, 8.2), (90.3, 22.0)], (76, -8)),
    (f"China {x1(c['CHN']['ratio'])}", [(121.9, 31.0)], (146, 28)),
    (f"Ghana {x1(c['GHA']['ratio'])}\nCôte d'Ivoire {x1(c['CIV']['ratio'])}\nSenegal {x1(c['SEN']['ratio'])}", [(-0.2, 5.5), (-4.0, 5.2), (-17.4, 14.7)], (-34, -24)),
    (f"Tanzania {x1(c['TZA']['ratio'])}\nKenya {x1(c['KEN']['ratio'])}", [(39.7, -4.1), (39.3, -6.8)], (61.5, -18.5)),
    (f"United States\n+{c['USA']['pct']:.0f}%, still\nthe brightest", [(-118.3, 33.9)], (-162, 34)),
]
RINGS = [  # number, key text, place lon/lat
    (1, f"Ukraine {pc(c['UKR']['pct'])}", (31.5, 49.5)),
    (2, f"Syria {pc(c['SYR']['pct'])}, Lebanon {pc(c['LBN']['pct'])}", (36.4, 34.2)),
    (3, f"Khartoum {pc(ci['Khartoum']['dip']['fall'])} since 2022", (32.5, 15.6)),
    (4, f"Nepal {x1(c['NPL']['ratio'])}", (84.5, 27.9)),
    (5, f"Ethiopia {x1(c['ETH']['ratio'])}", (38.7, 9.0)),
    (6, f"Cambodia {x1(c['KHM']['ratio'])}", (104.9, 12.3)),
]
halo = [pe.withStroke(linewidth=5, foreground=NIGHT)]
texts = []
for t, targets, pos in LAB:
    lx, ly = fwd(*pos)
    tt = ax.text(lx, ly, t, color="#F4F1EA", fontsize=13, va="center", ha="left", fontweight="medium", path_effects=halo, zorder=10, linespacing=1.25)
    texts.append((tt, [fwd(*tg) for tg in targets]))
for k, txt, (lo, la) in RINGS:
    x_, y_ = fwd(lo, la)
    ax.plot(x_, y_, "o", ms=21, mfc=NIGHT, mec="#FFFFFF", mew=2, alpha=.92, zorder=12)
    ax.text(x_, y_, str(k), color="#FFFFFF", fontsize=12, ha="center", va="center", fontweight="bold", zorder=13)
# key, on paper above the map
kx = .045
fig.text(kx, .776, "Numbered on the map:", fontsize=15, color=MUT, va="center")
kx += .118
for k, txt, _ in RINGS:
    fig.add_artist(matplotlib.patches.Circle((kx, .776), .0055, transform=fig.transFigure, fc=BG, ec=FG, lw=1.6))
    fig.text(kx, .776, str(k), fontsize=11.5, color=FG, ha="center", va="center", fontweight="bold")
    tk = fig.text(kx + .009, .776, txt, fontsize=15, color=FG, va="center", fontweight="medium")
    fig.canvas.draw(); kx = tk.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted()).x1 + .02
assert kx < .97, kx
fig.canvas.draw()
rend = fig.canvas.get_renderer()
inv = ax.transData.inverted()
from shapely.geometry import shape, box as sbox, LineString, Point
from shapely.ops import unary_union, transform as stransform
land = unary_union([shape(f["geometry"]) for f in jload(f"{GEO}/ne_50m_land.geojson")["features"]]).intersection(sbox(-180, -60, 180, 84))
landp = stransform(lambda xx, yy, z=None: fwd(xx, yy), land)
land25 = landp.buffer(25000)
lboxes, lines = [], []
for i, (tt, tgs) in enumerate(texts):
    bb = tt.get_window_extent(rend).expanded(1.03, 1.06)
    d0 = inv.transform((bb.x0, bb.y0)); d1 = inv.transform((bb.x1, bb.y1))
    lboxes.append(sbox(d0[0], d0[1], d1[0], d1[1]))
    for tx, ty in tgs:
        ex = min(max(tx, d0[0]), d1[0]); ey = min(max(ty, d0[1]), d1[1])
        ax.plot([tx, ex], [ty, ey], color="#F4F1EA", lw=1.3, alpha=.9, zorder=9, solid_capstyle="round")
        ax.plot(tx, ty, "o", ms=7, mfc="none", mec="#FFFFFF", mew=1.8, zorder=11)
        lines.append((LineString([(tx, ty), (ex, ey)]), i))
rr = (inv.transform((0, 0)) - inv.transform((12, 0)))[0]          # ring radius (12 px) in metres
rings = [Point(*fwd(*p)).buffer(abs(rr)) for _, _, p in RINGS]
from pyproj import Transformer as _T
_inv = _T.from_crs("EPSG:8857", 4326, always_xy=True)
PROBLEMS = []
lon_, lat_, pk_, cls_ = change_points(s12, s24, min_nw=3); dx, dy = fwd(lon_, lat_)
from shapely import points as spoints, contains as scontains
dots = spoints(np.column_stack([dx, dy]))
names = [t.get_text().split(chr(10))[0] for t, _ in texts]
for i, b in enumerate(lboxes):
    if b.intersects(land25):
        hit = b.intersection(land25).centroid; print("LANDHIT", names[i], [round(v, 1) for v in _inv.transform(hit.x, hit.y)])
        PROBLEMS.append(("label within 25 km of land", names[i]))
    if scontains(b, dots).sum():
        m_ = scontains(b, dots); print("DOTHIT", names[i], list(zip(np.round(lon_[m_], 1), np.round(lat_[m_], 1)))[:5])
        PROBLEMS.append(("label over lit dots", names[i]))
    for j in range(i + 1, len(lboxes)):
        if b.intersects(lboxes[j]): PROBLEMS.append(("labels overlap", names[i], names[j]))
    for k, r in enumerate(rings):
        if b.intersects(r): PROBLEMS.append(("label over ring", names[i], k + 1))
for i in range(len(rings)):
    for j in range(i + 1, len(rings)):
        if rings[i].intersects(rings[j]): PROBLEMS.append(("rings overlap", i + 1, j + 1))
for ln, own in lines:
    for j, b in enumerate(lboxes):
        if j != own and ln.intersects(b): PROBLEMS.append(("leader crosses label", names[own], names[j]))
    for k, r in enumerate(rings):
        if ln.intersects(r): PROBLEMS.append(("leader crosses ring", names[own], k + 1))
    overland = ln.intersection(landp).length / 1000
    if overland > 150: PROBLEMS.append(("leader over land", names[own], round(overland)))
print("leader lengths over land (km):", [round(ln.intersection(landp).length / 1000) for ln, _ in lines])

# ---- legend ----
lax = fig.add_axes([.045, .372, .91, .026]); lax.axis("off"); lax.set_xlim(0, 1); lax.set_ylim(0, 1)
x = 0
for k, lo, col in CHG[::-1]:
    lax.add_patch(Rectangle((x, .2), .014, .6, color=np.array(col) / 255, ec="#00000055", lw=.6))
    lab = {"up3": "More than ×4, or new", "up2": "×2 to ×4", "up1": "Up a fifth to ×2", "same": "Within a fifth",
           "dim1": "Down a fifth to half", "dim2": "Down half to 3/4", "dark": "Down 3/4 or more"}[k]
    tt = lax.text(x + .018, .5, lab, va="center", fontsize=14.5, color=FG)
    fig.canvas.draw(); bb = tt.get_window_extent(fig.canvas.get_renderer()).transformed(lax.transData.inverted())
    x = bb.x1 + .022
assert x < 1.02, x

# ---- brightened against dimmed ----
bax = fig.add_axes([.17, .072, .33, .232]); bax.set_facecolor(BG)
rows = R["up"][:12] + sorted([d for d in R["down"] if round(d["pct"]) <= -10], key=lambda d: -d["ratio"])
for i, r in enumerate(rows):
    v = np.log2(r["ratio"]); y = len(rows) - 1 - i; up = v > 0
    bax.barh(y, v, color=GOLD if up else MAG, height=.74)
    bax.text(-.08 if up else .08, y, r["name"], ha="right" if up else "left", va="center", fontsize=14.5, color=FG)
    bax.text(v + (.07 if up else -.07), y, x1(r["ratio"]) if up else f"{round(r['pct'])}%", ha="left" if up else "right", va="center", fontsize=13.5, color=FG, fontweight="medium")
bax.axvline(0, color=FG, lw=1.2); bax.set_xlim(-1.45, 3.75); bax.set_ylim(-.7, len(rows) - .3); bax.set_yticks([])
bax.set_xticks([-1, 0, 1, 2, 3]); bax.set_xticklabels(["half", "same", "×2", "×4", "×8"], fontsize=13)
for s_ in ("top", "right", "left"): bax.spines[s_].set_visible(False)
bax.grid(axis="x", color=RULE); bax.set_axisbelow(True)
fig.text(.045, .338, "Brightened and dimmed", fontproperties=DSEMI, fontsize=30, color=FG, va="bottom")
fig.text(.045, .332, "Change in each country's light, 2012 to 2024, on a doubling scale. The 12 fastest\nrisers and every country that lost a tenth or more (countries of a million people or more).", fontsize=13.5, color=MUT, va="top", linespacing=1.35)

# ---- cities ----
fig.text(.55, .338, "Cities that went dark, and lit up", fontproperties=DSEMI, fontsize=30, color=FG, va="bottom")
fig.text(.55, .332, "Light within 20 km of each city, every year 2012 to 2024 (each scaled to its own peak).", fontsize=13.5, color=MUT, va="top")
CL = [("Kharkiv", 0), ("Aleppo", 0), ("Sanaa", 0), ("Khartoum", 0), ("Beirut", 0), ("The Hague", 0),
      ("Kathmandu", 1), ("Kumasi", 1), ("Addis Ababa", 1), ("Phnom Penh", 1), ("Mosul", 1), ("Baghdad", 1)]
for k, (nm, up) in enumerate(CL):
    col_, row_ = k % 3, k // 3
    cax = fig.add_axes([.55 + col_ * .145, .247 - row_ * .058, .125, .034]); cax.set_facecolor(BG)
    s_ = np.array(R["city"][nm]["series"][12:]); colr = GOLD if up else MAG
    cax.fill_between(OBS, s_, color=colr, alpha=.2, lw=0); cax.plot(OBS, s_, color=colr, lw=2.6)
    cax.set_ylim(0, s_.max() * 1.1); cax.set_xlim(2012, 2024); cax.axis("off")
    cax.plot([2012, 2024], [0, 0], color=MUT, lw=.8)
    cc = R["city"][nm]
    sub = f"{x1(cc['ratio'])} since 2012" if up else f"-{round(cc['dip']['fall'])}%, {cc['dip']['peak_year']} to {cc['dip']['low_year']}"
    cax.text(0, 1.62, nm, transform=cax.transAxes, fontproperties=DSEMI, fontsize=17, color=FG, va="top")
    cax.text(0, 1.2, sub, transform=cax.transAxes, fontsize=12, color=colr, va="top", fontweight="medium")
fig.text(.55, .066, "2012 to 2024 along each line. Kharkiv, Aleppo, Sanaa, Khartoum: war. Beirut: economic\ncollapse. The Hague: greenhouse lighting cut in 2022, and LEDs. Mosul fell after 2014.", fontsize=12, color=MUT, va="top", linespacing=1.35)

# ---- footer ----
fig.add_artist(Rectangle((.045, .044), .91, .0012, transform=fig.transFigure, color=FG))
fig.text(.045, .037, "Data: Annual VIIRS Night Lights V2 (Earth Observation Group, Colorado School of Mines; Elvidge et al. 2021), yearly layers by T. Hengl, OpenGeoHub (Zenodo, CC BY 4.0), at about 15 km;\n"
         "countries, populations and cities: Natural Earth. Light = radiance × area. The 2022 to 2024 layers were rescaled to match earlier years. The satellite passes at about 1.30 am and does not see blue light,\n"
         "so LED street lamps and lights switched off after midnight look like dimming; gas flares at oil fields count as light. Analysis and chart: Tristan Hotham, with Python and matplotlib.",
         fontsize=12.5, color=MUT, va="top", linespacing=1.45)
fig.text(.955, .953, "maps.tristanhotham.com/earth-at-night", fontsize=19, color=FG, ha="right", va="top", fontweight="medium")
out = os.path.join(ROOT, "reddit", "earth_at_night.png")
fig.savefig(out, dpi=110, facecolor=BG); plt.close(fig)
from PIL import Image
print(out, Image.open(out).size)
print("label problems:", PROBLEMS)
assert not PROBLEMS or os.environ.get("COLLAGE_DRAFT")
