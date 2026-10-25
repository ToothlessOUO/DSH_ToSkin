from fontTools.ttLib import TTFont

for p in (r"font-lab\fonts\MapleMonoCN-Regular.ttf", r"font-lab\fonts\MapleMonoCNTight-Regular.ttf"):
    f = TTFont(p, fontNumber=0, lazy=True)
    cm = f.getBestCmap()
    hm = f["hmtx"]
    print(p.split("\\")[-1])
    print("   M adv =", hm[cm[ord("M")]][0], " 国 adv =", hm[cm[ord("国")]][0],
          " ，adv =", hm[cm[ord("，")]][0])
    names = {r.nameID: r.toUnicode() for r in f["name"].names if r.nameID in (1, 6)}
    print("   names:", names)
