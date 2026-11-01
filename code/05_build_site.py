"""Step 5. Build index.html from code/page_template.html, code/page_style.css and code/fullscreen_snippet.html. Every number
in the text is a {{path|format}} token filled from data/results.json; facts stated in words are checked by the asserts
in check_facts() (they cover the page, paper, blog, README and collage, which import this file). 10.5281/zenodo.23857868, https://doi.org/10.5281/zenodo.23857868
and https://blog.tristanhotham.com/2026/10/31/earth-at-night/ are left for the publisher.
Run: python3 code/05_build_site.py
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from common import WORK, jload, YEARS, OBS
R = json.load(open(os.path.join(ROOT, "data", "results.json"), encoding="utf-8"))
PLACEHOLDERS = {"DOI", "DOI_URL", "BLOG_URL"}
TOK = re.compile(r"\{\{([^}|]+)(\|(\w+))?\}\}")


def get(path, R=R):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(v):,}"
    if f == "abs": return f"{abs(round(v)):,}"
    if f == "p0": return f"{round(v):,}%"
    if f == "p1": return f"{v:.1f}%"
    if f == "x1": return f"{v:.1f}"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    if f == "f3": return f"{v:.3f}"
    raise ValueError(f)


def fill(tpl, esc=lambda s: s):
    def sub(m):
        if m.group(1).strip() in PLACEHOLDERS or m.group(1).startswith(("IMG", "TABLE_")):
            return m.group(0)
        return esc(fmt(get(m.group(1).strip()), m.group(3)))
    return TOK.sub(sub, tpl)


def check_facts():
    """Facts stated in words anywhere in the study."""
    w, c, ci, n = R["world"], R["c"], R["city"], R["n"]
    assert w["fell_years"] == [2014, 2015, 2020], w["fell_years"]
    assert w["lit_pct"] > w["pct"] > w["pct3"] > 35                       # 'the lit area grew even faster than the light'
    assert max(R["reg"].values(), key=lambda r: r["pct"])["name"] == "South Asia"
    assert R["reg"]["ssa"]["share1"] - R["reg"]["ssa"]["share0"] < .5     # 'its share barely moved'
    assert R["reg"]["na"]["share1"] < R["reg"]["na"]["share0"] and R["reg"]["eca"]["share1"] < R["reg"]["eca"]["share0"]
    assert R["reg"]["eap"]["share1"] > R["reg"]["eap"]["share0"] and R["reg"]["sa"]["share1"] > R["reg"]["sa"]["share0"]
    assert 2 < c["CHN"]["ratio"] < 2.5 and c["IND"]["ratio"] > c["CHN"]["ratio"]
    assert c["USA"]["share1"] == max(x["share1"] for x in c.values())    # 'still the brightest country'
    assert [x["a3"] for x in R["up"][:8]] == ["NPL", "KHM", "GHA", "TZA", "CIV", "SEN", "KEN", "ETH"], [x["a3"] for x in R["up"][:8]]
    assert R["cup"][0]["name"] == "Kumasi" and "Addis Ababa" in [x["name"] for x in R["cup"][:5]]
    assert ci["Mosul"]["dip"]["peak_year"] == 2013 and ci["Mosul"]["dip"]["low_year"] == 2015 and ci["Mosul"]["ratio"] > 3
    assert ci["Baghdad"]["ratio"] > 3 and ci["Basra"]["ratio"] > 3
    assert n["fell"] == len(R["down"]) and n["fell10"] == sum(round(x["pct"]) <= -10 for x in R["down"])
    for a3, py, ly in (("UKR", 2021, 2022), ("SYR", 2012, 2015), ("YEM", 2012, 2016), ("LBN", 2019, 2022), ("VEN", 2014, 2020), ("AFG", 2013, 2022)):
        d = c[a3]["dip"]; assert (d["peak_year"], d["low_year"]) == (py, ly), (a3, d)
    for name, py, ly in (("Khartoum", 2022, 2024), ("Beirut", 2018, 2022), ("Aleppo", 2012, 2015), ("Sanaa", 2013, 2016)):
        d = ci[name]["dip"]; assert (d["peak_year"], d["low_year"]) == (py, ly), (name, d)
    for name in ("Kharkiv", "Zaporizhzhia", "Odesa"):
        assert ci[name]["dip"]["peak_year"] >= 2018 and ci[name]["dip"]["low_year"] >= 2022, name
    assert ci["Maracaibo"]["dip"]["low_year"] == 2019 and ci["Caracas"]["dip"]["low_year"] == 2019
    assert [x["a3"] for x in R["down"][:2]] == ["UKR", "YEM"]
    assert {"FRA", "NLD", "CHE", "GBR", "GAB"} <= {x["a3"] for x in R["down"]}
    assert -30 < ci["Paris"]["pct"] < -20 and -30 < ci["London"]["pct"] < -20     # 'each lost about a quarter'
    assert ci["The Hague"]["pct"] < -50 and ci["Rotterdam"]["pct"] < -40
    assert R["pp"]["top"][0]["a3"] == "QAT" and R["pp"]["bottom"][0]["a3"] == "ETH"
    assert {"UGA", "COD", "BGD"} <= {x["a3"] for x in R["pp"]["bottom"]}
    assert c["QAT"]["pp"] > c["LBY"]["pp"] > c["SAU"]["pp"] > 100 and c["CHN"]["pp"] < 100 and c["IND"]["pp"] < 100
    dis = [x for x in R["dis"]]
    assert len(dis) == n["disagree"] and all(min(abs(x["pct"]), abs(x["pct3"])) < 10 for x in dis), dis   # 'all within a tenth of no change on one measure'
    assert 45 < R["ven"]["monagas_share1"] < 60                            # 'about half'
    assert R["ven"]["monagas_share1"] > R["ven"]["monagas_share0"]
    assert R["gain"]["top"][0]["name"] == "China" and R["gain"]["top"][1]["name"] == "India"
    assert R["world"]["jump"] > 20                                         # 'they do not meet the observations'
    assert R["c"]["AFG"]["dip"]["low_year"] == 2022
    assert R["grid"]["dmsp_corr"] > .6
    assert R["reg"]["ssa"]["pop_share"] > 5 * R["reg"]["ssa"]["share1"]
    return True


def check_text(html):
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv", "Civil Serv"):
        assert bad not in vis, bad
    return vis


if __name__ == "__main__":
    check_facts()
    tpl = open(os.path.join(HERE, "page_template.html"), encoding="utf-8").read()
    tpl = tpl.replace("/*CSS*/", open(os.path.join(HERE, "page_style.css"), encoding="utf-8").read())
    tpl = tpl.replace("/*FULLSCREEN*/", open(os.path.join(HERE, "fullscreen_snippet.html"), encoding="utf-8").read().strip())
    html = fill(tpl)
    pm = jload(f"{WORK}/page_meta.json"); pal = jload(f"{WORK}/palette.json"); dpal = jload(f"{WORK}/dmsp_palette.json")
    keep = {k: R[k] for k in ("world", "reg", "up", "down", "pp", "city", "grid")}
    PD = dict(R=keep, C=json.load(open(os.path.join(ROOT, "data", "page", "countries.json"), encoding="utf-8")), years=YEARS,
              pal=pal["stops"], dpal=dpal["stops"], change=pm["change"]["classes"], chmin=pm["change"]["min_nw"],
              north=pm["merc"]["north"], south=pm["merc"]["south"], dnorth=pm["merc"]["dmsp_north"])
    html = html.replace("/*PD*/", json.dumps(PD, ensure_ascii=False, separators=(",", ":")))
    left = set(re.findall(r"\{\{(\w+)\}\}", html))
    assert left <= PLACEHOLDERS and "{{" not in re.sub(r"\{\{(DOI|DOI_URL|BLOG_URL)\}\}", "", html), left
    check_text(html)
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()), "bytes")
