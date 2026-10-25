"""Ink/advance ratio of Chinese glyphs, so "looks bigger" can be checked."""
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

FACES = [
    ("Maple Mono CN", "font-lab/fonts/MapleMonoCN-Regular.ttf"),
    ("Maple Tight", "font-lab/fonts/MapleMonoCNTight-Regular.ttf"),
    ("HarmonyOS SC", "font-lab/fonts/HarmonyOSSC-Regular.ttf"),
    ("MiSans", "font-lab/fonts/MiSans-Regular.otf"),
]

SAMPLE = "国黑会话硬件橙语圆永把模型与工具排成一条线进度结果"

for name, path in FACES:
    f = TTFont(path, fontNumber=0)
    upem = f["head"].unitsPerEm
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    widths, heights = [], []
    for ch in SAMPLE:
        g = cmap.get(ord(ch))
        if not g:
            continue
        pen = BoundsPen(gs)
        gs[g].draw(pen)
        if not pen.bounds:
            continue
        x0, y0, x1, y1 = pen.bounds
        widths.append((x1 - x0) / upem)
        heights.append((y1 - y0) / upem)
    widths.sort()
    heights.sort()
    n = len(widths)
    print(f"{name:14} ink width p50={widths[n//2]:.3f} p95={widths[int(n*0.95)]:.3f} | height p50={heights[n//2]:.3f}")
