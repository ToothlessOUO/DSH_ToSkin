import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "font-lab", "fonts")
W = os.path.join(os.environ["WINDIR"], "Fonts")

LINE = "把会话、模型与工具排成一条流水线，左边是进度，右边是结果。"

FACES = {
    "微软雅黑": (os.path.join(W, "msyh.ttc"), 0),
    "HarmonyOS": (os.path.join(FONTS, "HarmonyOSSC-Regular.ttf"), 0),
    "MiSans": (os.path.join(FONTS, "MiSans-Regular.otf"), 0),
    "PuHuiTi3": (os.path.join(FONTS, "PuHuiTi35-Regular.ttf"), 0),
    "得意黑": (os.path.join(FONTS, "SmileySans-Oblique.ttf"), 0),
}

print(f"{'face':12} {'13px黑度':>9} {'13px宽':>8} {'34px/700黑度':>13}")
for name, (path, idx) in FACES.items():
    f13 = ImageFont.truetype(path, 13, index=idx)
    w13 = f13.getlength(LINE)
    img = Image.new("L", (int(w13) + 4, 24), 0)
    d = ImageDraw.Draw(img)
    d.text((2, 2), LINE, font=f13, fill=255)
    px = list(img.getdata())
    cov = sum(1 for p in px if p > 96) / len(px)

    # bold display line at 34px: use the bold companion where we have one
    boldmap = {
        "微软雅黑": os.path.join(W, "msyhbd.ttc"),
        "HarmonyOS": os.path.join(FONTS, "HarmonyOSSC-Bold.ttf"),
        "MiSans": os.path.join(FONTS, "MiSans-Bold.otf"),
        "PuHuiTi3": os.path.join(FONTS, "PuHuiTi35-Bold.ttf"),
        "得意黑": os.path.join(FONTS, "SmileySans-Oblique.ttf"),
    }
    f34 = ImageFont.truetype(boldmap[name], 34, index=0)
    t = "黑橙硬件工作台"
    w34 = int(f34.getlength(t)) + 4
    img2 = Image.new("L", (w34, 50), 0)
    d2 = ImageDraw.Draw(img2)
    d2.text((2, 2), t, font=f34, fill=255)
    px2 = list(img2.getdata())
    cov2 = sum(1 for p in px2 if p > 96) / len(px2)
    print(f"{name:12} {cov*100:8.1f}% {w13:8.0f} {cov2*100:12.1f}%")
