## Title

[OC] The Earth at night, 2012 to 2024: the planet gave off 57% more light, Nepal's light grew 9.3 times, while Ukraine's and Yemen's halved

## Body

I added up every year of satellite night lights (VIIRS annual composites, 2012 to 2024) by country and around 1,007 cities. The world's measured light rose 57% (41% comparing three-year averages), and China and India gave 26% of the increase. The fastest risers started from almost nothing: Nepal 9.3x, Cambodia 7.0x, Ghana 6.4x, Tanzania 6.0x. The steepest falls are wars and crises: Kharkiv lost 98% of its light from its peak, Aleppo 97%, Khartoum 77% since 2022, Lebanon 71% between 2019 and 2022.

The surprise: France (-40%), the Netherlands (-26%) and the UK (-13%) also "dimmed". That is mostly not real darkness. The sensor cannot see blue light, so white LED street lamps look dimmer than the orange sodium lamps they replace, and the satellite passes at about 1.30 am, after many towns switch their lights off. Gas flares at oil fields count as light too (much of Iraq's rise, and about half of Venezuela's light).

Interactive map, where you can slide through the years or swipe between any two: https://maps.tristanhotham.com/earth-at-night/

## Source comment

Source: Annual VIIRS Night Lights V2 (Earth Observation Group, Colorado School of Mines; Elvidge et al. 2021, Remote Sensing 13, 922), as consistent yearly 500 m layers by Tomislav Hengl, OpenGeoHub (Zenodo 10.5281/zenodo.7750174, CC BY 4.0), used at about 15 km (7 km for 2012 and 2024). The 2022 to 2024 layers in that release are stored on a scale ten times smaller than earlier years, so all years were put on the same scale. Light = radiance x area, summed by Natural Earth country; cities = light within 20 km; populations from Natural Earth. Years before 2012 in that dataset are modelled, not observed, and are not used for any number here.

Tools: Python (numpy, rasterio, shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/earth-at-night/
Paper: https://doi.org/10.5281/zenodo.23857868
Blog post: https://blog.tristanhotham.com/2026/10/31/earth-at-night/
