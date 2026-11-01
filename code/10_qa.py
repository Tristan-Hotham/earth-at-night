"""Step 10. QA: open index.html in Chromium (desktop 1280 px and phone 390 px), collect console errors, exercise the map
modes, the swipe, a click popup and the search, and save screenshots to qa/. External tiles and fonts are blocked in the
build container, so failed requests to other hosts are expected and ignored.
Run: python3 code/10_qa.py
"""
import os, re, json, threading, http.server, functools
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
QA = os.path.join(ROOT, "qa"); os.makedirs(QA, exist_ok=True)
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("QA_PORT", "8771"))), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:%d/index.html" % int(os.environ.get("QA_PORT", "8771"))
LEAF = os.environ.get("LEAFLET_DIST", "/dev/shm/piracy/npm/node_modules/leaflet/dist")   # npm leaflet 1.9.x, served in place of the CDN


def route(r):
    u = r.request.url
    if "cdnjs.cloudflare.com" in u and "leaflet" in u:      # the CDN is not reachable from the container: serve a local copy
        f = "leaflet.css" if u.endswith(".css") else "leaflet.js"
        return r.fulfill(path=os.path.join(LEAF, f), content_type="text/css" if f.endswith("css") else "application/javascript")
    if u.startswith("http://127.0.0.1"):
        return r.continue_()
    return r.abort()
errors = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vp in (("desktop", dict(width=1280, height=900)), ("phone", dict(width=390, height=844))):
        ctx = b.new_context(viewport=vp, device_scale_factor=1)
        pg = ctx.new_page()
        pg.on("console", lambda m, n=name: m.type == "error" and not re.search(r"Failed to load resource|ERR_|net::", m.text) and errors.append((n, m.text)))
        pg.on("pageerror", lambda e, n=name: errors.append((n, str(e))))
        pg.route("**/*", route)
        pg.goto(URL, wait_until="load"); pg.wait_for_timeout(1500)
        sw = pg.evaluate("document.documentElement.scrollWidth")
        assert sw <= vp["width"] + 1, (name, "horizontal scroll", sw)
        pg.screenshot(path=f"{QA}/{name}_top.png")
        pg.locator("#atlas").scroll_into_view_if_needed(); pg.wait_for_timeout(800)
        pg.locator("#atlas").screenshot(path=f"{QA}/{name}_map_2024.png")
        pg.click("#modeBtns .btn[data-m=change]"); pg.wait_for_timeout(1200)
        pg.locator("#atlas").screenshot(path=f"{QA}/{name}_map_change.png")
        pg.click("#modeBtns .btn[data-m=swipe]"); pg.wait_for_timeout(1200)
        pg.locator("#atlas").screenshot(path=f"{QA}/{name}_map_swipe.png")
        pg.click("#modeBtns .btn[data-m=year]"); pg.wait_for_timeout(300)
        pg.fill("#q", "Khartoum"); pg.wait_for_timeout(700)
        pg.locator("#sug li").first.click(); pg.wait_for_timeout(1800)
        pg.locator("#atlas").screenshot(path=f"{QA}/{name}_search.png")
        box = pg.locator("#lmap").bounding_box()
        pg.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); pg.wait_for_timeout(1500)
        pg.locator("#atlas").screenshot(path=f"{QA}/{name}_click.png")
        pg.click(".lyrBtn"); pg.wait_for_timeout(300)
        pg.locator("#lmap").screenshot(path=f"{QA}/{name}_layers.png")
        pg.click(".lyrBtn")
        pg.click(".mfs-btn"); pg.wait_for_timeout(800)
        pg.screenshot(path=f"{QA}/{name}_fullscreen.png"); pg.click(".mfs-btn"); pg.wait_for_timeout(500)
        pg.evaluate("document.fullscreenElement && document.exitFullscreen()"); pg.wait_for_timeout(300)
        for i, sel in enumerate(["#worldChart", "#regionChart", "#divChart", "#cityMini", "#ppChart"]):
            pg.locator(sel).scroll_into_view_if_needed(); pg.wait_for_timeout(200)
            pg.locator(sel).screenshot(path=f"{QA}/{name}_chart{i}_{sel[1:]}.png")
        pg.screenshot(path=f"{QA}/{name}_full.png", full_page=True)
        if name == "desktop":
            pg.evaluate("document.documentElement.dataset.theme='dark'"); pg.wait_for_timeout(200)
            pg.locator("#divChart").scroll_into_view_if_needed(); pg.screenshot(path=f"{QA}/desktop_dark.png")
        ctx.close()
    b.close()
srv.shutdown()
print("console errors:", errors)
assert not errors
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
vis = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S))
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
print("QA ok; screenshots in", QA)
