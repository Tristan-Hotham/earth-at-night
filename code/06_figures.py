"""Step 6. Figures for the blog post and the paper (release/blog/b_*.png) and the social card (header.png).
Every number drawn comes from data/results.json or from the same grids the results were computed from.
Run: python3 code/06_figures.py
"""
import json
import numpy as np
from matplotlib.patches import Rectangle
from figlib import *

OUT = os.path.join(ROOT, "release", "blog"); os.makedirs(OUT, exist_ok=True)
R = jload(f"{DATA}/results.json")
a12 = np.nan_to_num(np.load(f"{WORK}/viirs_5400_{Y0}.npy")); a24 = np.nan_to_num(np.load(f"{WORK}/viirs_5400_{Y1}.npy"))
S = np.load(f"{WORK}/viirs_2700.npy")
land5 = load_land(5400, 2240); land2 = load_land(2700, 1120)
SAVE = dict(dpi=200, facecolor=BG)


def world_img(rgba, land, width=2600):
    img = over(rgba, base_night(land))
    return equal_earth(img, TOP, BOT, width, bg=hex2rgb(BG))


def map_fig(rgba, land, title_note, legend_fn, name):
    ee, ext, _ = world_img(rgba, land)
    fig = plt.figure(figsize=(13, 7.3), facecolor=BG)
    ax = fig.add_axes([0, .12, 1, .88]); ax.imshow(ee, extent=ext, interpolation="lanczos"); ax.axis("off")
    lax = fig.add_axes([.06, .02, .88, .09]); lax.axis("off"); lax.set_xlim(0, 1); lax.set_ylim(0, 1)
    legend_fn(lax)
    lax.text(1, .05, title_note, ha="right", va="bottom", color=MUT, fontsize=9.5)
    fig.savefig(f"{OUT}/{name}", **SAVE); plt.close(fig)


def light_legend(lax):
    vs = np.exp(np.linspace(np.log(.5), np.log(255), 300))
    bar = over(night_rgba(vs)[None, :, :], hex2rgb(NIGHT)[None, None, :])
    lax.imshow(bar, extent=(0, .42, .55, .9), aspect="auto")
    for v in (1, 3, 10, 30, 100, 255):
        x = .42 * (np.log(v) - np.log(.5)) / (np.log(255) - np.log(.5))
        lax.plot([x, x], [.48, .55], color=FG, lw=.8); lax.text(x, .3, "255+" if v == 255 else str(v), ha="center", va="center", fontsize=9.5, color=FG)
    lax.text(.44, .72, "Average night light, nW/cm²/sr (log scale)", va="center", fontsize=10, color=FG)


def change_legend(lax):
    x = 0
    for k, lo, c in CHG[::-1]:
        lax.add_patch(Rectangle((x, .6), .018, .3, color=np.array(c) / 255))
        lab = CHG_LABEL[k]
        lax.text(x + .024, .75, lab, va="center", fontsize=8.6, color=FG)
        x += .024 + len(lab) * .0068 + .012
        if k == "same": x = 0
    # second row placement: redo in two rows for space
    lax.cla(); lax.axis("off"); lax.set_xlim(0, 1); lax.set_ylim(0, 1)
    rows = [CHG[::-1][:4], CHG[::-1][4:]]
    for j, row in enumerate(rows):
        x = 0; y = .78 - j * .38
        for k, lo, c in row:
            lax.add_patch(Rectangle((x, y - .13), .016, .26, color=np.array(c) / 255, ec="#00000040", lw=.4))
            lax.text(x + .022, y, CHG_LABEL[k], va="center", fontsize=9, color=FG)
            x += .022 + len(CHG_LABEL[k]) * .0072 + .02


