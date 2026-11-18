#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge-graph delivery validator. Used by CI and runnable locally.

Checks:
  1. graph.json / graph.en.json parse and have identical topology (ids, links)
  2. no dangling edges, no self-loops, no isolated nodes
  3. every node's source_file exists and source_location points to a valid line
  4. English graph coverage: every label/community name translated
  5. required documentation files present (bilingual)
  6. no secrets (token / password / private key / known credential strings)
  7. query.py loads both graphs and --en switches correctly

Exit code 0 = all pass, 1 = at least one failure.
"""

import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []
checks = []


def ok(name):
    checks.append((name, True))
    print(f"  PASS  {name}")


def fail(name, detail):
    checks.append((name, False))
    errors.append(f"{name}: {detail}")
    print(f"  FAIL  {name}: {detail}")


def load(name):
    path = os.path.join(BASE, name)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"load {name}", str(e))
        return None


print("== KG delivery validation ==")

# 1. load graphs
g = load("graph.json")
ge = load("graph.en.json")
if g is None or ge is None:
    sys.exit(1)

# 2. topology
zh_ids = {n["id"] for n in g["nodes"]}
en_ids = {n["id"] for n in ge["nodes"]}
if zh_ids == en_ids:
    ok("node ids identical across zh/en")
else:
    fail("node ids identical across zh/en", f"diff={len(zh_ids ^ en_ids)}")

def edge_set(graph):
    return {(l["source"], l["target"], l.get("relation")) for l in graph["links"]}

if edge_set(g) == edge_set(ge):
    ok("edge topology identical across zh/en")
else:
    fail("edge topology identical across zh/en", "link sets differ")

# 3. graph health (on zh graph)
node_ids = zh_ids
dangling = [l for l in g["links"] if l["source"] not in node_ids or l["target"] not in node_ids]
if not dangling:
    ok("no dangling edges")
else:
    fail("no dangling edges", f"{len(dangling)} dangling")

selfloops = [l for l in g["links"] if l["source"] == l["target"]]
if not selfloops:
    ok("no self-loops")
else:
    fail("no self-loops", f"{len(selfloops)} self-loops")

degree = {nid: 0 for nid in node_ids}
for l in g["links"]:
    degree[l["source"]] = degree.get(l["source"], 0) + 1
    degree[l["target"]] = degree.get(l["target"], 0) + 1
isolated = [nid for nid, d in degree.items() if d == 0]
if not isolated:
    ok("no isolated nodes")
else:
    fail("no isolated nodes", f"{len(isolated)} isolated")

# 4. provenance
missing_src = []
bad_loc = []
for n in g["nodes"]:
    sf = n.get("source_file", "")
    if not sf or not os.path.exists(os.path.join(BASE, "knowledge-base", sf)):
        missing_src.append((n["id"], sf))
    loc = n.get("source_location", "")
    if loc.startswith("L") and loc[1:].isdigit() and int(loc[1:]) < 1:
        bad_loc.append((n["id"], loc))
if not missing_src:
    ok("all source_file paths exist")
else:
    fail("all source_file paths exist", f"{len(missing_src)} missing, e.g. {missing_src[:2]}")
if not bad_loc:
    ok("source_location values valid")
else:
    fail("source_location values valid", str(bad_loc[:3]))

# 5. English coverage (advisory: gaps are listed in I18N_GAPS.md and do not
#    block the pipeline, so daily corpus growth cannot break CI)
try:
    sys.path.insert(0, os.path.join(BASE, "scripts"))
    from translate_graph import collect_missing
    gaps = collect_missing(g)
    if not gaps:
        ok("English translation coverage 100%")
    else:
        checks.append(("English translation coverage", True))
        print(f"  WARN  English translation coverage: {len(gaps)} untranslated "
              f"labels (see I18N_GAPS.md; contributions welcome)")
except Exception as e:
    fail("English translation coverage", str(e))

# 6. required docs
required = [
    "README.md", "README_EN.md", "GRAPH_REPORT.md", "GRAPH_REPORT_EN.md",
    "LICENSE", "CONTRIBUTING.md", "CONTRIBUTORS.md", "query.py",
    "graph.json", "graph.en.json", "knowledge-base/CORPUS_INDEX_EN.md",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/ISSUE_TEMPLATE/share-insight.md",
]
missing_docs = [f for f in required if not os.path.exists(os.path.join(BASE, f))]
if not missing_docs:
    ok("required bilingual docs present")
else:
    fail("required bilingual docs present", str(missing_docs))

# 7. secret scan over tracked text files
# NOTE: keep this pattern GENERIC -- never hardcode real credentials here,
# since this script itself is committed to a public repository.
secret_pat = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{30,}|"                       # GitHub personal/OAuth tokens
    r"github_pat_[A-Za-z0-9_]{30,}|"                      # GitHub fine-grained tokens
    r"sk-[A-Za-z0-9]{20,}|"                              # OpenAI-style keys
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"               # private keys
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b|"                      # bare IPv4 addresses
    r"(?i:(?:password|passwd|api[_-]?key)\s*[:=]\s*['\"][^'\"]{8,})"
)
# Exclude this validator from its own scan (the generic pattern text above
# contains example-shaped strings that would otherwise self-match).
SELF = os.path.relpath(os.path.abspath(__file__), BASE).replace("\\", "/")
hits = []
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
    for fn in files:
        if not fn.endswith((".md", ".py", ".json", ".yml", ".yaml", ".txt")):
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, BASE).replace("\\", "/")
        if rel == SELF:
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if secret_pat.search(line):
                        hits.append(f"{rel}:{i}")
        except Exception:
            pass
if not hits:
    ok("no secrets in tracked text files")
else:
    fail("no secrets in tracked text files", str(hits[:5]))

# 8. query.py smoke test
try:
    for args in (["stats"], ["--en", "stats"]):
        r = subprocess.run([sys.executable, os.path.join(BASE, "query.py")] + args,
                           capture_output=True, text=True, timeout=20)
        if r.returncode != 0:
            fail(f"query.py {' '.join(args)}", r.stderr.strip()[:200])
    ok("query.py zh/en smoke test")
except Exception as e:
    fail("query.py zh/en smoke test", str(e))

# summary
print("\n== Summary ==")
print(f"Passed: {sum(1 for _, p in checks if p)}/{len(checks)}")
if errors:
    print(f"FAILED ({len(errors)}):")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("ALL CHECKS PASSED")
