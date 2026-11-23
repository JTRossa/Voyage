"""Build Voyage data files from content/u*.txt.

Format:
  #unit N | Title | Era
  @voyage routeId | Voyage title | Subtitle
  ? Category | Question text
  T Display name|alias|alias; T Display name; ...   (T = tier 1-4, lines may wrap)
"""
import json, os, re, sys, unicodedata, glob

ROOT = os.path.dirname(os.path.abspath(__file__))

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d")
    s = re.sub(r"[’'`]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)

def parse(path):
    unit, cur, q = None, None, None
    buf = []
    def flush():
        nonlocal buf
        if q is not None and buf:
            for item in " ".join(buf).split(";"):
                item = item.strip()
                if not item: continue
                m = re.match(r"([1-4])\s+(.+)$", item)
                if not m: sys.exit(f"{path}: bad item {item!r}")
                parts = [p.strip() for p in m.group(2).split("|") if p.strip()]
                q["a"].append([int(m.group(1))] + parts)
        buf = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip(): continue
        if line.startswith("#unit"):
            n, title, era = [x.strip() for x in line[5:].split("|")]
            unit = {"unit": int(n), "title": title, "era": era, "voyages": []}
        elif line.startswith("@voyage"):
            flush(); q = None
            rid, title, sub = [x.strip() for x in line[7:].split("|")]
            cur = {"route": rid, "title": title, "sub": sub, "qs": []}
            unit["voyages"].append(cur)
        elif line.startswith("?"):
            flush()
            cat, text = [x.strip() for x in line[1:].split("|", 1)]
            q = {"cat": cat, "q": text, "a": []}
            cur["qs"].append(q)
        else:
            buf.append(line.strip())
    flush()
    return unit

problems = 0
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
total_v = total_q = 0
for path in sorted(glob.glob(os.path.join(ROOT, "content", "u*.txt"))):
    u = parse(path)
    for v in u["voyages"]:
        if not os.path.exists(os.path.join(ROOT, "maps", v["route"] + ".json")):
            print("MISSING MAP", v["route"]); problems += 1
        if len(v["qs"]) != 5:
            print("NOT 5 QUESTIONS", v["title"], len(v["qs"])); problems += 1
        for q in v["qs"]:
            seen = {}
            for a in q["a"]:
                forms = {norm(x) for x in a[1:]}
                for f in forms:
                    if f in seen and seen[f] != a[1]:
                        print(f"DUP in '{q['q'][:40]}': {f!r} -> {seen[f]} / {a[1]}"); problems += 1
                    seen[f] = a[1]
            if len(q["a"]) < 12:
                print(f"SHORT LIST ({len(q['a'])}) u{u['unit']} {v['route']}: {q['q'][:60]}")
            total_q += 1
        total_v += 1
    json.dump(u, open(os.path.join(ROOT, "data", f"u{u['unit']}.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"unit {u['unit']}: {len(u['voyages'])} voyages")
print(f"TOTAL {total_v} voyages, {total_q} questions, {problems} problems")
