#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-shot pipeline: sync corpus -> rebuild graph -> regenerate EN graph ->
validate -> git commit -> push to GitHub.

Designed to be called by the daily material-collection automation.

Prerequisites
-------------
* Python with graphify installed lives at GRAPHIFY_PY (default below).
  Override with env GRAPHIFY_PY if your environment differs.
* The credential file containing the GitHub token is passed via env
  KG_CRED_FILE. THIS SCRIPT NEVER CONTAINS A TOKEN OR A CREDENTIAL PATH BY
  DEFAULT -- both are supplied at call time, so it is safe to commit openly.
  The token string is read into memory and only used in an in-process HTTP
  Basic-auth header; it is never written to .git/config, logs or disk.

Usage
-----
    # local prep (no push)
    python scripts/sync_and_publish.py --no-push

    # full run with push (automation)
    KG_CRED_FILE=/path/to/creds.txt python scripts/sync_and_publish.py --push

What it does
------------
1. Copy source corpus (../knowledge-base) into this delivery package's
   knowledge-base/, excluding CORPUS_INDEX_EN.md (generated doc).
2. Run graphify rebuild (_rebuild.py) with GRAPHIFY_PY to refresh graph.json
   in ../graphify-out, then copy graph.json into this package.
3. Regenerate graph.en.json via translate_graph.py.
4. Run validate.py; abort if it fails.
5. git add -A, commit with a dated message (skip if nothing changed).
6. If --push: push origin main using Basic auth built in memory from the
   token read out of KG_CRED_FILE (pattern: ghp_/github_pat_ prefixed).
"""

import argparse
import base64
import os
import re
import shutil
import subprocess
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)                       # 具身智能赛事知识图谱/
SRC_KB = os.path.join(ROOT, "knowledge-base")
DST_KB = os.path.join(BASE, "knowledge-base")
REBUILD = os.path.join(ROOT, "graphify-out", "_rebuild.py")
OUT_GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
PKG_GRAPH = os.path.join(BASE, "graph.json")

DEFAULT_GRAPHIFY_PY = r"C:\CarLab\runtime\Python311\python.exe"
PYTHON = os.environ.get("GRAPHIFY_PY", DEFAULT_GRAPHIFY_PY)
PY = sys.executable  # this script's interpreter for our own python helpers

TOKEN_RE = re.compile(r"\b(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")


def run(cmd, cwd=None, capture=False):
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=capture)
    if capture:
        if r.stdout:
            print(r.stdout.rstrip())
    if r.returncode != 0:
        if capture and r.stderr:
            print(r.stderr.rstrip(), file=sys.stderr)
        raise SystemExit(f"FAILED ({r.returncode}): {' '.join(cmd)}")
    return r


def sync_corpus():
    print("== 1. sync corpus ==")
    if not os.path.isdir(SRC_KB):
        raise SystemExit(f"source corpus not found: {SRC_KB}")
    n = 0
    for name in os.listdir(SRC_KB):
        src = os.path.join(SRC_KB, name)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(DST_KB, name)
        os.makedirs(dst, exist_ok=True)
        for fn in os.listdir(src):
            if fn.endswith(".md"):
                s = os.path.join(src, fn)
                d = os.path.join(dst, fn)
                if not os.path.exists(d) or os.path.getmtime(s) > os.path.getmtime(d):
                    shutil.copy2(s, d)
                    n += 1
    print(f"  synced {n} updated md files")


def rebuild_graph():
    print("== 2. rebuild graph with graphify ==")
    if not os.path.exists(PYTHON):
        raise SystemExit(f"graphify python not found: {PYTHON} (set GRAPHIFY_PY)")
    run([PYTHON, REBUILD], cwd=ROOT)
    if not os.path.exists(OUT_GRAPH):
        raise SystemExit(f"rebuilt graph not found: {OUT_GRAPH}")
    shutil.copy2(OUT_GRAPH, PKG_GRAPH)
    print("  copied graph.json into delivery package")


def regenerate_en():
    print("== 3. regenerate graph.en.json ==")
    run([PY, os.path.join(BASE, "scripts", "translate_graph.py")], cwd=BASE)


def validate():
    print("== 4. validate ==")
    run([PY, os.path.join(BASE, "scripts", "validate.py")], cwd=BASE)


def commit():
    print("== 5. git commit ==")
    run(["git", "add", "-A"], cwd=BASE)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=BASE)
    if r.returncode == 0:
        print("  nothing to commit")
        return False
    msg = f"chore: daily KG sync {date.today().isoformat()}"
    run(["git", "commit", "-m", msg], cwd=BASE)
    print("  committed")
    return True


def push(cred_file):
    print("== 6. push with in-memory Basic auth ==")
    if not cred_file or not os.path.exists(cred_file):
        raise SystemExit("--push requires KG_CRED_FILE pointing to a file with the GitHub token")
    with open(cred_file, "r", encoding="utf-8", errors="ignore") as f:
        match = TOKEN_RE.search(f.read())
    if not match:
        raise SystemExit("no GitHub token found in credential file")
    token = match.group(0)
    # Build Basic auth header in memory; never persist token anywhere.
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    remote = "https://github.com/danfouer/embodied-kg-delivery.git"
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    cmd = ["git", "-c", f"http.extraheader=AUTHORIZATION: basic {basic}",
           "push", remote, "main"]
    # Suppress command echo of the token-bearing arg by not printing cmd here.
    r = subprocess.run(cmd, cwd=BASE, env=env, capture_output=True, text=True)
    safe_out = re.sub(r"ghp_[A-Za-z0-9]{30,}", "***", r.stdout)
    safe_out = re.sub(r"github_pat_[A-Za-z0-9_]{30,}", "***", safe_out)
    safe_err = re.sub(r"ghp_[A-Za-z0-9]{30,}", "***", r.stderr)
    safe_err = re.sub(r"github_pat_[A-Za-z0-9_]{30,}", "***", safe_err)
    if safe_out:
        print(safe_out.rstrip())
    if r.returncode != 0:
        print(safe_err.rstrip(), file=sys.stderr)
        raise SystemExit("push failed")
    print("  pushed to origin/main")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="push to GitHub after commit")
    ap.add_argument("--no-push", action="store_true", help="local prep only (default)")
    args = ap.parse_args()
    print(f"BASE={BASE}")
    sync_corpus()
    rebuild_graph()
    regenerate_en()
    validate()
    changed = commit()
    if args.push and changed:
        push(os.environ.get("KG_CRED_FILE", ""))
    elif args.push and not changed:
        print("== 6. push skipped (no changes) ==")
    print("DONE")


if __name__ == "__main__":
    main()
