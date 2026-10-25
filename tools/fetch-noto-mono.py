import os
import urllib.request

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

FONT = r"font-lab\fonts\NotoSansMonoCJKsc-Regular.otf"
f = TTFont(FONT)
print("family:", f["name"].getDebugName(1), "| style:", f["name"].getDebugName(2))
upem = f["head"].unitsPerEm
cmap = f.getBestCmap()
hm = f["hmtx"]
print("upem", upem, "| M adv", hm[cmap[ord("M")]][0], "| 国 adv", hm[cmap[ord("国")]][0])

gs = f.getGlyphSet()
sample = "国黑会话硬件橙语圆永把模型与工具排成一条线进度结果"
ws, hs = [], []
for ch in sample:
    g = cmap.get(ord(ch))
    pen = BoundsPen(gs)
    gs[g].draw(pen)
    if pen.bounds:
        x0, y0, x1, y1 = pen.bounds
        ws.append((x1 - x0) / upem)
        hs.append((y1 - y0) / upem)
ws.sort()
hs.sort()
n = len(ws)
print(f"ink width p50={ws[n//2]:.3f} p95={ws[int(n*0.95)]:.3f} | height p50={hs[n//2]:.3f}")

URL = "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/Mono/NotoSansMonoCJKsc-Bold.otf"
DST = r"font-lab\fonts\NotoSansMonoCJKsc-Bold.otf"
if not os.path.exists(DST):
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        open(DST, "wb").write(data)
        print("bold downloaded", round(len(data) / 1048576, 2), "MB")
    except Exception as e:
        print("bold download failed:", e)
else:
    print("bold already present")

if os.path.exists(DST):
    fb = TTFont(DST)
    print("bold family:", fb["name"].getDebugName(1), "| style:", fb["name"].getDebugName(2))
