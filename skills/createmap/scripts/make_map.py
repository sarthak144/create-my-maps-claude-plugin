#!/usr/bin/env python3
"""Turn a map spec (JSON) into a createmymaps.com link that opens the finished map.

Usage:
    python3 make_map.py spec.json              # prints the link + a match report
    python3 make_map.py spec.json --csv out.csv  # also writes a file for Import -> Import Excel/CSV

Standard library only. The spec format is documented in references/spec.md.
"""
import argparse, base64, csv, difflib, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "references")
BASE_URL = "https://createmymaps.com/app?utm_source={via}&utm_medium=plugin&utm_campaign=createmap"
MODES = {"flat": "flat", "color": "flat", "tag": "tag", "category": "tag",
         "number": "number", "gradient": "number", "logic": "logic", "rules": "logic"}
THEMES = {"default", "midnight", "parchment", "neon", "arctic", "dusk", "moss", "sandstone",
          "coral", "slate", "sunrise", "ocean", "forest", "rose", "lavender", "blueprint"}
OPS = {">", ">=", "<", "<=", "=="}
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
MAX_URL = 60000  # well under browser limits; above this, fall back to the CSV import


def die(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(the|of|state|province|region|district|county|republic)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def load_catalog():
    with open(os.path.join(REF, "catalog.csv"), newline="", encoding="utf-8") as f:
        return {r["map_id"]: r for r in csv.DictReader(f)}


def load_regions(map_id):
    p = os.path.join(REF, "regions", map_id + ".csv")
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Matcher:
    def __init__(self, regions):
        self.by_id = {r["id"]: r for r in regions}
        self.by_id_ci = {r["id"].lower(): r for r in regions}
        self.by_name = {}
        self.by_norm = {}
        for r in regions:
            self.by_name.setdefault(r["name"].lower(), r)
            self.by_norm.setdefault(norm(r["name"]), r)
        self.norm_keys = list(self.by_norm)

    def find(self, key):
        """Return (region, how) where how is exact|fuzzy, or (None, None)."""
        k = str(key).strip()
        r = self.by_id.get(k) or self.by_id_ci.get(k.lower()) or self.by_name.get(k.lower()) \
            or self.by_norm.get(norm(k))
        if r:
            return r, "exact"
        close = difflib.get_close_matches(norm(k), self.norm_keys, n=1, cutoff=0.85)
        if close:
            return self.by_norm[close[0]], "fuzzy"
        return None, None


def color(c, where):
    if not isinstance(c, str) or not HEX.match(c):
        die(f"{where}: color must be 6-digit hex like #2563EB, got {c!r}")
    return c.upper()


def number(v, where):
    if isinstance(v, bool):
        die(f"{where}: expected a number, got {v!r}")
    if isinstance(v, (int, float)):
        return v
    try:
        return float(str(v).replace(",", "").replace("%", "").strip())
    except ValueError:
        die(f"{where}: expected a plain number, got {v!r}")


def build(spec, via="claude"):
    catalog = load_catalog()
    map_id = spec.get("map")
    if map_id not in catalog:
        hint = difflib.get_close_matches(str(map_id), list(catalog), n=5)
        die(f"unknown map {map_id!r}. Run find_map.py. Close: {', '.join(hint) or 'none'}")
    info = catalog[map_id]
    regions = load_regions(map_id)
    m = Matcher(regions)
    mode = MODES.get(str(spec.get("mode", "flat")).lower())
    if not mode:
        die("mode must be one of flat, tag, number, logic")

    w, h = float(info["width"]), float(info["height"])
    ox, oy = float(info["origin_x"]), float(info["origin_y"])
    mn = min(w, h)

    es = {"mode": mode, "tags": [], "gradStops": [], "logicRules": []}
    theme = spec.get("theme", "default")
    if theme not in THEMES:
        die(f"theme must be one of {', '.join(sorted(THEMES))}")
    es["themeId"] = theme
    if spec.get("title"):
        es["mapTitle"] = str(spec["title"])
    es["legendTitle"] = str(spec.get("legend_title") or ("" if mode == "flat" else "Legend"))
    es["legendVisible"] = bool(spec.get("legend", mode != "flat"))
    es["lblMode"] = spec.get("labels", "none")
    if es["lblMode"] not in ("none", "abbr", "full"):
        die("labels must be none, abbr or full")
    if spec.get("label_display"):
        if spec["label_display"] not in ("label", "value", "both"):
            die("label_display must be label, value or both")
        es["lblDisplayMode"] = spec["label_display"]
    if spec.get("default_color"):
        es["defColor"] = color(spec["default_color"], "default_color")

    tag_lookup = {}
    if mode == "tag":
        cats = spec.get("categories") or die("tag mode needs a 'categories' list")
        for i, c in enumerate(cats):
            name = str(c.get("name") or die(f"categories[{i}] needs a name"))
            tid = str(c.get("id") or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or f"cat{i+1}")
            es["tags"].append({"id": tid, "name": name, "color": color(c.get("color"), f"categories[{i}]")})
            tag_lookup[tid.lower()] = tid
            tag_lookup[name.lower()] = tid
    if mode == "logic":
        rules = spec.get("rules") or die("logic mode needs a 'rules' list")
        for i, r in enumerate(rules):
            op = r.get("op")
            if op not in OPS:
                die(f"rules[{i}].op must be one of {' '.join(sorted(OPS))}")
            es["logicRules"].append({"op": op, "val": number(r.get("value"), f"rules[{i}].value"),
                                     "color": color(r.get("color"), f"rules[{i}]"), "label": str(r.get("label", ""))})

    # ── Region data ──
    state, report = {}, {"fuzzy": [], "unmatched": [], "duplicates": []}
    raw = spec.get("regions") or {}
    items = raw.items() if isinstance(raw, dict) else [(r.get("region"), r) for r in raw]
    for key, val in items:
        r, how = m.find(key)
        if not r:
            report["unmatched"].append(str(key))
            continue
        if how == "fuzzy":
            report["fuzzy"].append(f"{key} -> {r['name']} ({r['id']})")
        if r["id"] in state:
            report["duplicates"].append(f"{key} -> {r['id']}")
        if not isinstance(val, dict):
            val = {"value": val}
        entry = {}
        v = val.get("value", val.get("color", val.get("tag", val.get("category"))))
        where = f"regions[{key!r}]"
        if val.get("hidden"):
            entry["hidden"] = True
        if v is not None and v != "":
            if mode == "flat":
                entry["color"] = color(v, where)
            elif mode == "tag":
                tid = tag_lookup.get(str(v).lower())
                if not tid:
                    die(f"{where}: category {v!r} is not in 'categories'")
                entry["tag"] = tid
            else:
                entry["value"] = number(v, where)
        if entry:
            state[r["id"]] = entry

    if mode == "number":
        vals = [e["value"] for e in state.values() if "value" in e]
        g = spec.get("gradient") or {}
        stops = g.get("stops") or [{"position": 0, "color": "#DBEAFE"}, {"position": 100, "color": "#1D4ED8"}]
        if isinstance(stops[0], str):  # ["#fff", "#000"] shorthand → evenly spaced
            stops = [{"position": round(100 * i / (len(stops) - 1)), "color": c} for i, c in enumerate(stops)]
        es["gradStops"] = [{"position": number(s["position"], "gradient.stops"), "color": color(s["color"], "gradient.stops")} for s in stops]
        es["gradValueMode"] = "value"
        es["gradMinOverride"] = number(g["min"], "gradient.min") if g.get("min") is not None else (min(vals) if vals else 0)
        es["gradMaxOverride"] = number(g["max"], "gradient.max") if g.get("max") is not None else (max(vals) if vals else 100)
        es["gradReversed"] = False

    # ── Annotations & pins (positions/sizes are in map units, not pixels) ──
    anns, pins = [], []
    place = {"top": (ox + w / 2, oy + h * 0.06), "bottom": (ox + w * 0.02, oy + h * 0.96)}
    for i, a in enumerate(spec.get("annotations") or []):
        pos = a.get("position", "top")
        x, y = (a["x"], a["y"]) if "x" in a and "y" in a else place.get(pos, place["top"])
        default_size = 0.05 if pos == "top" else 0.022
        anns.append({"id": f"a{i+1}", "text": str(a.get("text", "")), "svgX": round(float(x), 1), "svgY": round(float(y), 1),
                     "fontSize": round(min(float(a.get("size", mn * default_size)), mn * 0.09), 1),
                     "color": color(a.get("color", "#1A2035" if theme in ("default", "arctic", "moss", "coral", "slate", "sunrise", "rose", "lavender", "parchment") else "#F1F5F9"), f"annotations[{i}]"),
                     "bold": bool(a.get("bold", pos == "top")), "italic": bool(a.get("italic", False)),
                     "underline": False, "strikethrough": False})
    for i, p in enumerate(spec.get("pins") or []):
        if "region" in p:
            r, _ = m.find(p["region"])
            if not r or not r["center_x"]:
                report["unmatched"].append(f"pin region {p['region']}")
                continue
            x, y = float(r["center_x"]), float(r["center_y"])
        else:
            x, y = float(p["x"]), float(p["y"])
        pins.append({"id": f"pin{i+1}", "label": str(p.get("label", f"Pin {i+1}")), "svgX": round(x, 1), "svgY": round(y, 1),
                     "color": color(p.get("color", "#E11D48"), f"pins[{i}]"), "type": p.get("shape", "teardrop"),
                     "size": round(min(float(p.get("size", mn * 0.06)), mn * 0.10), 1)})
    if anns:
        es["annotations"] = anns
    if pins:
        es["pins"] = pins

    payload = {"v": 1, "n": str(spec.get("name") or spec.get("title") or info["label"]), "m": map_id, "s": state, "e": es}
    enc = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode()).decode().rstrip("=")
    report["filled"] = len(state)
    report["total"] = len(regions)
    report["empty"] = [r["name"] for r in regions if r["id"] not in state]
    return BASE_URL.format(via=via) + "#s=" + enc, payload, report, regions


