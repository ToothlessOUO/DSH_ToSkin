"""Spacing ladder for Maple Mono CN: 1.2em stock down to 0.92em."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rs", os.path.join(HERE, "render-specimen.py"))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

PAD = rs.PAD
Sheet, mono, bahn, yahei, tw = rs.Sheet, rs.mono, rs.bahn, rs.yahei, rs.tw
INK, DIM, BRAND = rs.INK, rs.DIM, rs.BRAND
kind_of, adv_units, masthead = rs.kind_of, rs.adv_units, rs.masthead
FONTS = rs.FONTS

LOOSE = os.path.join(FONTS, "MapleMonoCN-Regular.ttf")
TIGHT = os.path.join(FONTS, "MapleMonoCNTight-Regular.ttf")   # built at 0.96em
SIZE = 12.5
LH = 1.62 * SIZE
COL = 380

TEXT = ("把会话、模型与工具排成一条流水线，左边是进度，右边是结果。"
        "中文换到等宽字面之后，每行能放下的字会少一成多，长句和注释都会提前折行。")

STEPS = [
    ("原版", "1.20 EM", LOOSE, 1.20, 1.00, 11.3, DIM),
    ("现在", "0.96 EM", LOOSE, 0.96, 1.00, 11.3, DIM),
    ("再小一点", "0.94 格 · 0.97 面", TIGHT, 0.94, 1.00, 11.0, BRAND),
]


def wrap(text, adv, limit):
    lines, cur, w = [], "", 0.0
    for ch in text:
        a = adv(ch)
        if w + a > limit and cur:
            lines.append(cur)
            cur, w = "", 0.0
        cur += ch
        w += a
    if cur:
        lines.append(cur)
    return lines


def column(sh, x, y, title, tag, path, em):
    def adv(ch):
        return em * SIZE if kind_of(ch) == "cjk" else tw(bahn(SIZE), ch)

    lines = wrap(TEXT, adv, COL)
    h = 30 + len(lines) * LH + 10
    sh.mixed(x, y + 18, title, mono(9), yahei(9), BRAND if "再小" in title else DIM, 1.4)
    tw_tag = sum((tw(mono(8), ch) + 0.7) for ch in tag) - 0.7
    sh.mixed(x + COL - tw_tag, y + 18, tag, mono(8), yahei(8), rs.blend(DIM, 0.3), 0.7)

    latin = bahn(SIZE)
    cjk = rs.f(path, SIZE)
    cy = y + 30 + SIZE * 0.82
    for ln in lines:
        cx = x
        for ch in ln:
            ft = cjk if kind_of(ch) == "cjk" else latin
            sh.d.text((cx * rs.S, cy * rs.S), ch, font=ft, fill=INK, anchor="ls")
            cx += adv(ch)
        cy += LH
    return len(lines), y + h


def main():
    sh = Sheet(520)
    masthead(sh, "再小一点", "同一段话、同一列宽 380px · 12.5px · 格子收到 0.94，字面再缩 3%",
             ["1.20 / 0.96 / 0.94", "SIZE 12.5 PX", "COL 380 PX"], yahei)
    sh.y += 16

    y = sh.y
    x = PAD
    bottom = y
    for title, tag, path, em, scale, ink, accent in STEPS:
        n, b = column(sh, x, y, title, tag, path, em)
        sh.mixed(x, b + 14, f"{n} 行 · 格 {em * SIZE:.1f}px · 面 {ink:.1f}px",
                 mono(8.5), yahei(8.5), accent, 0.5)
        bottom = max(bottom, b + 14)
        x += COL + 26

    fy = bottom + 26
    sh.mixed(PAD, fy, "格子 0.94：字与字的间距比刚才窄 2%；字面 0.97：每个字本身小 3%（墨迹 11.3 到 11.0px，和雅黑一个量级）。",
             bahn(11), yahei(11), rs.blend(DIM, 0.1))
    sh.mixed(PAD, fy + 18, "两档都收，是因为「小」既可能是嫌挤、也可能是嫌字号大；再往下走 0.92 格汉字就要贴边了（墨迹 0.90em / 格 0.92em）。",
             bahn(11), yahei(11), rs.blend(DIM, 0.3))
    sh.save("zone-maple-ladder.png")


if __name__ == "__main__":
    main()
