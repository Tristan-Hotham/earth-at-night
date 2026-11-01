"""Step 9. README.md and LICENSE, numbers from data/results.json.
Run: python3 code/09_readme.py
"""
import importlib.util
from common import *
spec = importlib.util.spec_from_file_location("site", os.path.join(ROOT, "code", "05_build_site.py")); S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
S.check_facts()
R = S.R; w, c, ci, rg, n = R["world"], R["c"], R["city"], R["reg"], R["n"]
mb = lambda p: f"{sum(os.path.getsize(os.path.join(b, f)) for b, _, fs in os.walk(p) for f in fs) / 1e6:.1f} MB" if os.path.isdir(p) else f"{os.path.getsize(p) / 1e6:.1f} MB"
readme = f"""# The Earth at night

Satellite night lights every year from 2012 to 2024 (with a modelled look back to 2000) on one interactive map: where the world lit up, where it went dark, and why a darker picture from space does not always mean a darker street. Built from the Annual VIIRS Night Lights V2 as prepared by Tomislav Hengl (OpenGeoHub) and Natural Earth.

Interactive page: {PAGE_URL}
Paper: {{https://doi.org/10.5281/zenodo.23857868}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/earth-at-night/}}

## Headline results

- The world gave off {w['pct']:.0f}% more light seen from space in 2024 than in 2012 ({w['l0']:.1f} million to {w['l1']:.1f} million light units; {w['pct3']:.0f}% between three-year averages). Land averaging at least 1 nW/cm²/sr grew by {w['lit_pct']:.0f}%, to {w['lit1']:.1f} million km².
- China ({c['CHN']['ratio']:.1f} times) and India ({c['IND']['ratio']:.1f} times) gave {R['gain']['chn_ind']:.0f}% of the extra light. South Asia's share rose from {rg['sa']['share0']:.1f}% to {rg['sa']['share1']:.1f}%; North America's fell from {rg['na']['share0']:.1f}% to {rg['na']['share1']:.1f}%. Sub-Saharan Africa gives off {rg['ssa']['share1']:.1f}% of the light for {rg['ssa']['pop_share']:.0f}% of the people.
- Fastest brightening (countries of a million or more): Nepal {c['NPL']['ratio']:.1f} times, Cambodia {c['KHM']['ratio']:.1f}, Ghana {c['GHA']['ratio']:.1f}, Tanzania {c['TZA']['ratio']:.1f}, Côte d'Ivoire {c['CIV']['ratio']:.1f}. Cities: Kumasi {ci['Kumasi']['ratio']:.1f} times, Addis Ababa {ci['Addis Ababa']['ratio']:.1f}, Accra {ci['Accra']['ratio']:.1f}. {n['doubled']} of {n['eligible']} countries at least doubled their light.
- Went dark: {n['fell']} of {n['eligible']} countries lost light. War: Ukraine fell {c['UKR']['dip']['fall']:.0f}% from 2021 to 2022 (Kharkiv {ci['Kharkiv']['dip']['fall']:.0f}% from its peak); Aleppo {ci['Aleppo']['dip']['fall']:.0f}% (2012 to 2015); Sanaa {ci['Sanaa']['dip']['fall']:.0f}% (2013 to 2016); Khartoum {ci['Khartoum']['dip']['fall']:.0f}% (2022 to 2024). Crises: Lebanon {c['LBN']['dip']['fall']:.0f}% (2019 to 2022), Venezuela {c['VEN']['dip']['fall']:.0f}% (2014 to 2020).
- Changing lamps: France ({abs(c['FRA']['pct']):.0f}% less light), the Netherlands ({abs(c['NLD']['pct']):.0f}%) and the United Kingdom ({abs(c['GBR']['pct']):.0f}%) dimmed as LEDs (which the sensor partly cannot see) replaced sodium lamps and lights were switched off after midnight, before the satellite's 1.30 am pass.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`); loads the images in `data/tiles/` and the files in `data/page/`. |
| `header.png` | Social card, 1200 x 630. |
| `data/countries.csv` | Every country: light 2000 to 2024 (2000 to 2011 marked modelled), change 2012 to 2024 and between three-year averages, share of world light, light per person, lit area, deepest fall. |
| `data/regions.csv` | The same for World Bank regions. |
| `data/cities.csv` | {n['cities']:,} Natural Earth places of at least 500,000 people: light within 20 km in 2012 and 2024 (7 km grid) and every year (15 km grid). |
| `data/world_series.csv` | World and land totals and lit land area, every year. |
| `data/results.json` | Every number used in the page, paper, blog, README, collage and Reddit post. |
| `data/tiles/` | Web Mercator images: night lights for each year, the 2012 to 2024 change, the DMSP-style long-term average ({mb(os.path.join(DATA, 'tiles'))}). |
| `data/page/` | Page data: country outlines, country and city summaries, and the yearly value of every ever-lit 15 km cell in 10 degree blocks ({mb(PAGE)}). |
| `code/` | Numbered scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper (PDF and LaTeX), blog post, figures and meta, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots from the automated check of the page (desktop and phone). |

## Method in brief

- Night lights: Hengl's yearly layers of the VNL V2 annual averages, read at the overview levels in his Cloud-Optimised GeoTIFFs: 2,700 by 1,120 cells (about {R['grid']['km15']:.0f} km) for every year and 5,400 by 2,240 (about {R['grid']['km7']:.1f} km) for 2012 and 2024; extent 180 W to 180 E, 87.37 N to 62.0 S, checked against city positions.
- Scale fix: in this release the 2022 to 2024 layers are stored in whole nW, the earlier ones in tenths (median ratio of 2022 to 2021 on bright cells {R['grid']['scale_ratio']:.3f}). Every year was converted to whole nW and rounded alike; negatives set to 0; no data north of {R['grid']['north']:.1f} N.
- Light units: radiance (nW/cm²/sr) times area (km²). Countries: each cell to the Natural Earth country with most of its land. Cities: sum within 20 km. Per person: Natural Earth POP_EST (about 2019), world = 100.
- Rankings: countries with at least a million people and 2,000 light units in 2012; cities with at least a million people and an average of 2 nW in 2012. Robustness: three-year averages 2012 to 2014 against 2022 to 2024.
- Caveats: 2000 to 2011 are modelled, not observed; the 1.30 am overpass misses evening light and sees part-night switch-offs; the sensor misses blue light, so LEDs look dimmer; gas flares, greenhouses and industry count as light; no flare mask was available. The DMSP standard deviation file in the extract used was damaged and is not used.

## How to rerun

Needs Python 3 with numpy, scipy, shapely, rasterio, pyproj, matplotlib, fontTools and Pillow; xelatex, pdftotext and pdfinfo; Playwright with Chromium for the QA step. Raw inputs are read in place from `{RAW}` (rasters as gzipped raw arrays extracted from the overview levels of Hengl's COGs, and the Zenodo metadata) and Natural Earth from `{GEO}` (set in `code/common.py`). Intermediates go to `{WORK}` (set `NIGHT_WORK`).

```
python3 code/01_grids.py        # harmonised yearly grids, country grid, DMSP average
python3 code/02_stats.py        # world, region, country and city totals
python3 code/03_page_data.py    # map images and page data
python3 code/04_results.py      # data/results.json
python3 code/05_build_site.py   # index.html (and the fact checks)
python3 code/06_figures.py      # blog and paper figures, header.png
python3 code/07_paper.py        # paper PDF
python3 code/09_readme.py       # README and LICENSE
python3 code/08_release.py      # blog post and meta, Zenodo files
python3 reddit/collage.py       # collage
python3 code/10_qa.py           # browser check and screenshots
```

## Sources and licences

- Annual VIIRS Night Lights (VNL) V2, Earth Observation Group, Payne Institute for Public Policy, Colorado School of Mines (Elvidge, C.D., Zhizhin, M., Ghosh, T., Hsu, F.C. and Taneja, J. (2021) Remote Sensing 13(5), 922, doi:10.3390/rs13050922).
- Hengl, T. (2025) Annual time series of global VIIRS nighttime lights for 2000 to 2024 at 500 m spatial resolution extrapolated using logistic regression, v0.4. Zenodo, doi:10.5281/zenodo.17294744 (record 7750174). CC BY 4.0. The DMSP-style layer follows Li, X., Zhou, Y., Zhao, M. and Zhao, X. (2020) Scientific Data 7, 168.
- Natural Earth admin 0 countries and populated places (public domain).
- Base maps and hill shading on the page: © Esri. Map library: Leaflet.

## Citation

Hotham, T. (2026) The Earth at night: where the world lit up and where it went dark, from satellite night lights 2012 to 2024. Zenodo. {{https://doi.org/10.5281/zenodo.23857868}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "DSIT", "DCMS"):
    assert bad not in readme, bad
assert "--" not in readme.replace("|---|---|", "")
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, the figures, the paper and the derived data in data/ are
released under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). They are
derived from the Annual VIIRS Night Lights V2 (Earth Observation Group, Colorado
School of Mines) as published by T. Hengl on Zenodo under CC BY 4.0; please credit
those sources as well. Country outlines, populations and places are Natural Earth
(public domain).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(readme.split()), "words")
