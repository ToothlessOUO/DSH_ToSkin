"""Render the ZONE Chinese type specimen with real font files (no browser)."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FL = os.path.join(ROOT, "font-lab")
FONTS = os.path.join(FL, "fonts")
OUT = os.path.join(FL, "out")
os.makedirs(OUT, exist_ok=True)

S = 2  # supersample factor
W = 1280
PAD = 40
CW = W - PAD * 2

DEEP = (20, 17, 16)
BASE = (44, 41, 39)
L1 = (55, 51, 48)
L2 = (66, 61, 58)
INK = (248, 243, 232)
DIM = (204, 193, 176)
LINE = (84, 76, 70)
BRAND = (255, 111, 26)
WHITE = (255, 255, 255)

WIN_FONTS = os.path.join(os.environ["WINDIR"], "Fonts")


def f(path, size, index=0):
    return ImageFont.truetype(path, int(round(size * S)), index=index)


def mono(size):
    return f(os.path.join(WIN_FONTS, "CascadiaMono.ttf"), size)


def bahn(size, wght=400, wdth=100):
    font = f(os.path.join(WIN_FONTS, "bahnschrift.ttf"), size)
    try:
        font.set_variation_by_axes([wght, wdth])
    except Exception:
        pass
    return font


def sym(size):
    return f(os.path.join(WIN_FONTS, "seguisym.ttf"), size)


def yahei(size, bold=False):
    return f(os.path.join(WIN_FONTS, "msyhbd.ttc" if bold else "msyh.ttc"), size)


def harmony(size, weight=400):
    name = {400: "Regular", 500: "Medium", 700: "Bold"}.get(weight, "Regular")
    return f(os.path.join(FONTS, f"HarmonyOSSC-{name}.ttf"), size)


def misans(size, weight=400):
    name = {400: "Regular", 600: "Semibold", 700: "Bold"}.get(weight, "Regular")
    return f(os.path.join(FONTS, f"MiSans-{name}.otf"), size)


def puhui(size, weight=400):
    name = {400: "Regular", 600: "SemiBold", 700: "Bold"}.get(weight, "Regular")
    return f(os.path.join(FONTS, f"PuHuiTi35-{name}.ttf"), size)


def smiley(size):
    return f(os.path.join(FONTS, "SmileySans-Oblique.ttf"), size)


def tw(font, s):
    return font.getlength(s) / S


def tw_tracked(font, s, tracking):
    return tw(font, s) + tracking * max(0, len(s) - 1)


_METRICS = {}


def adv_units(path, ch):
    """Design-unit advance from hmtx — FreeType rounds to pixels, this does not."""
    from fontTools.ttLib import TTFont
    if path not in _METRICS:
        ft = TTFont(path, fontNumber=0, lazy=True)
        _METRICS[path] = (ft["head"].unitsPerEm, ft.getBestCmap(), ft["hmtx"])
    upem, cmap, hmtx = _METRICS[path]
    g = cmap.get(ord(ch))
    return (hmtx[g][0] if g else upem // 2) / upem


def kind_of(ch):
    o = ord(ch)
    if ((0x2E80 <= o <= 0x9FFF) or (0xF900 <= o <= 0xFAFF)
            or (0xFF00 <= o <= 0xFF60) or (0x3000 <= o <= 0x303F)):
        return "cjk"
    if (0x2190 <= o <= 0x21FF) or (0x2300 <= o <= 0x23FF) or (0x25A0 <= o <= 0x27BF) \
            or (0x2B00 <= o <= 0x2BFF) or (0xFE0F <= o <= 0xFE0F):
        return "sym"
    return "latin"


def runs(text):
    out, buf, kind = [], "", None
    for ch in text:
        k = kind_of(ch)
        if k != kind and buf:
            out.append((kind, buf))
            buf = ""
        kind = k
        buf += ch
    if buf:
        out.append((kind, buf))
    return out


def mix(a, b, t):
    return tuple(int(round(a[i] * (1 - t) + b[i] * t)) for i in range(3))


def blend(c, t):
    return mix(c, DEEP, t)


class Sheet:
    def __init__(self, height):
        self.img = Image.new("RGB", (W * S, height * S), DEEP)
        self.d = ImageDraw.Draw(self.img)
        self.y = 0

    def text(self, x, y, s, font, fill=INK, anchor="ls", tracking=0):
        if tracking:
            cx = x
            for ch in s:
                self.d.text((cx * S, y * S), ch, font=font, fill=fill, anchor=anchor)
                cx += tw(font, ch) + tracking
            return cx - tracking - x
        self.d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor)
        return tw(font, s)

    def mixed(self, x, y, s, latin, cjk, fill=INK, tracking=0, symbol=None):
        symbol = symbol or sym(1)
        cx = x
        for kind, chunk in runs(s):
            ft = {"latin": latin, "cjk": cjk, "sym": symbol}[kind]
            self.text(cx, y, chunk, ft, fill, "ls", tracking)
            cx += tw(ft, chunk) + tracking * len(chunk)
        return cx - x

    def rect(self, box, fill=None, outline=None, width=1, r=0):
        box = tuple(v * S for v in box)
        if r:
            self.d.rounded_rectangle(box, radius=r * S, fill=fill, outline=outline, width=width * S)
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=width * S)

    def line(self, x1, y1, x2, y2, fill=LINE, width=1):
        self.d.line((x1 * S, y1 * S, x2 * S, y2 * S), fill=fill, width=width * S)

    def hline(self, x, y, w, fill=LINE, width=1):
        self.line(x, y, x + w, y, fill, width)

    def save(self, name, pad=40):
        from PIL import ImageChops
        bg = Image.new("RGB", self.img.size, DEEP)
        bbox = ImageChops.difference(self.img, bg).getbbox()
        bottom = self.img.height if not bbox else min(self.img.height, bbox[3] + pad * S)
        img = self.img.crop((0, 0, self.img.width, bottom))
        p = os.path.join(OUT, name)
        img.save(p, "PNG")
        print("wrote", p, img.size)


def masthead(sh, title, sub, meta_lines, label_cjk):
    y = PAD + 6
    sh.rect((PAD, y, PAD + 54, y + 54), fill=DEEP, outline=BRAND, width=2, r=13)
    sh.text(PAD + 27, y + 27, "Z", bahn(30, 700, 88), INK, "mm")
    tx = PAD + 54 + 16
    sh.mixed(tx, y + 30, title, bahn(30, 700, 88), label_cjk(30, True) if callable(label_cjk) else label_cjk, INK)
    sh.mixed(tx, y + 52, sub, bahn(12.5), label_cjk(12.5) if callable(label_cjk) else label_cjk, DIM)

    mf = mono(9)
    xr = W - PAD
    yy = y + 20
    for ln in meta_lines:
        wln = tw_mixed(ln, mf, yahei(9)) + 1.6 * max(0, len(ln) - 1)
        sh.mixed(xr - wln, yy, ln, mf, yahei(9), DIM, 1.6)
        yy += 15
    sh.y = y + 54 + 18
    sh.hline(PAD, sh.y, CW, (124, 58, 22), 1)


CANDIDATES = [
    dict(
        idx="01 / 现状", name="微软雅黑", cn="Microsoft YaHei",
        meta=["系统自带 · 3 字重", "当前 CJK 回退"], tag="BASELINE", mute=True,
        cjk=yahei, bold=lambda s: yahei(s, True),
        verdict="笔画端点偏圆、字面偏宽，和 Bahnschrift 的方硬骨架打架；小字有点糊。",
    ),
    dict(
        idx="02 / 首选", name="HarmonyOS Sans SC", cn="鸿蒙黑体",
        meta=["华为 · 免费商用", "6 字重 · 已装本机"], tag="INSTALLED", mute=False,
        cjk=lambda s: harmony(s, 400), bold=lambda s: harmony(s, 700),
        verdict="结构最接近：方中带圆、字面略窄，9–13px 笔画不糊，和 DIN 骨架最顺。",
    ),
    dict(
        idx="03 / 产品感", name="MiSans", cn="小米 · 品牌字体",
        meta=["小米 · 免费商用", "10 字重"], tag="FREE", mute=True,
        cjk=lambda s: misans(s, 400), bold=lambda s: misans(s, 700),
        verdict="更中性、更像消费电子；字面偏宽，密度略松，深底上发灰但耐看。",
    ),
    dict(
        idx="04 / 工业感", name="阿里巴巴普惠体 3.0", cn="Alibaba PuHuiTi",
        meta=["阿里 · 免费商用", "105 款样式"], tag="105 STY", mute=True,
        cjk=lambda s: puhui(s, 400), bold=lambda s: puhui(s, 700),
        verdict="横竖更硬、转折更方，粗字重有机械感；9px 处略细，适合标题与盘面。",
    ),
    dict(
        idx="05 / 只做标题", name="得意黑", cn="Smiley Sans",
        meta=["SIL OFL 1.1", "单字重 · 斜切紧缩"], tag="DISPLAY", mute=True,
        cjk=lambda s: smiley(s), bold=lambda s: smiley(s),
        verdict="斜切 + 紧缩，像贴纸与赛车涂装；正文完全不能用，只进 hero 和 sticker。",
    ),
]

DISPLAY = "黑橙硬件工作台"
BODY = "把会话、模型与工具排成一条流水线，左边是进度，右边是结果。"
MIXED = "ZONE 橙 · 第 03 轮 · 2400 K / 87% · 画布 / 配色 / 动效"

ROW_H = 152


def overview():
    h = PAD + 6 + 54 + 18 + 24 + ROW_H * len(CANDIDATES) + 120
    sh = Sheet(h)
    masthead(sh, "中文候选字体", "ZONE skin / 与 Bahnschrift 同框 · 正文 13px · 标题 34px / 700",
             ["SPECIMEN 5", "LATIN BAHNSCHRIFT", "LABEL CASCADIA MONO", "REV R7 · 1280 PX"], yahei)
    sh.y += 16

    for i, c in enumerate(CANDIDATES):
        top = sh.y
        lx = PAD
        sh.mixed(lx, top + 6, c["idx"], mono(9), yahei(9), BRAND, 1.8)
        sh.text(lx, top + 28, c["name"], c["bold"](15), INK)
        sh.text(lx, top + 45, c["cn"], c["cjk"](11.5), mix(INK, DEEP, 0.38))
        my = top + 66
        for ln in c["meta"]:
            sh.mixed(lx, my, ln, bahn(9, 400, 95), c["cjk"](9), DIM)
            my += 14
        tf = mono(8.5)
        twid = tw_tracked(tf, c["tag"], 1.3)
        sh.rect((lx, my + 6, lx + twid + 14, my + 24),
                fill=mix(DEEP, BRAND, 0.14) if not c["mute"] else mix(DEEP, INK, 0.06),
                outline=mix(DEEP, BRAND, 0.5) if not c["mute"] else (70, 62, 56), width=1, r=4)
        sh.text(lx + 7, my + 20, c["tag"], tf, BRAND if not c["mute"] else DIM, "ls", 1.3)

        sx = PAD + 196 + 30
        sh.text(sx, top + 40, DISPLAY, c["bold"](34), INK)
        sh.mixed(sx, top + 78, BODY, bahn(13), c["cjk"](13), INK)
        sh.mixed(sx, top + 102, MIXED, bahn(11.5), c["cjk"](11.5), blend(DIM, 0.1))
        sh.text(sx, top + 128, "→", c["cjk"](11), BRAND)
        sh.mixed(sx + 14, top + 128, c["verdict"], bahn(11, 400, 95), c["cjk"](11), blend(DIM, 0.18))

        sh.y = top + ROW_H
        sh.hline(PAD, sh.y, CW, (56, 50, 46), 1)

    fy = sh.y + 28
    for col, (head, l1, l2) in enumerate([
        ("怎么判读", "大字号看骨架与重心，13px 看小字清晰度与行距节奏；灰字那行是真实混排——", "拉丁、数字、标点都来自 Bahnschrift，中文只补字形。"),
        ("共同前提", "拉丁与数字不动，只在 FONT_SANS 的中文回退位插一个族；", "中文不再走雅黑。"),
    ]):
        x = PAD + col * 640
        sh.mixed(x, fy, head, mono(9), yahei(9), BRAND, 1.8)
        sh.mixed(x, fy + 20, l1, bahn(11.5), yahei(11.5), DIM)
        sh.mixed(x, fy + 38, l2, bahn(11.5), yahei(11.5), DIM)

    sh.save("zone-cn-overview.png")


# ------------------------------------------------------------------ context

CARD_W = (CW - 22) // 2
SIDE_W = 172
CARD_H = 32 + 170


def tw_mixed(s, latin, cjk):
    w = 0
    for kind, chunk in runs(s):
        ft = {"latin": latin, "cjk": cjk, "sym": sym(1)}[kind]
        w += tw(ft, chunk)
    return w


def app_card(sh, x, y, w, cjk, bold, cap_name, cap_note, dot_color=BRAND):
    cap_h = 32
    sh.rect((x, y, x + w, y + cap_h), fill=L1)
    sh.hline(x, y + cap_h, w, (78, 70, 64), 1)
    sh.d.ellipse(((x + 12) * S, (y + 13) * S, (x + 19) * S, (y + 20) * S), fill=dot_color)
    sh.mixed(x + 27, y + 21, cap_name, mono(8.5), cjk(8.5), INK, 1.4)
    if cap_note:
        nf = mono(8)
        nw = tw_mixed(cap_note, nf, cjk(8)) + 0.8 * (len(cap_note) - 1)
        sh.mixed(x + w - 16 - nw, y + 21, cap_note, nf, cjk(8), DIM, 0.8)

    sh.rect((x, y + cap_h, x + w, y + CARD_H), fill=BASE)
    sh.rect((x, y + cap_h, x + SIDE_W, y + CARD_H), fill=(35, 32, 32))
    sh.rect((x + SIDE_W - 1, y + cap_h, x + SIDE_W, y + CARD_H), fill=(68, 60, 55))

    sy = y + cap_h
    sx = x + 8
    sh.text(sx + 6, sy + 18, "会话", cjk(8.5), mix(DIM, DEEP, 0.35), "ls", 1.5)
    rows = [("把半调网点做旧一点", True), ("ZONE 皮肤的配色分层", False), ("设备条 LED 为什么在闪", False)]
    ry = sy + 28
    for txt, sel in rows:
        need = tw_mixed(txt, bahn(12), cjk(12))
        rh = 24 if need < SIDE_W - 32 else 36
        if sel:
            sh.rect((sx, ry, sx + SIDE_W - 16, ry + rh - 4), fill=BRAND, r=5)
            sh.mixed(sx + 7, ry + 14, txt, bahn(12, 600), bold(12), WHITE)
        else:
            sh.mixed(sx + 7, ry + 14, txt, bahn(12), cjk(12), mix(INK, DEEP, 0.26))
        ry += rh + 4

    cx = x + SIDE_W + 14
    bf = cjk(12.5)
    btxt = "中文字体换成这个看看？"
    bw = tw_mixed(btxt, bahn(12.5, 500), bf) + 20
    bx = x + w - 14 - bw
    sh.rect((bx, sy + 12, bx + bw, sy + 12 + 30), fill=(210, 69, 15), r=8)
    sh.mixed(bx + 10, sy + 32, btxt, bahn(12.5, 500), bf, WHITE)

    msg = ["收到。正文换到 13px，标签继续用 Cascadia Mono，", "标题压到 600 先看两屏。"]
    my = sy + 62
    for ln in msg:
        draw_bold_token(sh, cx, my, ln, bahn(12.5), cjk(12.5), INK, "13px", bold(12.5))
        my += 21

    cy = sy + 112
    sh.rect((cx, cy, x + w - 14, cy + 34), fill=L2, outline=(96, 88, 82), width=1, r=9)
    sh.mixed(cx + 11, cy + 22, "输入消息，回车发送", bahn(12), cjk(12), DIM)
    sh.d.ellipse(((x + w - 48) * S, (cy + 7) * S, (x + w - 28) * S, (cy + 27) * S), fill=BRAND)
    ax, ay = x + w - 38, cy + 17
    sh.d.polygon([((ax) * S, (ay - 4) * S), ((ax - 4) * S, (ay + 2) * S),
                  ((ax + 4) * S, (ay + 2) * S)], fill=WHITE)
    sh.d.rectangle(((ax - 1) * S, (ay + 2) * S, (ax + 1) * S, (ay + 6) * S), fill=WHITE)

    by = cy + 46
    sh.d.ellipse((cx * S, (by - 3) * S, (cx + 6) * S, (by + 3) * S), fill=BRAND)
    sh.text(cx + 12, by + 3, "LIVE", mono(8), DIM, "ls", 1.5)
    tape_x = cx + 12 + tw_tracked(mono(8), "LIVE", 1.5) + 10
    sh.rect((tape_x, by - 3, x + w - 150, by + 2), fill=BRAND, r=2)
    sh.mixed(x + w - 138, by + 3, "ZONE 橙", mono(8), cjk(8), BRAND, 1.2)
    sh.text(x + w - 14 - tw_tracked(mono(8), "SHEET R7", 1.2), by + 3, "SHEET R7", mono(8), INK, "ls", 1.2)


def draw_bold_token(sh, x, y, s, latin, cjk, fill, token, bold_font):
    if token not in s:
        sh.mixed(x, y, s, latin, cjk, fill)
        return
    a, b = s.split(token, 1)
    cx = x + sh.mixed(x, y, a, latin, cjk, fill)
    cx += sh.mixed(cx, y, token, latin, bold_font, fill)
    sh.mixed(cx, y, b, latin, cjk, fill)


def context():
    cards = [
        ("现状 · 微软雅黑", "BASELINE", yahei, lambda s: yahei(s, True), (109, 100, 96)),
        ("02 · HarmonyOS Sans SC", "鸿蒙黑体", lambda s: harmony(s, 400), lambda s: harmony(s, 700), BRAND),
        ("03 · MiSans", "小米", lambda s: misans(s, 400), lambda s: misans(s, 700), BRAND),
        ("04 · 阿里巴巴普惠体 3.0", "Alibaba PuHuiTi", lambda s: puhui(s, 400), lambda s: puhui(s, 700), BRAND),
    ]
    h = PAD + 6 + 54 + 18 + 24 + CARD_H * 2 + 22 + 200
    sh = Sheet(h)
    masthead(sh, "界面内实测", "同一段界面文案 · 侧栏 12px / 正文 12.5px / 标签 8.5px mono",
             ["CANVAS BLACKSITE", "COLORWAY ZONE 橙", "REV R7 · 1280 PX"], yahei)
    sh.y += 16

    y0 = sh.y
    for i, (name, note, cjk, bold, dot) in enumerate(cards):
        col, row = i % 2, i // 2
        x = PAD + col * (CARD_W + 22)
        y = y0 + row * (CARD_H + 22)
        sh.rect((x, y, x + CARD_W, y + CARD_H), fill=BASE, outline=(78, 70, 64), width=1, r=12)
        app_card(sh, x, y, CARD_W, cjk, bold, name, note, dot)

    sh.y = y0 + 2 * (CARD_H + 22) + 18

    sh.mixed(PAD, sh.y + 6, "贴纸位 · 得意黑只在这里", mono(9), yahei(9), BRAND, 1.8)
    sh.hline(PAD + 220, sh.y + 3, CW - 220, (56, 50, 46), 1)
    sy = sh.y + 22
    specs = [("ZONE", bahn(25, 700, 88), "SKIN / 01", 0.50),
             ("皮肤 01", smiley(25), "SKIN / 02", 0.28),
             ("黑橙", smiley(25), "SKIN / 03", 0.22)]
    x = PAD
    for txt, ft, code, frac in specs:
        w = CW * frac
        sh.rect((x, sy, x + w - 12, sy + 46), fill=(239, 233, 219), r=10)
        sh.rect((x, sy, x + w - 12, sy + 46), outline=DEEP, width=2, r=10)
        sh.text(x + 12, sy + 31, txt, ft, DEEP)
        tape_x = x + 12 + tw(ft, txt) + 12
        cf = mono(8.5)
        cw = tw_tracked(cf, code, 1.4)
        sh.rect((tape_x, sy + 18, x + w - 12 - 14 - cw - 10, sy + 27), fill=DEEP, r=2)
        sh.mixed(x + w - 12 - 12 - cw, sy + 28, code, cf, yahei(8.5), blend((23, 19, 16), 0.3), 1.4)
        x += w

    sh.save("zone-cn-context.png")


def detail():
    glyphs = ["硬", "会", "橙", "语", "圆", "永"]
    rows = [
        ("现状 · 微软雅黑", yahei, "端点圆、字面宽"),
        ("HarmonyOS", lambda s: harmony(s, 400), "转折方、字面窄"),
        ("MiSans", lambda s: misans(s, 400), "骨架开、重心高"),
        ("PuHuiTi 3.0", lambda s: puhui(s, 400), "笔直、骨硬"),
        ("得意黑", lambda s: smiley(s), "斜切、紧缩"),
    ]
    cell = (CW - 200) / len(glyphs)
    row_h = 104
    h = PAD + 6 + 54 + 18 + 24 + row_h * len(rows) + 90
    sh = Sheet(h)
    masthead(sh, "字形对照", "六个常用字 · 56px / Regular · 放大看转折与封闭",
             ["GLYPHS 6", "SIZE 56 PX", "WEIGHT 400", "REV R7 · 1280 PX"], yahei)
    sh.y += 20

    for i, (name, mk, note) in enumerate(rows):
        top = sh.y
        lx = PAD
        sh.text(lx, top + 46, name, mk(13) if i > 0 else yahei(13, True), INK)
        sh.mixed(lx, top + 64, note, bahn(9.5, 400, 95), yahei(9.5), blend(DIM, 0.15))
        gx = PAD + 200
        for g in glyphs:
            ft = mk(56)
            gw = tw(ft, g)
            sh.text(gx + cell / 2 - gw / 2 - 6, top + 74, g, ft, INK)
            gx += cell
        sh.y = top + row_h
        sh.hline(PAD, sh.y, CW, (56, 50, 46), 1)

    sh.mixed(PAD, sh.y + 30, "看四件事：转折是方是圆、字面（中宫）是紧是松、横竖粗细比、封闭部件的“口”是否方正。",
             bahn(11), yahei(11), DIM)
    sh.mixed(PAD, sh.y + 50, "实测：中文均为整字宽 1em，换字不会换行（得意黑 0.77em 例外）；13px 黑度 雅黑 16.4 / 鸿蒙 15.4 / MiSans 15.8 / 普惠 15.6；34px/700 为 34.7 / 29.0 / 32.5 / 28.2。",
             bahn(11), yahei(11), mix(DIM, DEEP, 0.25))
    sh.save("zone-cn-detail.png")


# -------------------------------------------------------------------- mono

MONO_ROWS = [
    dict(name="Cascadia Mono", note="现状 · 无中文字形，回退雅黑", tag="BASELINE", mute=True,
         path=os.path.join(WIN_FONTS, "CascadiaMono.ttf"), cjk=None),
    dict(name="Sarasa Mono SC", note="更纱黑体 · Iosevka + 思源黑体", tag="RECOMMENDED", mute=False,
         path=os.path.join(FONTS, "SarasaMonoSC-Regular.ttf"), cjk="self"),
    dict(name="Maple Mono CN", note="圆角 + 连字 · 与 Cascadia 同为 0.6em", tag="0.6 EM", mute=True,
         path=os.path.join(FONTS, "MapleMonoCN-Regular.ttf"), cjk="self"),
    dict(name="Noto Sans Mono CJK SC", note="Google · 与思源黑体同源", tag="OFL", mute=True,
         path=os.path.join(FONTS, "NotoSansMonoCJKsc-Regular.otf"), cjk="self"),
]

CODE = [
    ("const 面板 = 测量(宽, 高);", "取一次就够"),
    ("const 会话 = 列表.map(渲染);", "每行都要对齐"),
    ("const 主题 = 主题包.读取('黑场');", "黑场 / 米白"),
]
COL = 46


def cols_of(s):
    return sum(2 if kind_of(ch) == "cjk" else 1 for ch in s)


def draw_mono(sh, x, y, s, path, size, fill, tracking=0, cjk_path=None):
    """Lay out a line with exact design-unit advances; CJK comes from cjk_path."""
    latin = f(path, size)
    cjk = f(cjk_path, size) if cjk_path else None
    cx = x
    for ch in s:
        from_cjk = cjk is not None and kind_of(ch) == "cjk"
        ft = cjk if from_cjk else latin
        sh.d.text((cx * S, y * S), ch, font=ft, fill=fill, anchor="ls")
        src = cjk_path if from_cjk else path
        cx += adv_units(src, ch) * size + tracking
    return cx - x


def mono_spec():
    row_h = 104
    h = PAD + 6 + 54 + 18 + 24 + row_h * len(MONO_ROWS) + 40 + 34 * len(MONO_ROWS) + 160
    sh = Sheet(h)
    masthead(sh, "等宽字体", "代码注释与设备条 · 13px 代码 / 9px 标签 · 中文字宽决定对齐",
             ["MONO 4", "CODE 13 PX", "LABEL 9 PX", "COL 46"], yahei)
    sh.y += 14

    code_size = 13
    for r in MONO_ROWS:
        top = sh.y
        lat_adv = adv_units(r["path"], "M") * code_size
        cjk_src = r["path"] if r["cjk"] == "self" else os.path.join(WIN_FONTS, "msyh.ttc")
        cjk_adv = adv_units(cjk_src, "国") * code_size
        ratio = cjk_adv / lat_adv

        lx = PAD
        sh.text(lx, top + 24, r["name"], f(r["path"], 13) if r["cjk"] == "self" else f(r["path"], 13), INK)
        sh.mixed(lx, top + 42, r["note"], bahn(9.5, 400, 95), yahei(9.5), blend(DIM, 0.2))
        sh.mixed(lx, top + 60, f"拉丁 {lat_adv:.2f}px · 中文 {cjk_adv:.2f}px · {ratio:.2f} 列",
                 mono(8.5), yahei(8.5), BRAND if abs(ratio - 2) < 0.01 else mix(BRAND, DIM, 0.6), 0.7)

        cx = PAD + 230
        cw = 470
        sh.rect((cx - 12, top + 2, cx + cw + 12, top + 84), fill=(30, 26, 24), r=7)
        guide = cx + COL * lat_adv
        for gy in range(int(top + 8), int(top + 80), 6):
            sh.line(guide, gy, guide, gy + 3, (104, 66, 46), 1)

        drifts = []
        y = top + 22
        for code, comment in CODE:
            x = cx + draw_mono(sh, cx, y, code, r["path"], code_size, INK, 0,
                               None if r["cjk"] == "self" else cjk_src)
            pad_cols = max(1, COL - cols_of(code))
            x += pad_cols * lat_adv
            drifts.append(x - guide)
            draw_mono(sh, x, y, "// " + comment, r["path"], code_size, blend(DIM, 0.12), 0,
                      None if r["cjk"] == "self" else cjk_src)
            y += 20

        rx = cx + cw + 30
        worst = min(drifts)
        sh.text(rx, top + 34, f"{worst:+.1f} px", mono(11),
                (255, 138, 74) if worst < -2 else (150, 200, 120))
        sh.mixed(rx, top + 50, "最偏一行 · COL 46", mono(8), yahei(8), DIM, 0.6)

        sh.y = top + row_h
        sh.hline(PAD, sh.y, CW, (56, 50, 46), 1)

    sh.mixed(PAD, sh.y + 26, "设备条 / 标签：中文落在 9px 等宽里是什么样", mono(9), yahei(9), BRAND, 1.8)
    ly = sh.y + 40
    for r in MONO_ROWS:
        cjk_src = r["path"] if r["cjk"] == "self" else os.path.join(WIN_FONTS, "msyh.ttc")
        draw_mono(sh, PAD, ly + 12, "ZONE 橙 · 余烬红 · 警戒黄 · 钴蓝 · SHEET R7", r["path"], 9, INK, 1.1,
                  None if r["cjk"] == "self" else cjk_src)
        sh.text(PAD + 700, ly + 12, r["name"], mono(8), blend(DIM, 0.3), "ls", 0.8)
        ly += 26

    sh.mixed(PAD, ly + 30, "结论：代码注释里成串汉字才需要中文等宽；设备条只有一两个汉字，差 0.3 列肉眼看不出。",
             bahn(11), yahei(11), DIM)
    sh.mixed(PAD, ly + 48, "换的时候整条栈一起换——Cascadia 0.586em、Sarasa / Noto 0.500em、Maple 0.600em，只把中文接在 Cascadia 后面仍是 1.71 列。",
             bahn(11), yahei(11), mix(DIM, DEEP, 0.2))

    sh.save("zone-mono-specimen.png")


if __name__ == "__main__":
    overview()
    context()
    detail()
    mono_spec()
