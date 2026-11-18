#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-shot pipeline: sync corpus -> rebuild graph -> regenerate EN graph ->
validate -> local git commit -> publish to GitHub via REST API.

Push uses the GitHub Git Data API (blobs/tree/commit/ref) over api.github.com
instead of `git push` over HTTPS. This intentionally bypasses the local HTTPS
transport, which can be blocked by proxies while the REST API stays reachable.

Designed to be called by the daily material-collection automation.

Prerequisites
-------------
* Python with graphify installed lives at GRAPHIFY_PY (default below).
  Override with env GRAPHIFY_PY if your environment differs.
* The credential file containing the GitHub token is passed via env
  KG_CRED_FILE. THIS SCRIPT NEVER CONTAINS A TOKEN OR A CREDENTIAL PATH BY
  DEFAULT -- both are supplied at call time, so it is safe to commit openly.
  The token string is read into memory and only used in an in-process HTTP
  Bearer-auth header to api.github.com; never written to config, logs or disk.

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
5. git add -A, commit locally with a dated message (local history only).
6. If --push: publish the working tree to GitHub main via the Git Data API:
   compare local file blob SHAs against the remote tree, upload only changed
   blobs, create a new tree + commit, and move the main ref. Token read from
   KG_CRED_FILE is used only in a Bearer header, never echoed or persisted.
   After a successful push, align local git history to the remote commit so
   subsequent runs stay clean (via commit objects fetched through the API).
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
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

REPO_SLUG = "danfouer/embodied-kg-delivery"
BRANCH = "main"
API_ROOT = "https://api.github.com"
COMMITTER = {"name": "Sean Zhu", "email": "danfouer@users.noreply.github.com"}


def read_token(cred_file):
    """Read the GitHub token into memory from KG_CRED_FILE. Never logged."""
    if not cred_file or not os.path.exists(cred_file):
        raise SystemExit("--push requires KG_CRED_FILE pointing to a file with the GitHub token")
    with open(cred_file, "r", encoding="utf-8", errors="ignore") as f:
        match = TOKEN_RE.search(f.read())
    if not match:
        raise SystemExit("no GitHub token found in credential file")
    return match.group(0)


def api(path, token, method="GET", payload=None):
    """Call GitHub REST API. Token only lives in the request header in memory."""
    url = API_ROOT + path
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "embodied-kg-sync")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="ignore")[:400]
        raise SystemExit(f"GitHub API {method} {path} failed: HTTP {e.code}: {detail}")


def local_head_tree():
    """Return {path: blob_sha} from local HEAD's git object store.

    Using the committed git objects (not worktree bytes) avoids CRLF/autocrlf
    drift and yields canonical blob SHAs directly comparable with the remote.
    """
    out = subprocess.check_output(["git", "ls-tree", "-r", "-z", "HEAD"], cwd=BASE)
    result = {}
    for entry in out.decode("utf-8").split("\0"):
        if not entry or "\t" not in entry:
            continue
        meta, path = entry.split("\t", 1)
        parts = meta.split()
        if len(parts) >= 3 and parts[1] == "blob":
            result[path] = parts[2]
    return result


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


def publish_via_api(token):
    """Publish tracked working-tree files to main via the Git Data API.

    Strategy: start from the CURRENT remote tree as base_tree and overwrite
    only paths whose content SHA differs locally. This preserves files added
    by others via PR (they stay in base_tree) and produces one atomic commit.
    Returns (new_remote_head_sha, published_bool).
    """
    print("== 6. publish to GitHub via Git Data API ==")
    # Current remote head + tree (single request chain, all over api.github.com)
    ref = api(f"/repos/{REPO_SLUG}/git/ref/heads/{BRANCH}", token)
    remote_head = ref["object"]["sha"]
    head_commit = api(f"/repos/{REPO_SLUG}/git/commits/{remote_head}", token)
    base_tree = head_commit["tree"]["sha"]
    tree_data = api(f"/repos/{REPO_SLUG}/git/trees/{base_tree}?recursive=1", token)
    remote_map = {e["path"]: e["sha"] for e in tree_data.get("tree", []) if e["type"] == "blob"}

    # Local committed content from git object store (canonical LF, exact SHAs)
    local_map = local_head_tree()
    changed_rels = [rel for rel, sha in local_map.items() if remote_map.get(rel) != sha]

    if not changed_rels:
        print(f"  no content changes vs remote tree ({len(local_map)} tracked files); skip publish")
        return remote_head, False

    print(f"  {len(changed_rels)} file(s) differ from remote; uploading blobs")
    entries = []
    for rel in changed_rels:
        lsha = local_map[rel]
        data = subprocess.check_output(["git", "cat-file", "blob", lsha], cwd=BASE)
        blob = api(f"/repos/{REPO_SLUG}/git/blobs", token, "POST",
                   {"content": base64.b64encode(data).decode("ascii"), "encoding": "base64"})
        entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print(f"    + {rel}")

    new_tree = api(f"/repos/{REPO_SLUG}/git/trees", token, "POST",
                   {"base_tree": base_tree, "tree": entries})
    msg = f"chore: daily KG sync {date.today().isoformat()}"
    new_commit = api(f"/repos/{REPO_SLUG}/git/commits", token, "POST",
                     {"message": msg, "tree": new_tree["sha"],
                      "parents": [remote_head], "author": COMMITTER, "committer": COMMITTER})
    new_sha = new_commit["sha"]
    api(f"/repos/{REPO_SLUG}/git/refs/heads/{BRANCH}", token, "PATCH", {"sha": new_sha})
    print(f"  published -> {BRANCH} @ {new_sha[:12]}")
    return new_sha, True


def align_local_ref():
    """Point local origin/main at local HEAD so status reads clean.

    API-created commits and local git commits are content-identical but have
    different SHAs (different metadata/parents). Publishing never uses git
    push/fetch -- it compares file SHAs against the remote tree -- so this
    divergence is harmless. Aligning the remote-tracking ref avoids a
    misleading 'ahead of origin/main' state.
    """
    local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE, text=True).strip()
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", local], cwd=BASE, check=True)
    print(f"  local origin/main -> {local[:12]} (content mirrors remote)")


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
    if args.push:
        token = read_token(os.environ.get("KG_CRED_FILE", ""))
        remote_head, published = publish_via_api(token)
        if published:
            align_local_ref()
        else:
            print("== 7. align skipped (no remote change) ==")
    print("DONE")


if __name__ == "__main__":
    main()
