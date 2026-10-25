import collections
from fontTools.ttLib import TTFont

p = r"font-lab\fonts\MapleMonoCN-Regular.ttf"
f = TTFont(p, fontNumber=0, lazy=True)
cmap = f.getBestCmap()
hmtx = f["hmtx"]

cjk_adv = collections.Counter()
for cp, g in cmap.items():
    if 0x4E00 <= cp <= 0x9FFF:
        cjk_adv[hmtx[g][0]] += 1
print("CJK advances:", cjk_adv.most_common(6))
print("CJK glyph count:", sum(cjk_adv.values()))

tags = sorted({r.FeatureTag for r in f["GSUB"].table.FeatureList.FeatureRecord}) if "GSUB" in f else []
print("GSUB:", tags)
