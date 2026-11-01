"""Step 7. The paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex twice.
Output: release/paper/Hotham_The_Earth_at_Night.tex and .pdf
Run: python3 code/07_paper.py
"""
import importlib.util, re, shutil, subprocess
from common import *
spec = importlib.util.spec_from_file_location("site", os.path.join(ROOT, "code", "05_build_site.py")); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
S.check_facts()
R = S.R
OUT = os.path.join(ROOT, "release", "paper"); os.makedirs(OUT, exist_ok=True)
NAME = "Hotham_The_Earth_at_Night"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
st = jload(f"{WORK}/stats.json")
pc = lambda r: f"{'+' if r >= 1 else '-'}{abs(round((r - 1) * 100))}\\%"

TS = ("\\begin{table}[tbp]\\centering\\small\\caption{Sources and licences.}\\label{tab:sources}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.6cm}>{\\raggedright\\arraybackslash}p{7.6cm}>{\\raggedright\\arraybackslash}p{2.6cm}}\\toprule Source & Used & Licence\\\\\\midrule\n"
      "VNL V2 annual night lights (EOG, Colorado School of Mines), via \\citet{hengl} & Annual averages 2012 to 2024 at about 15 km (all years) and 7 km (2012, 2024); modelled years 2000 to 2011 & CC BY 4.0\\\\\n"
      "DMSP-style lights, after \\citet{li2020}, via \\citet{hengl} & Average over 1992 to 2024, 1 km & CC BY 4.0\\\\\n"
      f"Natural Earth & Countries, POP\\_EST, World Bank regions; {R['n']['cities']:,} populated places of at least 500,000 people & Public domain\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for k in ["na", "eca", "eap", "mena", "lac", "sa", "ssa"]:
    r = R["reg"][k]
    rows += f"{tex(r['name'])} & {r['l0']:.2f} & {r['l1']:.2f} & {pc(1 + r['pct'] / 100)} & {pc(1 + r['pct3'] / 100)} & {r['share0']:.1f} & {r['share1']:.1f} & {r['pop_share']:.1f} & {r['pp']:.0f}\\\\\n"
TR = ("\\begin{table}[tbp]\\centering\\small\\caption{Light by World Bank region: millions of light units, change between single years and between three-year averages, share of world light and of people (\\%), and light per person (world = 100).}\\label{tab:regions}\\setlength{\\tabcolsep}{4pt}"
      "\\begin{tabular}{lrrrrrrrr}\\toprule Region & 2012 & 2024 & Change & 3-year & Share 2012 & Share 2024 & People & Per person\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")


def ctab(lst, cap, lab):
    rows = ""
    for r in lst:
        d = r["dip"]
        rows += f"{tex(r['name'])} & {r['l0'] / 1000:,.1f} & {r['l1'] / 1000:,.1f} & {pc(r['ratio'])} & {pc(1 + r['pct3'] / 100)} & {d['fall']:.0f}\\% ({d['peak_year']} to {d['low_year']})\\\\\n" if d else ""
    return (f"\\begin{{table}}[tbp]\\centering\\small\\caption{{{cap}}}\\label{{{lab}}}"
            "\\begin{tabular}{lrrrrl}\\toprule Country & 2012 & 2024 & Change & 3-year & Deepest fall\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")


TU = ctab(R["up"][:15], "The fifteen countries whose light grew fastest, 2012 to 2024 (thousand light units; countries with at least a million people and 2,000 units in 2012).", "tab:up")
TD = ctab(R["down"], "Every ranked country whose light fell between 2012 and 2024.", "tab:down")
rows = ""
for a, b in zip(R["cup"][:12], R["cdown"][:12]):
    rows += f"{tex(a['name'])}, {tex(a['country'])} & {pc(a['ratio'])} & {tex(b['name'])}, {tex(b['country'])} & {pc(b['ratio'])}\\\\\n"
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{Cities of a million or more whose light within 20 km changed most, 2012 to 2024 (7 km grid; discs that averaged at least 2 nW in 2012).}\\label{tab:cities}"
      "\\begin{tabular}{lrlr}\\toprule Brightened & Change & Dimmed & Change\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")

t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
t = t.replace("\\url{{{meta.page}}}", "\\url{%s}" % PAGE_URL).replace("\\url{{{meta.repo}}}", "\\url{%s}" % REPO)
t = S.fill(t, esc=tex)
t = t.replace("{{TABLE_SOURCES}}", TS).replace("{{TABLE_REGIONS}}", TR).replace("{{TABLE_UP}}", TU).replace("{{TABLE_DOWN}}", TD).replace("{{TABLE_CITIES}}", TC)
assert not re.findall(r"\{\{(?!DOI\}\})", t), re.findall(r"\{\{[^}]*\}\}", t)
assert "--" not in t and "—" not in t and "–" not in t
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
# the PDF shows the placeholder as the text '10.5281/zenodo.23857868' until the publisher fills it
tc = t.replace("DOI: 10.5281/zenodo.23857868", "DOI: \\{\\{DOI\\}\\}")
open(os.path.join(OUT, "_build.tex"), "w", encoding="utf-8").write(tc)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "_build.tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, "_build.log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Error" in l][:12])
shutil.move(os.path.join(OUT, "_build.pdf"), os.path.join(OUT, NAME + ".pdf"))
for ext in (".aux", ".log", ".out", ".tex"):
    q = os.path.join(OUT, "_build" + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
