# The Earth at night

Satellite night lights every year from 2012 to 2024 (with a modelled look back to 2000) on one interactive map: where the world lit up, where it went dark, and why a darker picture from space does not always mean a darker street. Built from the Annual VIIRS Night Lights V2 as prepared by Tomislav Hengl (OpenGeoHub) and Natural Earth.

Interactive page: https://maps.tristanhotham.com/earth-at-night/
Paper: https://doi.org/10.5281/zenodo.23857868
Blog post: https://blog.tristanhotham.com/2026/10/31/earth-at-night/

## Headline results

- The world gave off 57% more light seen from space in 2024 than in 2012 (33.2 million to 52.3 million light units; 41% between three-year averages). Land averaging at least 1 nW/cm²/sr grew by 61%, to 15.1 million km².
- China (2.1 times) and India (2.7 times) gave 26% of the extra light. South Asia's share rose from 4.5% to 7.4%; North America's fell from 24.2% to 18.7%. Sub-Saharan Africa gives off 2.6% of the light for 14% of the people.
- Fastest brightening (countries of a million or more): Nepal 9.3 times, Cambodia 7.0, Ghana 6.4, Tanzania 6.0, Côte d'Ivoire 5.5. Cities: Kumasi 4.4 times, Addis Ababa 3.6, Accra 3.3. 47 of 141 countries at least doubled their light.
- Went dark: 17 of 141 countries lost light. War: Ukraine fell 73% from 2021 to 2022 (Kharkiv 98% from its peak); Aleppo 97% (2012 to 2015); Sanaa 95% (2013 to 2016); Khartoum 77% (2022 to 2024). Crises: Lebanon 71% (2019 to 2022), Venezuela 41% (2014 to 2020).
- Changing lamps: France (40% less light), the Netherlands (26%) and the United Kingdom (13%) dimmed as LEDs (which the sensor partly cannot see) replaced sodium lamps and lights were switched off after midnight, before the satellite's 1.30 am pass.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`); loads the images in `data/tiles/` and the files in `data/page/`. |
| `header.png` | Social card, 1200 x 630. |
| `data/countries.csv` | Every country: light 2000 to 2024 (2000 to 2011 marked modelled), change 2012 to 2024 and between three-year averages, share of world light, light per person, lit area, deepest fall. |
| `data/regions.csv` | The same for World Bank regions. |
| `data/cities.csv` | 1,007 Natural Earth places of at least 500,000 people: light within 20 km in 2012 and 2024 (7 km grid) and every year (15 km grid). |
| `data/world_series.csv` | World and land totals and lit land area, every year. |
| `data/results.json` | Every number used in the page, paper, blog, README, collage and Reddit post. |
| `data/tiles/` | Web Mercator images: night lights for each year, the 2012 to 2024 change, the DMSP-style long-term average (2.8 MB). |
| `data/page/` | Page data: country outlines, country and city summaries, and the yearly value of every ever-lit 15 km cell in 10 degree blocks (7.3 MB). |
| `code/` | Numbered scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper (PDF and LaTeX), blog post, figures and meta, Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots from the automated check of the page (desktop and phone). |

## Method in brief

- Night lights: Hengl's yearly layers of the VNL V2 annual averages, read at the overview levels in his Cloud-Optimised GeoTIFFs: 2,700 by 1,120 cells (about 15 km) for every year and 5,400 by 2,240 (about 7.4 km) for 2012 and 2024; extent 180 W to 180 E, 87.37 N to 62.0 S, checked against city positions.
- Scale fix: in this release the 2022 to 2024 layers are stored in whole nW, the earlier ones in tenths (median ratio of 2022 to 2021 on bright cells 0.100). Every year was converted to whole nW and rounded alike; negatives set to 0; no data north of 75.1 N.
- Light units: radiance (nW/cm²/sr) times area (km²). Countries: each cell to the Natural Earth country with most of its land. Cities: sum within 20 km. Per person: Natural Earth POP_EST (about 2019), world = 100.
- Rankings: countries with at least a million people and 2,000 light units in 2012; cities with at least a million people and an average of 2 nW in 2012. Robustness: three-year averages 2012 to 2014 against 2022 to 2024.
- Caveats: 2000 to 2011 are modelled, not observed; the 1.30 am overpass misses evening light and sees part-night switch-offs; the sensor misses blue light, so LEDs look dimmer; gas flares, greenhouses and industry count as light; no flare mask was available. The DMSP standard deviation file in the extract used was damaged and is not used.

## How to rerun

Needs Python 3 with numpy, scipy, shapely, rasterio, pyproj, matplotlib, fontTools and Pillow; xelatex, pdftotext and pdfinfo; Playwright with Chromium for the QA step. Raw inputs are read in place from `/home/claude/newdata/raw8/nightlights` (rasters as gzipped raw arrays extracted from the overview levels of Hengl's COGs, and the Zenodo metadata) and Natural Earth from `/home/claude/newdata/raw/geo` (set in `code/common.py`). Intermediates go to `/home/claude/work/earth-at-night` (set `NIGHT_WORK`).

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

Hotham, T. (2026) The Earth at night: where the world lit up and where it went dark, from satellite night lights 2012 to 2024. Zenodo. https://doi.org/10.5281/zenodo.23857868

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
