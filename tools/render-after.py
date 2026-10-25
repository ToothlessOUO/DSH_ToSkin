"""Before/after: Chinese set in Maple Mono CN (1.2em lattice) vs YaHei (1em)."""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rs", os.path.join(HERE, "render-specimen.py"))
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

PAD, W, CW = rs.PAD, rs.W, rs.CW
Sheet, mono, bahn, yahei, mix, blend = rs.Sheet, rs.mono, rs.bahn, rs.yahei, rs.mix, rs.blend
INK, DIM, BRAND, DEEP, BASE, L1 = rs.INK, rs.DIM, rs.BRAND, rs.DEEP, rs.BASE, rs.L1
tw, adv_units, kind_of, masthead = rs.tw, rs.adv_units, rs.kind_of, rs.masthead

MAPLE = os.path.join(rs.FONTS, "MapleMonoCN-Regular.ttf")
SIZE = 12.5
LH = SIZE * 1.62
COL_W = 500

TEXT = ("把会话、模型与工具排成一条流水线，左边是进度，右边是结果。"
        "中文换到等宽字面之后，每行能放下的字会少一成多，长句和注释都会提前折行，"
        "读起来更像终端里的输出，而不是文档里的正文；折行位置一变，段落的节奏也就跟着变了。")


def advances(cjk_em):
    latin = bahn(SIZE)
    return lambda ch: (cjk_em * SIZE if kind_of(ch) == "cjk" else tw(latin, ch))


def wrap(text, adv):
    lines, cur, w = [], "", 0.0
    for ch in text:
        a = adv(ch)
        if w + a > COL_W and cur:
            lines.append(cur)
            cur, w = "", 0.0
        cur += ch
        w += a
    if cur:
        lines.append(cur)
    return lines


def panel(sh, x, y, title, note, cjk_em, cjk_font_path, accent=INK):
    adv = advances(cjk_em)
    lines = wrap(TEXT, adv)
    h = 34 + len(lines) * LH + 14
    sh.rect((x, y, x + COL_W + 24, y + h), fill=(30, 26, 24), r=8)
    sh.mixed(x + 12, y + 22, title, mono(9), yahei(9), accent, 1.4)
    sh.text(x + COL_W + 12 - tw(mono(8), note), y + 22, note, mono(8), blend(DIM, 0.25), "ls", 0.8)

    latin = bahn(SIZE)
    cjk = rs.f(cjk_font_path or os.path.join(rs.WIN_FONTS, "msyh.ttc"), SIZE)
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
    sh_h = int(180 + 34 + 6 * LH + 120)
    sh = Sheet(sh_h)
    masthead(sh, "换成 Maple Mono CN", "中文落到 1.2em 等宽格 · 同一段话、同一列宽（500px）",
             ["SIZE 12.5 PX", "COL 500 PX", "CJK 1.20 EM", "LH 1.62"], yahei)
    sh.y += 18

    y = sh.y
    l1, h1 = panel(sh, PAD, y, "现状 · 微软雅黑", "1.00 EM", 1.0, None, blend(INK, 0.0))
    l2, h2 = panel(sh, PAD + COL_W + 60, y, "MAPLE MONO CN", "1.20 EM", 1.2, MAPLE, BRAND)

    # line-count readout under each panel
    for i, (lines, x) in enumerate([(l1, PAD), (l2, PAD + COL_W + 60)]):
        maxc = max(len(ln) for ln in lines)
        w10 = advances(1.0 if i == 0 else 1.2)("国") * 10
        sh.mixed(x, y + max(h1, h2) + 26, f"{len(lines)} 行 · 单行最多 {maxc} 字 · 每 10 字 {w10:.0f}px",
                 mono(9), yahei(9), BRAND if i else DIM, 0.6)

    fy = y + max(h1, h2) + 62
    sh.mixed(PAD, fy, "中文每字 15.0px（原 12.5px）：同宽一列少 17% 的字，1000px 的聊天区一行从 76 字掉到 64 字。",
             bahn(11.5), yahei(11.5), DIM)
    sh.mixed(PAD, fy + 20, "字面色本身按 2:1 设计，正文字距因此比黑体松约 0.3em；看起来是终端/HUD 的调子，不是正文的调子。",
             bahn(11.5), yahei(11.5), DIM)
    sh.mixed(PAD, fy + 40, "英文与数字不动：Bahnschrift 仍在前，Maple 只补汉字。",
             bahn(11.5), yahei(11.5), mix(BRAND, DIM, 0.35))

    sh.save("zone-maple-after.png")


if __name__ == "__main__":
    main()
