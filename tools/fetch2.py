import json, os, sys, tarfile, urllib.request, urllib.parse, io

UA = {"User-Agent": "Mozilla/5.0"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "font-lab", "_src")
os.makedirs(DEST, exist_ok=True)


def fetch(name, keep=None, drop_big=None):
    url = "https://registry.npmjs.org/" + urllib.parse.quote(name, safe="@")
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
    latest = d["dist-tags"]["latest"]
    v = d["versions"][latest]
    print(f"FETCH {name}@{latest} ({v['dist'].get('unpackedSize', 0)/1048576:.1f} MB unpacked)")
    data = urllib.request.urlopen(urllib.request.Request(v["dist"]["tarball"], headers=UA), timeout=180).read()
    outdir = os.path.join(DEST, name.replace("/", "__").replace("@", ""))
    os.makedirs(outdir, exist_ok=True)
    files = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        for m in tf.getmembers():
            if not m.isfile():
                continue
            ext = os.path.splitext(m.name)[1].lower()
            if ext not in (".ttf", ".otf", ".woff2", ".woff"):
                continue
            rel = m.name.lstrip("./")
            if keep and not any(k.lower() in rel.lower() for k in keep):
                continue
            m.name = rel
            tf.extract(m, outdir, filter="data")
            files.append(rel)
    for f in sorted(files):
        p = os.path.join(outdir, f)
        print(f"   {f}  {os.path.getsize(p)/1048576:.2f} MB")
    print(f"   ({len(files)} files)")
    return outdir


if __name__ == "__main__":
    args = sys.argv[1:]
    for a in args:
        name, _, keep = a.partition("::")
        try:
            fetch(name, keep=[k for k in keep.split(",") if k] or None)
        except Exception as e:
            print("FAIL", name, type(e).__name__, e)
