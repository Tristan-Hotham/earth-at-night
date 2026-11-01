"""Shared paths and helpers for the earth-at-night study ("The Earth at night").

Raw inputs (read in place, never copied into the repo):
  RAST   Overview levels of Tomislav Hengl's Cloud-Optimised GeoTIFFs of annual night lights (Zenodo record 7750174,
         version DOI 10.5281/zenodo.17294744, CC BY 4.0), extracted as gzipped raw arrays. File names give width,
         height and type (Int16Array = int16, Uint16Array = uint16, Float32Array = float32), little-endian,
         row-major, north-up. Metadata: META.
           average_viirs ... 2700x1120 (ov5, about 15 km): one file per year 2000 to 2024
           average_viirs ... 5400x2240 (ov4, about 7 km): 2012 and 2024 (and 2000 at 5400x2241, not used)
           average_dmsp  ... 43201x16801 (1 km): DMSP-style lights, one average over 1992 to 2024
           difference_viirs, pc1..pc4 (not used: see the paper)
         Extent of the VIIRS layers: lon -180 to 180, lat 87.37 to -62.0008 (checked in 01_grids.py against city
         points); DMSP: lon -180 to 180, lat 75 to -65 (checked against VIIRS). Nodata -32768.
  GEO    Natural Earth 10m admin 0 countries (with POP_EST) and populated places (public domain).
Intermediates are written to WORK (outside the repo)."""
import json, os, re, math, glob, gzip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("NIGHT_RAW", "/home/claude/newdata/raw8/nightlights")
RAST = os.path.join(RAW, "rasters")
META = os.path.join(RAW, "zenodo_7750174_metadata.json")
GEO = os.environ.get("NIGHT_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("FONT_DIR", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
PAGE = os.path.join(DATA, "page")
WORK = os.environ.get("NIGHT_WORK", "/home/claude/work/earth-at-night")
for d in (DATA, PAGE, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "earth-at-night"
PAGE_URL = "https://maps.tristanhotham.com/earth-at-night/"
REPO = "https://github.com/Tristan-Hotham/earth-at-night"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

YEARS = list(range(2000, 2025))
OBS = list(range(2012, 2025))          # observed by VIIRS
MODEL = list(range(2000, 2012))        # extrapolated backwards by logistic regression (Hengl), not observed
Y0, Y1 = 2012, 2024
TOP, BOT = 87.37, -62.0008             # VIIRS extent
DTOP, DBOT = 75.0, -65.0               # DMSP extent
R_EARTH = 6371.0088
MERC = 85.0511


def raw_file(kind, year=None, w=2700):
    pat = f"nightlights.{kind}.*"
    if year is not None:
        pat += f"_{year}0101_*"
    pat += f"_{w}x*"
    fs = sorted(glob.glob(os.path.join(RAST, pat)))
    assert len(fs) == 1, (pat, fs)
    return fs[0]


def read_raw(path):
    import numpy as np
    m = re.search(r"_(\d+)x(\d+)_(\w+?)Array", path)
    w, h, t = int(m[1]), int(m[2]), m[3]
    dt = {"Int16": "<i2", "Uint16": "<u2", "Float32": "<f4"}[t]
    a = np.frombuffer(gzip.open(path).read(), dt)
    assert a.size == w * h, path
    return a.reshape(h, w)


def year_nw(year, w=2700):
    """Annual VIIRS night light for one year, harmonised to whole nW/cm2/sr (float32, NaN = nodata).

    In this release the 2012 to 2021 layers (and the modelled 2000 to 2011 ones) are stored on the 0 to 2000 scale
    (tenths of a nW), but the 2022 to 2024 layers are on the original 0 to 200 scale (whole nW): on bright cells the
    ratio of 2022 to 2021 has a median of 0.100 (01_grids.py checks this). To compare like with like, every year is put
    into whole nW and rounded to a whole nW, as the 2022 to 2024 overviews already are; negative values (noise) are 0."""
    import numpy as np
    a = read_raw(raw_file("average_viirs", year, w)).astype(np.float32)
    nd = a == -32768
    if year <= 2021:
        a = np.round(a / 10.0)
    a = np.maximum(a, 0)
    a[nd] = np.nan
    return a


def cell_area(h, top=TOP, bot=BOT, w=2700):
    """km2 of one cell in each row of a regular lon/lat grid (exact on a sphere)."""
    import numpy as np
    e = top - (top - bot) * np.arange(h + 1) / h
    return R_EARTH ** 2 * math.radians(360 / w) * (np.sin(np.radians(e[:-1])) - np.sin(np.radians(e[1:])))


def row_lat(h, top=TOP, bot=BOT):
    import numpy as np
    return top - (top - bot) * (np.arange(h) + .5) / h


def col_lon(w):
    import numpy as np
    return -180 + 360 * (np.arange(w) + .5) / w


def rc(lon, lat, w=2700, h=1120, top=TOP, bot=BOT):
    import numpy as np
    r = ((top - np.asarray(lat, float)) / (top - bot) * h).astype(int)
    c = ((np.asarray(lon, float) + 180) / 360 * w).astype(int) % w
    return r, c


def dash(v):
    """House style: no em or en dashes, no double hyphens, in anything written to data/."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, (list, tuple)):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def _np(o):
    import numpy as np
    if isinstance(o, np.integer): return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.bool_): return bool(o)
    if isinstance(o, np.ndarray): return o.tolist()
    raise TypeError(type(o))


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"), default=_np)


def jload(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