def write_csv(path, payload, regions):
    """Flat CSV in the format the app's Import (Excel/CSV) reads."""
    es, mode = payload["e"], payload["e"]["mode"]
    q = lambda v: '"' + str(v).replace('"', '""') + '"' if re.search(r'[",\n]', str(v)) else str(v)
    out = [f"# Project: {payload['n']}", f"# Map: {payload['m']}", f"# Mode: {mode}", f"# Theme: {es['themeId']}"]
    if es.get("mapTitle"): out.append(f"# Map Title: {es['mapTitle']}")
    if es.get("legendTitle"): out.append(f"# Legend Title: {es['legendTitle']}")
    out.append(f"# Label Mode: {es['lblMode']}")
    out.append(f"# Legend Visible: {1 if es['legendVisible'] else 0}")
    if mode == "number":
        out += [f"# Gradient Stops: {json.dumps(es['gradStops'])}", "# Gradient Value Mode: value",
                f"# Gradient Min: {es['gradMinOverride']}", f"# Gradient Max: {es['gradMaxOverride']}"]
    if mode == "tag":
        out += ["# TAGS", "tag_id,tag_name,tag_color"] + [",".join(map(q, (t["id"], t["name"], t["color"]))) for t in es["tags"]]
    if mode == "logic":
        out += ["# LOGIC_RULES", "operator,value,color,label"] + [",".join(map(q, (r["op"], r["val"], r["color"], r["label"]))) for r in es["logicRules"]]
    if es.get("annotations") or es.get("pins"):
        out += ["# ANNOTATIONS", "id,type,label,svgX,svgY,fontSize,color,bold,italic,underline,strikethrough,fontStack,pinShape,pinSize"]
        for a in es.get("annotations", []):
            out.append(",".join(map(q, (a["id"], "text", a["text"], a["svgX"], a["svgY"], a["fontSize"], a["color"], int(a["bold"]), int(a["italic"]), 0, 0, "", "", ""))))
        for p in es.get("pins", []):
            out.append(",".join(map(q, (p["id"], "pin", p["label"], p["svgX"], p["svgY"], "", p["color"], "", "", "", "", "", p["type"], p["size"]))))
    col = {"flat": "color", "tag": "tag", "number": "value", "logic": "value"}[mode]
    out += ["# REGION_DATA", f"id,name,{col},visible"]
    for r in regions:
        e = payload["s"].get(r["id"], {})
        out.append(",".join(map(q, (r["id"], r["name"], e.get(col, ""), 0 if e.get("hidden") else 1))))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(out) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="path to spec JSON, or - for stdin")
    ap.add_argument("--csv", help="also write an importable CSV here")
    ap.add_argument("--via", default="claude", help="assistant building the map, for link attribution (claude, chatgpt, ...)")
    a = ap.parse_args()
    spec = json.load(sys.stdin if a.spec == "-" else open(a.spec, encoding="utf-8"))
    url, payload, rep, regions = build(spec, re.sub(r"[^a-z0-9-]", "", a.via.lower()) or "claude")

    if len(url) <= MAX_URL:
        print("LINK:", url)
    else:
        print(f"LINK: (too long for a link — {len(url)} chars; deliver the CSV instead)")
        if not a.csv:
            a.csv = re.sub(r"[^a-z0-9]+", "-", payload["n"].lower()).strip("-") + ".csv"
    if a.csv:
        write_csv(a.csv, payload, regions)
        print("CSV:", a.csv)
    print(f"\nFilled {rep['filled']} of {rep['total']} regions.")
    if rep["fuzzy"]:
        print("Fuzzy-matched (check these):\n  " + "\n  ".join(rep["fuzzy"]))
    if rep["unmatched"]:
        print("NOT matched (dropped):\n  " + "\n  ".join(rep["unmatched"]))
    if rep["duplicates"]:
        print("Duplicates (last one wins):\n  " + "\n  ".join(rep["duplicates"]))
    if rep["empty"] and payload["e"]["mode"] in ("number", "logic"):
        print(f"WARNING: in {payload['e']['mode']} mode the app colors regions with no data as if their value were 0. "
              "Fill them, hide them, or switch to tag mode with a 'No data' category.")
    if rep["empty"] and len(rep["empty"]) <= 40:
        print("No data:\n  " + ", ".join(rep["empty"]))
    elif rep["empty"]:
        print(f"No data: {len(rep['empty'])} regions (e.g. {', '.join(rep['empty'][:10])}, ...)")


if __name__ == "__main__":
    main()
