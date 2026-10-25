"""How big would a bundled Noto Sans Mono CJK SC get? full woff2 vs GB2312 subset."""
import io
import os
import time

from fontTools import subset
from fontTools.ttLib import TTFont

FL = os.path.join("font-lab", "fonts")
REG = os.path.join(FL, "NotoSansMonoCJKsc-Regular.otf")
BOLD = os.path.join(FL, "NotoSansMonoCJKsc-Bold.otf")


def gb2312_chars():
    out = set()
    for hi in range(0xB0, 0xF8):
        for lo in range(0xA1, 0xFF):
            try:
                out.add(bytes([hi, lo]).decode("gb2312"))
            except UnicodeDecodeError:
                pass
    return out


def subset_size(path, chars, flavor="woff2", label=""):
    font = TTFont(path)
    opts = subset.Options()
    opts.flavor = flavor
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables += ["DSIG"]
    sub = subset.Subsetter(options=opts)
    sub.populate(unicodes={ord(c) for c in chars})
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    return len(buf.getvalue())


base = {chr(c) for c in range(0x20, 0x7F)}
punct = set("　、。，．・：；？！“”‘’（）【】《》〈〉「」『』—…·～％＃＠＆")
gb = gb2312_chars()
full_set = base | punct | gb
print(f"charset: ascii {len(base)} + punct {len(punct)} + GB2312 {len(gb)} = {len(full_set)}")

for name, path in (("Regular", REG), ("Bold", BOLD)):
    t0 = time.time()
    w = subset_size(path, full_set, "woff2")
    print(f"{name:8} subset woff2 = {w/1048576:6.2f} MB  ({time.time()-t0:.0f}s)  base64 ≈ {w*4/3/1048576:5.2f} MB")
