"""Maple Tight (current) vs Noto Sans Mono CJK SC, in the skin's sizes."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rs", os.path.join(HERE, "render-specimen.py"))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

PAD = rs.PAD
Sheet, mono, bahn, yahei, tw = rs.Sheet, rs.mono, rs.bahn, rs.yahei, rs.tw
INK, DIM, BRAND = rs.INK, rs.DIM, rs.BRAND
kind_of, masthead, FONTS = rs.kind_of, rs.masthead, rs.FONTS

MAPLE = os.path.join(FONTS, "MapleMonoCNTight-Regular.ttf")
NOTO_R = os.path.join(FONTS, "NotoSansMonoCJKsc-Regular.otf")
NOTO_B = os.path.join(FONTS, "NotoSansMonoCJKsc-Bold.otf")

SIZE = 12.5
LH = 1.62 * SIZE
COL = 380

TEXT = ("把会话、模型与工具排成一条流水线，左边是进度，右边是结果。"
        "中文换到等宽字面之后，每行能放下的字会少一成多，长句和注释都会提前折行。")

ROWS = [
    ("现在 · MAPLE MONO CN TIGHT", "0.94 格 · 0.97 面", MAPLE, 0.94, 11.0),
    ("换 · NOTO SANS MONO CJK SC", "1.00 格 · 1.00 面", NOTO_R, 1.00, 11.5),
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
    sh.mixed(x, y + 18, title, mono(9), yahei(9), BRAND if "NOTO" in title else DIM, 1.4)
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
    masthead(sh, "换 Noto", "思源黑体骨架 + 2:1 等宽 · 12.5px 正文 / 34px 标题 · 同一列宽 380px",
             ["NOTO 2 WEIGHTS", "CJK 1.00 EM", "LATIN 0.50 EM"], yahei)
    sh.y += 16

    y = sh.y
    x = PAD
    for title, tag, path, em, ink in ROWS:
        n, b = column(sh, x, y, title, tag, path, em)
        sh.mixed(x, b + 14, f"{n} 行 · 格 {em * SIZE:.1f}px · 面 {ink:.1f}px", mono(8.5), yahei(8.5),
                 BRAND if "NOTO" in title else DIM, 0.5)
        x += COL + 60

    dy = y + 4 * LH + 70
    sh.text(PAD, dy, "黑橙硬件工作台", rs.f(MAPLE, 34), INK)
    sh.mixed(PAD, dy + 18, "Maple Tight · 只有一个 Regular 字重", mono(8), yahei(8), rs.blend(DIM, 0.3), 0.6)

    nx = PAD + 420
    sh.text(nx, dy, "黑橙硬件工作台", rs.f(NOTO_B, 34), INK)
    sh.mixed(nx, dy + 18, "Noto · 真 Bold（700），600 的标题不再靠合成粗体", mono(8), yahei(8),
             rs.blend(DIM, 0.3), 0.6)

    fy = dy + 52
    sh.mixed(PAD, fy, "Noto 的字面比 Maple 大一点（0.921 / 0.903 em）、字高多 2%，格子回到 1.00，所以整体会比刚才松一档、也大一点。",
             bahn(11), yahei(11), rs.blend(DIM, 0.1))
    sh.mixed(PAD, fy + 18, "要 Noto 的形状 + 刚才的密度，用同一个脚本再压一版：--target 940 --scale 0.97。",
             bahn(11), yahei(11), rs.blend(DIM, 0.3))
    sh.save("zone-noto-mono.png")


if __name__ == "__main__":
    main()
