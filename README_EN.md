# Embodied-AI Competition Knowledge Graph · Delivery Package

[简体中文](README.md) | English

This package is the **standard deliverable** of the *Embodied-AI Competition Knowledge Graph*, designed for deployment on other machines and direct consumption by AI agents. **Zero services, zero dependencies**: no database or API to set up — copy it to the target machine, unpack, and the agent can perform all queries using only the Python standard library.

> Note: The knowledge-base corpus (14 Markdown files) and the node labels in `graph.json` are in Chinese. This English README and `GRAPH_REPORT_EN.md` provide the English documentation layer. The corpus itself is not translated in this release.

## 1. Package Contents

```
embodied-kg-delivery/
├── README.md              # Chinese documentation (entry point)
├── README_EN.md           # This file, English documentation
├── graph.json             # The graph itself (core deliverable)
├── knowledge-base/        # Raw corpus (source text of graph nodes)
│   ├── 00-总纲/           # General principles
│   ├── 01-赛事目标/       # Competition objectives
│   ├── 02-教材精华/       # Textbook digests
│   ├── 03-MECE能力体系/   # MECE competency framework
│   └── 04-赛事知识映射/   # Competition-to-knowledge mapping
├── GRAPH_REPORT.md        # Graph report (Chinese)
├── GRAPH_REPORT_EN.md     # Graph report (English)
├── query.py               # Query script (standard library only)
└── LICENSE                # MIT License
```

## 2. Graph Data Format (graph.json)

Standard graph JSON with the following keys:

| Key | Description |
|---|---|
| `nodes` | Node list; each has `id / label / community / community_name / node_kind / source_file / source_location` |
| `links` | Edge list; each has `source / target / relation / confidence / weight` |
| `hyperedges` | Hyperedge list (currently empty) |
| `graph` | Metadata (`schema_version`, `graphify_version`) |

**Current scale**: 189 nodes (14 pages + 175 headings), 175 edges, 14 communities, 0 hyperedges.

### Node Fields

- `id`: Unique node id, formatted as `directory_filename` or `directory_filename_heading` (underscore-joined); this is the value returned by the `search` command.
- `label` / `norm_label`: Display label / normalized label.
- `community` / `community_name`: Community id and name the node belongs to.
- `node_kind`: `page` (file-level) or `heading` (heading-level).
- `source_file` / `source_location`: **Provenance** — points to the original Markdown file under `knowledge-base/` and the heading line number (e.g. `L41`), so the agent can trace back to the source text.

### Edge Fields

- `source` / `target`: Source / target node id.
- `relation`: Relation type. **Currently all `contains`** (document-structure relation meaning parent contains child; extraction was AST-structure based, semantic relations were not included in the final graph).
- `confidence` / `confidence_score`: Extraction confidence.
- `weight`: Edge weight.

## 3. Deployment

1. Copy the whole `embodied-kg-delivery/` directory to the target machine (any location; the script locates data by relative path).
2. The target machine only needs **Python 3.8+** (`query.py` uses the standard library only — no pip install required).
3. The agent consumes the graph via `query.py` or by `json.load`-ing `graph.json` directly.

## 4. query.py Usage

Run from the package directory:

```bash
python query.py stats                  # Graph statistics overview
python query.py search <keyword>       # Search nodes by keyword (label/id/community name)
python query.py node <node_id>         # Node details + all neighbors
python query.py neighbors <node_id>    # Neighbor relations only
python query.py community <community_id>  # All members of a community
python query.py source <node_id>       # Trace back to the original text section
```

**Typical agent workflow**: `search` to locate a node → `node` to inspect its relations → `source` to retrieve the original passage as context for the LLM.

## 5. Notes for Agents

1. **The graph is a structured index; the text lives in the corpus**: Nodes in `graph.json` do not store text. Use a node's `source_file + source_location` to trace back to the original Markdown — do not assume nodes carry content.
2. **Read `GRAPH_REPORT_EN.md` first**: It gives community structure, God Nodes (high-degree hubs) and suggested questions — a good entry point for understanding the graph.
3. **Edge relations today**: All edges are `contains` structure relations, not semantic ones. Interpret paths as "containing/belonging to", not semantic similarity.
4. **Static snapshot**: The graph was built on 2026-11-17 (graphify 0.9.111). If the corpus is updated later, rebuild `graph.json` and re-deliver.

## 6. Rebuilding (Optional)

If the corpus changes, rebuild in the source project with graphify (requires Python + graphify) to produce `graph.json` / `graph.html`. Replace the `graph.json` in this package; no other files need to change.

## License

MIT — see [LICENSE](LICENSE). The underlying textbook digests are study notes for educational use; please respect the copyright of the original textbooks and competition materials.