# 1. world 2024
map_fig(night_rgba(glow(a24)), land5, "VIIRS annual night lights 2024, about 7 km cells; Equal Earth projection", light_legend, "b_world_2024.png")
# 2. change 2012 to 2024, as dots on the 15 km grid (cells that averaged at least 3 nW in either year)
s12, s24 = np.nan_to_num(S[YEARS.index(Y0)]), np.nan_to_num(S[YEARS.index(Y1)])
ee, ext, fwd = world_img(np.zeros(land5.shape + (4,), np.float32), land5)
fig = plt.figure(figsize=(13, 7.3), facecolor=BG)
ax = fig.add_axes([0, .12, 1, .88]); ax.imshow(ee, extent=ext, interpolation="lanczos"); ax.axis("off")
draw_change_dots(ax, fwd, s12, s24, scale=.55); ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
lax = fig.add_axes([.06, .02, .88, .09]); lax.axis("off"); lax.set_xlim(0, 1); lax.set_ylim(0, 1); change_legend(lax)
fig.text(.94, .005, "One dot per 15 km cell that averaged at least 3 nW in 2012 or 2024; bigger dots are brighter", ha="right", va="bottom", color=MUT, fontsize=9.5)
fig.savefig(f"{OUT}/b_change_map.png", **SAVE); plt.close(fig)

# 3. world series
fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG); ax.set_facecolor(BG)
ws = R["world"]["series"]; ys = YEARS
ax.axvspan(1999.6, 2011.5, color="#ECE5D8", lw=0)
ax.plot(ys[:12], ws[:12], color=GREY, lw=2.2, ls=(0, (5, 4)), marker="o", ms=5, mfc=BG)
ax.plot(ys[11:13], ws[11:13], color=GREY, lw=1, ls=":")
ax.plot(ys[12:], ws[12:], color=GOLD, lw=3, marker="o", ms=6)
ax.text(2005.75, 57, "modelled backwards\n(not observed)", ha="center", va="top", color=MUT, fontsize=10)
ax.text(2018, 57, "observed by VIIRS", ha="center", va="top", color=MUT, fontsize=10)
for y in (2012, 2024):
    v = ws[ys.index(y)]; ax.annotate(f"{v:.1f}m", (y, v), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=10.5, color=FG, fontweight="medium")
ax.set_ylim(0, 60); ax.set_xlim(1999.6, 2024.6); ax.set_ylabel("million light units", color=FG)
style(ax, axis="y"); ax.set_xticks(range(2000, 2025, 4))
fig.tight_layout(); fig.savefig(f"{OUT}/b_series.png", **SAVE); plt.close(fig)

# 4. regions
keys = ["na", "eca", "eap", "mena", "lac", "sa", "ssa"]
fig, ax = plt.subplots(figsize=(10, 4.8), facecolor=BG); ax.set_facecolor(BG)
for i, k in enumerate(keys):
    r = R["reg"][k]; y = len(keys) - 1 - i; col = GOLD if r["share1"] > r["share0"] else MAG
    ax.plot([r["pop_share"]] * 2, [y - .28, y + .28], color=GREY, lw=3, solid_capstyle="butt")
    ax.annotate("", (r["share1"], y), (r["share0"], y), arrowprops=dict(arrowstyle="-|>", color=col, lw=2.2, shrinkA=6, shrinkB=5))
    ax.plot(r["share0"], y, "o", ms=9, mfc=BG, mec=FG, mew=1.4); ax.plot(r["share1"], y, "o", ms=9, color=col)
    ax.text(-1, y, r["name"], ha="right", va="center", fontsize=10.5, color=FG)
ax.set_xlim(0, 32); ax.set_yticks([]); ax.set_xlabel("share of the world's light (%)", color=FG)
ax.plot([], [], "o", mfc=BG, mec=FG, label="2012"); ax.plot([], [], "o", color=GOLD, label="2024"); ax.plot([], [], "|", color=GREY, ms=12, mew=3, label="share of people")
ax.legend(frameon=False, loc="lower right", fontsize=10); style(ax)
ax.spines["left"].set_visible(False)
fig.tight_layout(); fig.subplots_adjust(left=.28); fig.savefig(f"{OUT}/b_regions.png", **SAVE); plt.close(fig)


