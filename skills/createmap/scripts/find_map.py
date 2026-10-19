#!/usr/bin/env python3
"""Find the right map id for a request.

Usage:
    python3 find_map.py india states       # best matches for a query
    python3 find_map.py --list "Europe"    # every map in a category
    python3 find_map.py --regions india    # the region list (id, name) for one map
"""
import csv, os, re, sys

REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references")


def rows():
    with open(os.path.join(REF, "catalog.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def show(r):
    print(f"{r['map_id']:<40} {r['regions']:>5} regions  {r['label']}  [{r['category']}]")


def main(argv):
    if not argv:
        print(__doc__)
        return
    if argv[0] == "--regions":
        with open(os.path.join(REF, "regions", argv[1] + ".csv"), newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                print(f"{r['id']}\t{r['name']}")
        return
    cat = rows()
    if argv[0] == "--list":
        q = " ".join(argv[1:]).lower()
        for r in cat:
            if q in r["category"].lower():
                show(r)
        return
    query = " ".join(argv).lower().strip()
    terms = [t for t in re.split(r"\W+", query) if t]
    scored = []
    for r in cat:
        ids = set(r["map_id"].lower().split("-"))
        label = set(re.split(r"\W+", r["label"].lower()))
        catg = set(re.split(r"\W+", r["category"].lower()))
        s = 0
        for t in terms:
            # a match on the map's own id/name beats a match on its category
            s += 4 if t in ids else 0
            s += 3 if t in label else 0
            s += 1 if t in catg else 0
            if not (t in ids or t in label or t in catg) and t in f"{r['map_id']} {r['label']}".lower():
                s += 1
        if r["label"].lower() == query or r["map_id"] == query:
            s += 5
        if s:
            # ties → the canonical (shortest id) map, then the more complete one
            scored.append((-s, len(r["map_id"]), -int(r["regions"]), r))
    for *_, r in sorted(scored, key=lambda x: x[:3])[:15]:
        show(r)
    if not scored:
        print("No match. Try a broader word, or --list <category>. Categories:")
        print("  " + ", ".join(sorted({r['category'] for r in cat})))


if __name__ == "__main__":
    main(sys.argv[1:])
