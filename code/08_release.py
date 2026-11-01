"""Step 8. Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
Run after 07_paper.py and 09_readme.py (the zip includes README.md and LICENSE): python3 code/08_release.py
"""
import importlib.util, re, json, zipfile, shutil
from common import *
spec = importlib.util.spec_from_file_location("site", os.path.join(ROOT, "code", "05_build_site.py")); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
S.check_facts()
R = S.R
REL = os.path.join(ROOT, "release"); NAME = "Hotham_The_Earth_at_Night"

# numbers written out in alt text
r1 = lambda v: f"{v:.1f}"
assert [r1(x["ratio"]) for x in R["up"][:5]] == ["9.3", "7.0", "6.4", "6.0", "5.5"]
assert [round(x["pct"]) for x in R["down"][:2]] == [-53, -53] and round([x for x in R["down"] if x["a3"] == "BEL"][0]["pct"]) == -10
assert [r1(R["world"]["series"][i]) for i in (0, 11, 12, 24)] == ["21.6", "24.9", "33.2", "52.3"]
assert [x["name"] for x in R["pp"]["top"][:4]] == ["Qatar", "Libya", "Saudi Arabia", "Finland"] and [round(x["pp"]) for x in R["pp"]["top"][:4]] == [1302, 963, 837, 736]
assert [x["name"] for x in R["pp"]["bottom"][:4]] == ["Ethiopia", "Malawi", "Uganda", "Niger"] and [r1(x["pp"]) for x in R["pp"]["bottom"][:4]] == ["3.0", "4.3", "5.0", "5.1"]
assert R["city"]["Kharkiv"]["dip"]["low_year"] in (2022, 2023) and R["city"]["Mosul"]["dip"]["low_year"] == 2015

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = S.fill(post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, used
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for ln in post.splitlines():
    if "{{IMG" in ln: assert ln.startswith("{{IMG") and ln.endswith("}}"), ln
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
assert not set(re.findall(r"\{\{(\w+)\}\}", post)) - {"DOI_URL"}
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
w = R["world"]
meta = {"title": "The Earth at night: where the world lit up and where it went dark",
        "slug": "earth-at-night",
        "excerpt": f"Seen from space, the planet gave off {w['pct']:.0f}% more light in 2024 than in 2012. Nepal's light grew {R['c']['NPL']['ratio']:.1f} times and Africa's cities blazed up, while war halved the light of Ukraine and Yemen, and new LED street lamps made France look {abs(R['c']['FRA']['pct']):.0f}% darker than it is.",
        "seo_description": "Satellite night lights 2012 to 2024 mapped: where the world lit up, where it went dark through war and power cuts, and why LEDs fool the satellite.",
        "tags": ["night lights", "VIIRS", "light pollution", "electrification", "Ukraine", "Africa", "maps", "data visualisation"],
        "header_alt": f"Title card reading 'The Earth at night' in black and gold on cream, beside a dark world map dotted with every lit place coloured by change from 2012 to 2024, gold where light grew and magenta where it fell. Text: the planet gave off {w['pct']:.0f}% more light; Nepal's grew {R['c']['NPL']['ratio']:.1f} times, while Ukraine and Yemen lost half of theirs."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# ---- Zenodo ----
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for f in os.listdir(Z):
    os.remove(os.path.join(Z, f))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/earth-at-night_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for base, dirs, files in os.walk(os.path.join(ROOT, d)):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for fn in sorted(files):
                if fn.endswith(".pyc"): continue
                p = os.path.join(base, fn); z.write(p, "earth-at-night/" + os.path.relpath(p, ROOT))
    for fn in ("README.md", "LICENSE", "index.html", "header.png"):
        z.write(os.path.join(ROOT, fn), f"earth-at-night/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\emph{", "").replace("}", "").replace("\\&", "&")
zmeta = {"title": "The Earth at Night: Where the World Lit Up and Where It Went Dark, from Satellite Night Lights 2012 to 2024",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE_URL}\">{PAGE_URL}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/earth-at-night/}}.</p>"
                        "<p>Text, figures and derived data: CC BY 4.0; code: MIT. Night lights: Annual VIIRS Night Lights V2 (Earth Observation Group, Colorado School of Mines; Elvidge et al. 2021) as prepared by Hengl (Zenodo 10.5281/zenodo.7750174, CC BY 4.0); countries, populations and places: Natural Earth (public domain).</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["night lights", "VIIRS", "Day/Night Band", "artificial light at night", "light pollution", "electrification", "conflict", "LED street lighting", "remote sensing", "data visualisation"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [
             {"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
             {"identifier": PAGE_URL, "relation": "isSupplementedBy", "resource_type": "other"},
             {"identifier": "10.5281/zenodo.17294744", "relation": "isDerivedFrom", "scheme": "doi", "resource_type": "dataset"},
             {"identifier": "10.3390/rs13050922", "relation": "cites", "scheme": "doi", "resource_type": "publication-article"},
             {"identifier": "10.1038/s41597-020-0510-y", "relation": "cites", "scheme": "doi", "resource_type": "publication-article"},
             {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}]}
s = json.dumps(zmeta, ensure_ascii=False) + json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
with open(f"{Z}/metadata.json", "w", encoding="utf-8") as f:
    json.dump(zmeta, f, ensure_ascii=False, indent=2)
print("blog words", words, "images", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
