"""Build a tighter-CJK variant of Maple Mono CN.

Maple's Hanzi sit on a 1.2em advance (2:1 against its 0.6em Latin) — right for code,
loose for prose. This rewrites the full-width advance to TARGET and re-centres the
ink, leaving the outlines untouched (unless a glyph is wider than TARGET, in which
case only that glyph is condensed horizontally), then renames the family so it can
be installed alongside the original.

    python tools/tight-maple.py                    # report only
    python tools/tight-maple.py --write            # 1.00em
    python tools/tight-maple.py --write --target 960
"""
import os
import sys
from collections import Counter

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "font-lab", "fonts", "MapleMonoCN-Regular.ttf")
DST = os.path.join(ROOT, "font-lab", "fonts", "MapleMonoCNTight-Regular.ttf")
FAMILY = "Maple Mono CN Tight"
TARGET = 1000  # units per em is 1000; 1em advance
SCALE = 1.0    # glyph outline scale, around the ink centre and the baseline


def arg_src():
    if "--src" in sys.argv:
        i = sys.argv.index("--src")
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return SRC


def arg_target():
    if "--target" in sys.argv:
        i = sys.argv.index("--target")
        if i + 1 < len(sys.argv):
            return int(sys.argv[i + 1])
    return TARGET


def arg_scale():
    if "--scale" in sys.argv:
        i = sys.argv.index("--scale")
        if i + 1 < len(sys.argv):
            return float(sys.argv[i + 1])
    return SCALE


def main():
    global TARGET, SCALE, SRC
    SRC = arg_src()
    TARGET = arg_target()
    SCALE = arg_scale()
    write = "--write" in sys.argv
    font = TTFont(SRC)
    upem = font["head"].unitsPerEm
    if "glyf" not in font:
        print(f"{os.path.basename(SRC)} has CFF outlines, not glyf — this script only rewrites "
              f"TrueType. Noto's .otf would need a pen-based (CFF) rewrite.")
        return 3
    glyf = font["glyf"]
    hmtx = font["hmtx"]

    adv_hist = Counter(w for _, (w, _) in hmtx.metrics.items())
    full_adv = adv_hist.most_common(1)[0][0]
    targets = [g for g, (w, _) in hmtx.metrics.items() if w == full_adv]
    print(f"upem={upem}  source advance={full_adv} ({full_adv/upem:.2f}em)  target={TARGET} ({TARGET/upem:.2f}em)  glyphs={len(targets)}")

    inks, over = [], 0
    for g in targets:
        gl = glyf[g]
        if gl.numberOfContours == 0:
            continue
        gl.recalcBounds(glyf)
        ink = gl.xMax - gl.xMin
        inks.append(ink)
        if ink > TARGET:
            over += 1
    inks.sort()
    if not inks:
        print("no outlines found on that advance — abort")
        return 1
    print(f"ink width: min={inks[0]} p50={inks[len(inks)//2]} p95={inks[int(len(inks)*0.95)]} max={inks[-1]}")

    if over:
        print(f"note: {over} glyph(s) wider than {TARGET} — those get condensed horizontally")

    if not write:
        print("dry run — pass --write to build the font")
        return 0

    cmap = font.getBestCmap()
    names = {}
    for cp, g in cmap.items():
        names.setdefault(g, cp)

    condensed = 0
    for g in targets:
        gl = glyf[g]
        if gl.numberOfContours == 0:
            hmtx[g] = (TARGET, 0)
            continue
        if gl.isComposite():
            raise SystemExit(f"composite glyph {g} on the full-width advance — unsupported")
        gl.recalcBounds(glyf)
        cx = (gl.xMin + gl.xMax) / 2

        coords, endPts, flags = gl.getCoordinates(glyf)
        gl.coordinates = type(coords)([
            (round(cx + (x - cx) * SCALE), round(y * SCALE)) for (x, y) in coords
        ])
        gl.flags = flags
        gl.endPtsOfContours = endPts
        gl.recalcBounds(glyf)

        ink = gl.xMax - gl.xMin
        if ink > TARGET:
            k = TARGET / ink
            x0 = gl.xMin
            coords, endPts, flags = gl.getCoordinates(glyf)
            gl.coordinates = type(coords)([(round((x - x0) * k), y) for (x, y) in coords])
            gl.flags = flags
            gl.endPtsOfContours = endPts
            gl.recalcBounds(glyf)
            condensed += 1

        dx = round((TARGET - (gl.xMax - gl.xMin)) / 2 - gl.xMin)
        coords, endPts, flags = gl.getCoordinates(glyf)
        gl.coordinates = type(coords)([(x + dx, y) for (x, y) in coords])
        gl.flags = flags
        gl.endPtsOfContours = endPts
        gl.recalcBounds(glyf)
        hmtx[g] = (TARGET, gl.xMin)
    if condensed:
        print(f"  {condensed} glyph(s) still wider than the advance — condensed horizontally")

    for rec in font["name"].names:
        if rec.nameID in (1, 3, 4, 6, 16):
            try:
                old = rec.toUnicode()
            except Exception:
                continue
            new = {
                1: FAMILY,
                3: f"{FAMILY};1.000;TIGHT",
                4: f"{FAMILY} Regular",
                6: FAMILY.replace(" ", "") + "-Regular",
                16: FAMILY,
            }[rec.nameID]
            rec.string = new
            print(f"  name[{rec.nameID}] {old!r} -> {new!r}")

    font.save(DST)
    print("wrote", DST, f"{os.path.getsize(DST)/1048576:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