# 5. brightened and dimmed countries
def div_bars(ax, rows, fs=10.5, light=True):
    for i, r in enumerate(rows):
        v = np.log2(r["ratio"]); y = len(rows) - 1 - i; up = v > 0
        ax.barh(y, v, color=GOLD if up else MAG, height=.72)
        ax.text(-.06 if up else .06, y, r["name"], ha="right" if up else "left", va="center", fontsize=fs, color=FG)
        ax.text(v + (.06 if up else -.06), y, f"×{r['ratio']:.1f}" if up else f"{round(r['pct'])}%", ha="left" if up else "right", va="center", fontsize=fs - 1, color=FG, fontweight="medium")
    ax.axvline(0, color=FG, lw=1)
    ax.set_xticks([-1, 0, 1, 2, 3]); ax.set_xticklabels(["half", "same", "×2", "×4", "×8"])
    ax.set_xlim(-1.6, 3.6); ax.set_yticks([]); ax.set_ylim(-.7, len(rows) - .3)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(colors=FG, labelsize=fs - 1); ax.grid(axis="x", color=RULE, lw=.8); ax.set_axisbelow(True)


rows = R["up"][:15] + sorted([d for d in R["down"] if round(d["pct"]) <= -10], key=lambda d: -d["ratio"])
fig, ax = plt.subplots(figsize=(10, 9.2), facecolor=BG); ax.set_facecolor(BG)
div_bars(ax, rows)
ax.set_xlabel("change in total light, 2012 to 2024 (doubling scale)", color=FG)
fig.tight_layout(); fig.savefig(f"{OUT}/b_countries.png", **SAVE); plt.close(fig)

# 6. city small multiples
CL = [("Kharkiv", 0), ("Aleppo", 0), ("Sanaa", 0), ("Khartoum", 0), ("Beirut", 0), ("The Hague", 0),
      ("Kathmandu", 1), ("Kumasi", 1), ("Addis Ababa", 1), ("Phnom Penh", 1), ("Mosul", 1), ("Baghdad", 1)]
fig, axs = plt.subplots(2, 6, figsize=(13, 4.8), facecolor=BG, sharex=True)
for ax, (n, up) in zip(axs.ravel(), CL):
    c = R["city"][n]; s = np.array(c["series"][12:]) / 1000; col = GOLD if up else MAG
    ax.set_facecolor(BG); ax.fill_between(OBS, s, color=col, alpha=.18, lw=0); ax.plot(OBS, s, color=col, lw=2.2)
    ax.set_title(n, fontproperties=DSEMI, fontsize=13, loc="left", color=FG, pad=14)
    sub = f"×{c['ratio']:.1f} since 2012" if up else f"-{round(c['dip']['fall'])}%, {c['dip']['peak_year']} to {c['dip']['low_year']}"
    ax.text(0, 1.02, f"{c['country']} · {sub}", transform=ax.transAxes, fontsize=8, color=MUT)
    ax.set_ylim(0, s.max() * 1.12); ax.set_xticks([2012, 2018, 2024]); ax.set_xticklabels(["2012", "", "2024"])
    style(ax, axis="y"); ax.tick_params(labelsize=8.5)
fig.text(.01, .5, "light within 20 km, thousand light units", rotation=90, va="center", color=MUT, fontsize=9)
fig.tight_layout(rect=(.015, 0, 1, 1)); fig.savefig(f"{OUT}/b_cities.png", **SAVE); plt.close(fig)


# 7. before and after pairs
def crop(arr, top, bot, lon0, lon1, lat0, lat1):
    h, w = arr.shape
    r0 = int((top - lat1) / (top - bot) * h); r1 = int((top - lat0) / (top - bot) * h)
    c0 = int((lon0 + 180) / 360 * w); c1 = int((lon1 + 180) / 360 * w)
    return arr[r0:r1, c0:c1]


PAIRS = [("Ukraine", (21.5, 41.0, 44.0, 53.0), (2021, 2023), "2700", "Ukraine before and after the full-scale invasion"),
         ("Nepal and the Ganges plain", (79.0, 89.5, 24.0, 31.0), (2012, 2024), "5400", "Nepal and the Ganges plain"),
         ("Ghana and Côte d'Ivoire", (-8.8, 1.8, 4.3, 11.2), (2012, 2024), "5400", "Ghana and Côte d'Ivoire")]
