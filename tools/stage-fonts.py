import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "font-lab", "_src")
OUT = os.path.join(ROOT, "font-lab", "fonts")
os.makedirs(OUT, exist_ok=True)

USER_FONTS = os.path.join(os.environ["LOCALAPPDATA"], r"Microsoft\Windows\Fonts")

MAP = [
    (os.path.join(SRC, "fontpkg__mi-sans", "package", "MiSans-Regular.otf"), "MiSans-Regular.otf"),
    (os.path.join(SRC, "fontpkg__mi-sans", "package", "MiSans-Semibold.otf"), "MiSans-Semibold.otf"),
    (os.path.join(SRC, "fontpkg__mi-sans", "package", "MiSans-Bold.otf"), "MiSans-Bold.otf"),
    (os.path.join(SRC, "fontpkg__alibaba-pu-hui-ti-3-0", "package", "AlibabaPuHuiTi-3-55-Regular.ttf"), "PuHuiTi35-Regular.ttf"),
    (os.path.join(SRC, "fontpkg__alibaba-pu-hui-ti-3-0", "package", "AlibabaPuHuiTi-3-75-SemiBold.ttf"), "PuHuiTi35-SemiBold.ttf"),
    (os.path.join(SRC, "fontpkg__alibaba-pu-hui-ti-3-0", "package", "AlibabaPuHuiTi-3-85-Bold.ttf"), "PuHuiTi35-Bold.ttf"),
    (os.path.join(SRC, "fontpkg__smiley-sans", "package", "SmileySans-Oblique.ttf"), "SmileySans-Oblique.ttf"),
    (os.path.join(USER_FONTS, "HarmonyOS_Sans_SC_Regular.ttf"), "HarmonyOSSC-Regular.ttf"),
    (os.path.join(USER_FONTS, "HarmonyOS_Sans_SC_Medium.ttf"), "HarmonyOSSC-Medium.ttf"),
    (os.path.join(USER_FONTS, "HarmonyOS_Sans_SC_Bold.ttf"), "HarmonyOSSC-Bold.ttf"),
]

total = 0
for src, name in MAP:
    if not os.path.exists(src):
        print("MISSING", src)
        continue
    dst = os.path.join(OUT, name)
    shutil.copy2(src, dst)
    mb = os.path.getsize(dst) / 1048576
    total += mb
    print(f"{name:32} {mb:6.2f} MB")
print(f"{'TOTAL':32} {total:6.2f} MB")
