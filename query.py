#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
具身智能赛事知识图谱 —— 交付包查询脚本

供 AI agent 在本机直接调用，无需安装任何第三方依赖（仅标准库）。

用法示例：
    python query.py stats                          # 图谱统计概览
    python query.py search 蚂蚁灵波                # 关键词搜索节点
    python query.py node <node_id>                 # 查看节点详情与邻居
    python query.py community 0                    # 查看某社区的全部成员
    python query.py source <node_id>               # 回溯节点对应的原文内容
    python query.py neighbors <node_id>            # 仅查看邻居关系

语言切换（英文图谱）：
    python query.py --en stats                     # 英文图谱统计
    python query.py --en search embodied           # 在英文图谱中搜索
    python query.py --en node <node_id>            # node_id 与中文图谱完全一致
    也可设置环境变量 KG_LANG=en 永久切换，或使用 --graph <path> 指定任意图谱文件。

node_id 可通过 `search` 命令获得（如 01_赛事目标_蚂蚁灵波具身大模型挑战赛）。
node_id 在中英文图谱中保持一致，source 命令始终回溯到中文原文。
"""

import json
import os
import sys

# 包内相对路径（脚本与 graph.json、knowledge-base 同级目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(BASE_DIR, "graph.json")
KB_DIR = os.path.join(BASE_DIR, "knowledge-base")


def load_graph():
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_nodes(g):
    return {n["id"]: n for n in g["nodes"]}


def load_links(g):
    return g["links"]


def cmd_stats(g, nodes, links):
    print("=== 图谱统计 ===")
    print("节点总数 :", len(nodes))
    print("边总数   :", len(links))
    comm_set = sorted({n["community"] for n in nodes.values()})
    print("社区数   :", len(comm_set), "(id:", comm_set, ")")
    by_kind = {}
    for n in nodes.values():
        by_kind[n.get("node_kind", "?")] = by_kind.get(n.get("node_kind", "?"), 0) + 1
    print("节点类型 :", by_kind)
    rels = {}
    for l in links:
        rels[l.get("relation", "?")] = rels.get(l.get("relation", "?"), 0) + 1
    print("关系类型 :", rels)


def cmd_search(g, nodes, links, keyword):
    kw = keyword.lower()
    hits = []
    for nid, n in nodes.items():
        haystack = " ".join(
            [n.get("label", ""), n.get("norm_label", ""), nid, n.get("community_name", "")]
        ).lower()
        if kw in haystack:
            hits.append(nid)
    if not hits:
        print(f"未找到与「{keyword}」匹配的节点。")
        return
    print(f"=== 搜索「{keyword}」命中 {len(hits)} 个节点 ===")
    for nid in hits:
        n = nodes[nid]
        deg = sum(1 for l in links if l["source"] == nid or l["target"] == nid)
        print(f"\n[{nid}]")
        print(f"  标签     : {n.get('label')}")
        print(f"  社区     : {n.get('community')} - {n.get('community_name')}")
        print(f"  类型     : {n.get('node_kind')}")
        print(f"  来源     : {n.get('source_file')} @ {n.get('source_location')}")
        print(f"  度数     : {deg}")


def get_neighbors(nid, links):
    nb = []
    for l in links:
        if l["source"] == nid:
            nb.append(("out", l["target"], l))
        if l["target"] == nid:
            nb.append(("in", l["source"], l))
    return nb


def cmd_node(g, nodes, links, nid):
    n = nodes.get(nid)
    if n is None:
        print(f"节点不存在：{nid}（可用 search 命令查找）")
        return
    print(f"=== 节点详情：{nid} ===")
    print(json.dumps(n, ensure_ascii=False, indent=2))
    nb = get_neighbors(nid, links)
    print(f"\n=== 邻居（{len(nb)} 条边）===")
    if not nb:
        print("（无邻居）")
    for direction, other, l in nb:
        arrow = "→" if direction == "out" else "←"
        print(f"  {arrow} [{l.get('relation')}] {other}")


def cmd_neighbors(g, nodes, links, nid):
    nb = get_neighbors(nid, links)
    print(f"=== {nid} 的邻居（{len(nb)} 条边）===")
    if not nb:
        print("（无邻居）")
    for direction, other, l in nb:
        arrow = "→" if direction == "out" else "←"
        o = nodes.get(other, {})
        print(f"  {arrow} [{l.get('relation')}] {other}  ({o.get('label', '?')})")


def cmd_community(g, nodes, links, cid):
    members = [n for n in nodes.values() if n.get("community") == int(cid)]
    print(f"=== 社区 {cid}：{members[0].get('community_name') if members else '?'}（{len(members)} 个节点）===")
    for n in members:
        deg = sum(1 for l in links if l["source"] == n["id"] or l["target"] == n["id"])
        print(f"  [{n['id']}] ({n.get('node_kind')}, 度数 {deg})")


def cmd_source(g, nodes, links, nid):
    n = nodes.get(nid)
    if n is None:
        print(f"节点不存在：{nid}")
        return
    src = n.get("source_file", "")
    loc = n.get("source_location", "")
    md_path = os.path.join(KB_DIR, src)
    if not os.path.exists(md_path):
        print(f"未找到语料文件：{md_path}")
        return
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    # source_location 形如 "L41"，指向标题所在行
    start = None
    if loc.startswith("L") and loc[1:].isdigit():
        start = int(loc[1:]) - 1  # 转 0 基
        start = max(0, min(start, len(lines) - 1))
    if start is None:
        print(f"节点 {nid} 无有效 source_location，输出全文。")
        print("\n".join(lines))
        return
    # 从标题行截取：到下一个同级或更高级标题为止
    heading_level = 0
    for i in range(start, len(lines)):
        s = lines[i].strip()
        if s.startswith("#"):
            heading_level = len(s) - len(s.lstrip("#"))
            break
    # 找到下一个标题（同级或更高级）
    end = len(lines)
    for i in range(start + 1, len(lines)):
        s = lines[i].strip()
        if s.startswith("#"):
            lv = len(s) - len(s.lstrip("#"))
            if lv <= heading_level:
                end = i
                break
    section = lines[start:end]
    print(f"=== 原文回溯：{src} @ {loc} ===")
    print("\n".join(section).strip())


def resolve_graph_path(argv):
    """Parse language/graph flags and return (graph_path, remaining_args)."""
    path = GRAPH_PATH
    rest = list(argv)
    # --graph <path> takes highest precedence
    if "--graph" in rest:
        i = rest.index("--graph")
        if i + 1 < len(rest):
            path = os.path.join(BASE_DIR, rest[i + 1]) if not os.path.isabs(rest[i + 1]) else rest[i + 1]
            del rest[i:i + 2]
    elif "--en" in rest:
        path = os.path.join(BASE_DIR, "graph.en.json")
        rest.remove("--en")
    elif os.environ.get("KG_LANG", "").lower() in ("en", "english"):
        path = os.path.join(BASE_DIR, "graph.en.json")
    return path, rest


def main():
    graph_path, args = resolve_graph_path(sys.argv[1:])
    if not args:
        print(__doc__)
        sys.exit(1)
    if not os.path.exists(graph_path):
        print(f"未找到图谱文件：{graph_path}")
        sys.exit(1)
    global GRAPH_PATH
    GRAPH_PATH = graph_path
    g = load_graph()
    nodes = load_nodes(g)
    links = load_links(g)

    cmd = args[0]
    if cmd == "stats":
        cmd_stats(g, nodes, links)
    elif cmd == "search" and len(args) >= 2:
        cmd_search(g, nodes, links, args[1])
    elif cmd == "node" and len(args) >= 2:
        cmd_node(g, nodes, links, args[1])
    elif cmd == "neighbors" and len(args) >= 2:
        cmd_neighbors(g, nodes, links, args[1])
    elif cmd == "community" and len(args) >= 2:
        cmd_community(g, nodes, links, args[1])
    elif cmd == "source" and len(args) >= 2:
        cmd_source(g, nodes, links, args[1])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