fig, axs = plt.subplots(3, 2, figsize=(11, 13.2), facecolor=BG)
for row, (nm, bb, yrs, res, ttl) in zip(axs, PAIRS):
    for ax, y in zip(row, yrs):
        if res == "5400":
            arr = a12 if y == 2012 else a24; land = land5
        else:
            arr = np.nan_to_num(S[YEARS.index(y)]); land = land2
        v = crop(arr, TOP, BOT, *bb); lm = crop(land, TOP, BOT, *bb)
        img = over(night_rgba(v), base_night(lm))
        asp = 1 / np.cos(np.radians((bb[2] + bb[3]) / 2))
        ax.imshow(img, extent=(bb[0], bb[1], bb[2], bb[3]), aspect=asp, interpolation="nearest" if res == "2700" else "bilinear")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_color(MUT)
        ax.set_title(f"{y}", fontproperties=DISP, fontsize=20, color=FG, loc="left")
    row[0].text(0, 1.13, ttl, transform=row[0].transAxes, fontproperties=DSEMI, fontsize=15, color=FG)
fig.tight_layout(h_pad=3); fig.savefig(f"{OUT}/b_pairs.png", **SAVE); plt.close(fig)

# 8. light per person
rows = R["pp"]["top"] + R["pp"]["bottom"][::-1]
fig, ax = plt.subplots(figsize=(10, 7.4), facecolor=BG); ax.set_facecolor(BG)
for i, r in enumerate(rows):
    y = len(rows) - 1 - i - (0 if i < 10 else .8)
    ax.plot([2, r["pp"]], [y, y], color=RULE, lw=1.4, zorder=1)
    ax.plot(r["pp"], y, "o", ms=9, color=GOLD if r["pp"] > 100 else INK, zorder=2)
    ax.text(r["pp"] * 1.13, y, f"{r['pp']:.0f}" if r["pp"] >= 10 else f"{r['pp']:.1f}", va="center", fontsize=9.5, color=FG)
    ax.text(1.8, y, r["name"], ha="right", va="center", fontsize=10.5, color=FG)
ax.set_xscale("log"); ax.set_xlim(2, 2500); ax.axvline(100, color=FG, ls=(0, (4, 3)), lw=1)
ax.text(104, len(rows) - .2, "world average = 100", fontsize=9.5, color=MUT, va="bottom")
ax.set_xticks([3, 10, 30, 100, 300, 1000]); ax.set_xticklabels(["3", "10", "30", "100", "300", "1,000"]); ax.set_yticks([])
style(ax); ax.spines["left"].set_visible(False); ax.set_xlabel("light per person, 2024 (log scale)", color=FG)
fig.tight_layout(); fig.subplots_adjust(left=.24); fig.savefig(f"{OUT}/b_per_person.png", **SAVE); plt.close(fig)

# ---- header.png, 1200 x 630 ----
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ee, ext, fwd = equal_earth(base_night(land5), TOP, BOT, 1500, lat_min=-45, lat_max=72, bg=hex2rgb(BG))
ax = fig.add_axes([.355, .1, .63, .8]); ax.imshow(ee, extent=ext, interpolation="lanczos"); ax.axis("off")
draw_change_dots(ax, fwd, s12, s24, scale=.32); ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
fig.text(.04, .80, "The Earth", fontproperties=DISP, fontsize=50, color=FG, va="baseline")
fig.text(.04, .66, "at night", fontproperties=DISP, fontsize=50, color=GOLD, va="baseline")
w = R["world"]
fig.text(.04, .53, f"Satellite night lights, 2012 to 2024.\nThe planet gave off {w['pct']:.0f}% more light;\nNepal's grew {R['c']['NPL']['ratio']:.1f} times, while Ukraine\nand Yemen lost half of theirs.", fontsize=13, color=FG, va="top", family=SER, linespacing=1.45)
fig.add_artist(Rectangle((.04, .17), .022, .03, transform=fig.transFigure, color=np.array(CHG[6][2]) / 255))
fig.text(.068, .185, "lit up", fontsize=11, color=FG, va="center")
fig.add_artist(Rectangle((.15, .17), .022, .03, transform=fig.transFigure, color=np.array(CHG[0][2]) / 255))
fig.text(.178, .185, "went dark", fontsize=11, color=FG, va="center")
fig.text(.04, .07, "maps.tristanhotham.com/earth-at-night", fontsize=11, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG); plt.close(fig)
print("figures:", sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
