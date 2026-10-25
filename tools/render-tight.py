"""Loose vs tight Maple: same glyphs, 1.2em vs 1.0em CJK advance."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rs", os.path.join(HERE, "render-specimen.py"))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

PAD, CW = rs.PAD, rs.CW
Sheet, mono, bahn, yahei = rs.Sheet, rs.mono, rs.bahn, rs.yahei
INK, DIM, BRAND = rs.INK, rs.DIM, rs.BRAND
tw, kind_of, adv_units, masthead = rs.tw, rs.kind_of, rs.adv_units, rs.masthead
FONTS = rs.FONTS

LOOSE = os.path.join(FONTS, "MapleMonoCN-Regular.ttf")
TIGHT = os.path.join(FONTS, "MapleMonoCNTight-Regular.ttf")
SIZE = 12.5
LH = SIZE * 1.62
COL_W = 500

TEXT = ("把会话、模型与工具排成一条流水线，左边是进度，右边是结果。"
        "中文换到等宽字面之后，每行能放下的字会少一成多，长句和注释都会提前折行，"
        "读起来更像终端里的输出，而不是文档里的正文；折行位置一变，段落的节奏也就跟着变了。")


def adv_fn(font_path, size):
    return lambda ch: (adv_units(font_path, ch) * size if kind_of(ch) == "cjk"
                       else tw(bahn(size), ch))


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


def panel(sh, x, y, title, note, path, accent=INK):
    adv = adv_fn(path, SIZE)
    lines = wrap(TEXT, adv, COL_W)
    h = 34 + len(lines) * LH + 14
    sh.rect((x, y, x + COL_W + 24, y + h), fill=(30, 26, 24), r=8)
    sh.mixed(x + 12, y + 22, title, mono(9), yahei(9), accent, 1.4)
    sh.text(x + COL_W + 12 - tw(mono(8), note), y + 22, note, mono(8), rs.blend(DIM, 0.25), "ls", 0.8)

    latin = bahn(SIZE)
    cjk = rs.f(path, SIZE)
    cy = y + 34 + SIZE * 0.82
    for ln in lines:
        cx = x + 12
        for ch in ln:
            ft = cjk if kind_of(ch) == "cjk" else latin
            sh.d.text((cx * rs.S, cy * rs.S), ch, font=ft, fill=INK, anchor="ls")
            cx += adv(ch)
        cy += LH
    return lines, h


def main():
    sh = Sheet(int(320 + 34 + 6 * LH + 150))
    masthead(sh, "收紧到 1.0em", "同样的字形，只改等宽格：汉字前进宽度 15.0px 收紧到 12.5px（12.5px 字号）",
             ["GLYPHS SAME", "CJK 1.00 EM", "LATIN 0.60 EM", "COL 500 PX"], yahei)
    sh.y += 18
    y = sh.y
    l1, h1 = panel(sh, PAD, y, "原版 · MAPLE MONO CN", "1.20 EM", LOOSE, DIM)
    l2, h2 = panel(sh, PAD + COL_W + 60, y, "紧排版 · MAPLE MONO CN TIGHT", "1.00 EM", TIGHT, BRAND)

    for i, (lines, x) in enumerate([(l1, PAD), (l2, PAD + COL_W + 60)]):
        maxc = max(len(ln) for ln in lines)
        pitch = 15.6 if i == 0 else 12.5
        sh.mixed(x, y + max(h1, h2) + 26,
                 f"{len(lines)} 行 · 单行最多 {maxc} 字 · 字距 {pitch:.1f}px",
                 mono(9), yahei(9), BRAND if i else DIM, 0.6)

    # display-size check
    dy = y + max(h1, h2) + 70
    big = rs.f(TIGHT, 34)
    wbig = sh.text(PAD, dy, "黑橙硬件工作台", big, INK)
    sh.text(PAD + wbig + 8, dy, "01", bahn(34, 700, 90), INK)
    sh.mixed(PAD, dy + 22, "34px 紧排版：字面 0.91em，两侧各留 0.045em，不粘连", mono(8.5), yahei(8.5),
             rs.blend(DIM, 0.2), 0.7)

    fy = dy + 52
    sh.mixed(PAD, fy, "只动汉字与全角标点的前进宽度，轮廓一个点都没改；拉丁仍是 0.60em，所以代码里的 2:1 变成 1.67:1（和雅黑一样）。",
             bahn(11.5), yahei(11.5), DIM)
    sh.save("zone-maple-tight.png")


if __name__ == "__main__":
    main()
