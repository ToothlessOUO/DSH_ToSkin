from collections import Counter
from fontTools.ttLib import TTFont

f = TTFont(r"font-lab\fonts\MapleMonoCN-Regular.ttf")
glyf = f["glyf"]
hmtx = f["hmtx"]
full = Counter(w for w, _ in hmtx.metrics.values()).most_common(1)[0][0]
targets = [g for g, (w, _) in hmtx.metrics.items() if w == full]
comp = [g for g in targets if glyf[g].numberOfContours == -1]
print("full-width glyphs:", len(targets), "| composites:", len(comp), comp[:5])
