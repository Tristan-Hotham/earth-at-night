"""Shared drawing helpers for the figures, the header and the collage: fonts (static instances cut from the variable
Fraunces), the page's palettes, and night-light images on a lon/lat grid reprojected to Equal Earth."""
import os, sys
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (600, "Semibold")):
        instancer.instantiateVariableFont(TTFont(os.path.join(FONTS, "FrauncesVar.ttf")), {"wght": w, "opsz": 144 if w == 900 else 36, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
for f in ["IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(os.path.join(FONTS, f))
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DSEMI = fm.FontProperties(fname=f"{FD}/Fraunces-Semibold.ttf")
SER, MONO = "Source Serif 4", "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 11})
BG, FG, MUT, RULE, PAPER = "#F6F2EA", "#161A2C", "#5E5F6E", "#DDD4C4", "#FCFAF6"
INK, GOLD, MAG, DUSK, GREY, NIGHT, NLAND = "#232A57", "#B8790F", "#B4237E", "#3B2F78", "#8A8C99", "#0B0E1C", "#181C33"
GOLDB, MAGB = "#F2A626", "#D63AA0"          # brighter versions for dark panels

STOPS = [(0.5, (52, 38, 112, 120)), (1, (78, 48, 140, 170)), (3, (142, 62, 160, 215)), (8, (218, 92, 96, 240)), (20, (248, 152, 52, 252)),
         (50, (255, 206, 92, 255)), (120, (255, 238, 170, 255)), (255, (255, 255, 245, 255))]
CHG = [("dark", 0, (214, 40, 160)), ("dim2", .25, (236, 102, 190)), ("dim1", .5, (240, 170, 220)), ("same", .8, (150, 156, 170)),
       ("up1", 1.2, (255, 226, 140)), ("up2", 2, (255, 190, 50)), ("up3", 4, (255, 140, 0))]
CHG_LABEL = {"dark": "Fell by three quarters or more", "dim2": "Fell by half to three quarters", "dim1": "Fell by a fifth to a half",
             "same": "Within a fifth of 2012", "up1": "Rose by a fifth to double", "up2": "Doubled to quadrupled", "up3": "More than quadrupled, or new"}


def night_rgba(v):
    """RGBA (0..1) for radiance in whole nW, as on the page."""
    v = np.asarray(v, float); out = np.zeros(v.shape + (4,), np.float32)
    xs = np.log([s[0] for s in STOPS]); cs = np.array([s[1] for s in STOPS], float) / 255
    lv = np.log(np.maximum(v, .01))
    for k in range(4):
        out[..., k] = np.interp(lv, xs, cs[:, k])
    out[v < .5] = 0
    return out


def over(rgba, base):
    """Composite rgba (h, w, 4) over an opaque base colour or image (h, w, 3)."""
    a = rgba[..., 3:4]
    return rgba[..., :3] * a + np.asarray(base, np.float32) * (1 - a)


def hex2rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255


def change_rgba(a, b, min_nw=2):
    ratio = (b + .5) / (a + .5)
    cls = np.digitize(ratio, [c[1] for c in CHG[1:]])
    peak = np.maximum(a, b)
    strength = np.digitize(peak, [6, 30])
    cols = np.array([c[2] for c in CHG], np.float32) / 255
    out = np.zeros(a.shape + (4,), np.float32)
    out[..., :3] = cols[cls]
    out[..., 3] = np.array([.5, .78, 1.0], np.float32)[strength]
    out[peak < min_nw] = 0
    return out


def base_night(land):
    """Dark sea and slightly lighter land, (h, w, 3)."""
    img = np.empty(land.shape + (3,), np.float32)
    img[:] = hex2rgb(NIGHT); img[land] = hex2rgb(NLAND)
    return img


def style(ax, grid=True, axis="x"):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(MUT)
    ax.tick_params(colors=FG, labelsize=10)
    if grid: ax.grid(axis=axis, color=RULE, lw=.8); ax.set_axisbelow(True)


def equal_earth(img, top, bot, width, lat_min=-58, lat_max=76, bg=(1, 1, 1), lon0=0):
    """Reproject a lon/lat image (rows from top to bot, 360 degrees wide) to Equal Earth. Returns RGBA, extent and a
    lon/lat -> x/y function."""
    from pyproj import Transformer
    crs = "EPSG:8857" if lon0 == 0 else f"+proj=eqearth +lon_0={lon0} +datum=WGS84 +units=m +no_defs"
    fwd = Transformer.from_crs(4326, crs, always_xy=True); inv = Transformer.from_crs(crs, 4326, always_xy=True)
    X0, _ = fwd.transform(lon0 - 180 + 1e-9, 0); X1, _ = fwd.transform(lon0 + 180 - 1e-9, 0)
    _, Y0 = fwd.transform(lon0, lat_min); _, Y1 = fwd.transform(lon0, lat_max)
    height = int(round(width * (Y1 - Y0) / (X1 - X0)))
    xs = np.linspace(X0, X1, width); ys = np.linspace(Y1, Y0, height)
    h, w = img.shape[:2]; ch = img.shape[2]
    out = np.zeros((height, width, 4), np.float32)
    for a in range(0, height, 300):
        XX, YY = np.meshgrid(xs, ys[a:a + 300])
        lo, la = inv.transform(XX, YY)
        ok = np.isfinite(lo) & np.isfinite(la) & (np.abs(lo) <= 180)
        xb, _ = fwd.transform(np.where(ok, lo, 0), np.where(ok, la, 0))
        ok &= np.abs(xb - XX) < 1000
        lo = ((lo + 180) % 360) - 180
        ri = np.clip(((top - la) / (top - bot) * h).astype(int), 0, h - 1)
        ci = np.clip(((lo + 180) / 360 * w).astype(int), 0, w - 1)
        blk = img[ri, ci][..., :3].copy(); blk[~ok] = bg
        out[a:a + 300, :, :3] = blk; out[a:a + 300, :, 3] = ok
    return out, (X0, X1, Y0, Y1), lambda lo, la: fwd.transform(lo, la)


def load_land(w=5400, h=2240):
    c = np.load(f"{WORK}/cty_{w}.npy")
    return c > 0


def glow(v, sigma=1.6, k=2.2):
    """Brighten small lights for world-scale maps: each cell takes the larger of its own value and a blurred halo."""
    from scipy.ndimage import gaussian_filter, maximum_filter
    v = np.nan_to_num(np.asarray(v, np.float32))
    return np.maximum(maximum_filter(v, size=2), gaussian_filter(v, sigma) * k)


def change_points(a, b, top=TOP, bot=BOT, min_nw=3):
    """Cells (lon, lat, peak radiance, class index) of the change map, dimmest first, for dot maps."""
    h, w = a.shape
    peak = np.maximum(a, b); m = peak >= min_nw
    r, c = np.where(m)
    ratio = (b[m] + .5) / (a[m] + .5)
    cls = np.digitize(ratio, [x[1] for x in CHG[1:]])
    lat = top - (top - bot) * (r + .5) / h; lon = -180 + 360 * (c + .5) / w
    o = np.argsort(peak[m])
    return lon[o], lat[o], peak[m][o], cls[o]


def draw_change_dots(ax, fwd, a, b, scale=1.0, min_nw=3):
    lon, lat, pk, cls = change_points(a, b, min_nw=min_nw)
    x, y = fwd(lon, lat)
    cols = np.array([c[2] for c in CHG], np.float32) / 255
    s = (np.clip(np.log2(pk / min_nw + 1), 0, 7) ** 1.6 * .9 + .4) * scale
    ax.scatter(x, y, s=s * 7, c=cols[cls], alpha=.10, lw=0, zorder=3)
    ax.scatter(x, y, s=s, c=cols[cls], alpha=.95, lw=0, zorder=4)
