import os
from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FL = os.path.join(ROOT, "font-lab", "fonts")
W = os.path.join(os.environ["WINDIR"], "Fonts")

FACES = {
    "Cascadia Mono": (os.path.join(W, "CascadiaMono.ttf"), 0, None),
    "Sarasa Mono SC": (os.path.join(FL, "SarasaMonoSC-Regular.ttf"), 0, None),
    "Maple Mono CN": (os.path.join(FL, "MapleMonoCN-Regular.ttf"), 0, None),
    "Noto Sans Mono CJK": (os.path.join(FL, "NotoSansMonoCJKsc-Regular.otf"), 0, None),
    "微软雅黑(回退)": (os.path.join(W, "msyh.ttc"), 0, None),
    "HarmonyOS SC": (os.path.join(FL, "HarmonyOSSC-Regular.ttf"), 0, None),
    "Bahnschrift": (os.path.join(W, "bahnschrift.ttf"), 0, [400, 100]),
}


def has_glyph(path, ch, idx=0):
    from fontTools.ttLib import TTFont
    f = TTFont(path, fontNumber=idx)
    return ord(ch) in set(f.getBestCmap())


print(f"{'face':16} {'latin':>7} {'cjk':>7} {'cjk/latin':>10}  {'tabular':>8}  cjk?")
for name, (path, idx, axes) in FACES.items():
    ft = ImageFont.truetype(path, 100, index=idx)
    if axes:
        try:
            ft.set_variation_by_axes(axes)
        except Exception:
            pass
    latin = ft.getlength("M")
    cjk = ft.getlength("国")
    has = has_glyph(path, "国", idx)
    digits = {round(ft.getlength(d), 2) for d in "0123456789"}
    print(f"{name:20} {latin:7.2f} {cjk:7.2f} {cjk/latin:10.3f}  {str(len(digits)==1):>8}  {has}")
