# 具身智能赛事知识图谱

简体中文 | [English](README_EN.md)

本包是《具身智能赛事知识图谱》的**标准交付形态**，面向在其他机器上部署、供 AI agent 直接消费的场景。**零服务、零依赖**：无需部署数据库或 API，拷贝到目标机器解压即用，agent 用 Python 标准库即可完成全部查询。

## 一、包内容

```
embodied-kg-delivery/
├── README.md              # 本说明
├── graph.json             # 图谱本体（核心交付物）
├── knowledge-base/        # 原始语料（图谱节点的正文来源）
│   ├── 00-总纲/
│   ├── 01-赛事目标/
│   ├── 02-教材精华/
│   ├── 03-MECE能力体系/
│   └── 04-赛事知识映射/
├── graph.en.json          # 英文图谱（节点标签/社区名英文化，id 与中文一致）
├── GRAPH_REPORT.md        # 图谱说明书（统计、社区结构、God Nodes）
├── GRAPH_REPORT_EN.md     # 图谱说明书（英文）
├── CORPUS_INDEX_EN.md     # 语料英文索引（见 knowledge-base/）
├── CONTRIBUTING.md        # 贡献指南（中英双语，欢迎开分支提认知）
├── CONTRIBUTORS.md        # 贡献者名单
├── I18N_GAPS.md           # 待译标签清单（欢迎认领）
├── query.py               # 查询脚本（agent 可直接调用，仅用标准库）
├── scripts/               # 英文化、校验、每日同步发布脚本
│   ├── translate_graph.py
│   ├── validate.py
│   └── sync_and_publish.py
└── .github/workflows/validate.yml  # CI：图谱完整性/溯源/译文/敏感信息校验
```

> **语料英文索引**见 `knowledge-base/CORPUS_INDEX_EN.md`。语料正文保持中文以确保术语准确。

## 一·补 双语查询与参与贡献

```bash
python query.py stats              # 中文图谱
python query.py --en stats         # 英文图谱（或用环境变量 KG_LANG=en）
python query.py --en search robot  # 英文标签搜索，node_id 与中文一致
```

想贡献一条认知、一处译文或素材？见 [CONTRIBUTING.md](CONTRIBUTING.md)：Fork → 开分支 → 改语料/译文 →（若改标签则运行 `python scripts/translate_graph.py`）→ 提 PR。CI 会自动校验图谱结构、溯源、译文覆盖与敏感信息。欢迎所有人都来开自己的分支，让这份图谱持续生长。

## 二、图谱数据格式（graph.json）

标准图 JSON，结构如下：

| 键 | 说明 |
|---|---|
| `nodes` | 节点列表，每项含 `id / label / community / community_name / node_kind / source_file / source_location` 等字段 |
| `links` | 边列表，每项含 `source / target / relation / confidence / weight` 等字段 |
| `hyperedges` | 超边列表（当前为空） |
| `graph` | 元信息（`schema_version`、`graphify_version`） |

**当前规模**：259 节点（19 个 page + 240 个 heading）、240 条边（随每日素材收集持续增长）。英文图谱 `graph.en.json` 与中文图谱 id/拓扑完全一致。

### 节点字段

- `id`：节点唯一标识，格式为 `目录_文件名` 或 `目录_文件名_标题`（下划线连接），`search` 命令返回的即为该值。
- `label` / `norm_label`：节点显示标签 / 归一化标签。
- `community` / `community_name`：所属社区 id 与社区名称。
- `node_kind`：`page`（文件级节点）或 `heading`（标题级节点）。
- `source_file` / `source_location`：**溯源信息**——指向 `knowledge-base/` 下的原始 markdown 文件与标题行号（如 `L41`），agent 据此回溯原文。

### 边字段

- `source` / `target`：起点 / 终点节点 id。
- `relation`：关系类型。**当前全部为 `contains`**（文档结构级关系，表示父节点包含子节点；图谱构建时以 AST 结构提取为主，语义级关系未纳入最终图谱）。
- `confidence` / `confidence_score`：提取置信度。
- `weight`：边权重。

## 三、部署步骤

1. 将整个 `embodied-kg-delivery/` 目录拷贝到目标机器（任意位置均可，脚本按相对路径定位数据）。
2. 目标机器只需 **Python 3.8+**（query.py 仅使用标准库，无需 pip 安装任何依赖）。
3. agent 通过 `query.py` 或直接 `json.load` graph.json 消费图谱。

## 四、query.py 用法

在包目录下运行：

```bash
python query.py stats                  # 图谱统计概览
python query.py search <关键词>        # 关键词搜索节点（匹配标签/id/社区名）
python query.py node <node_id>         # 节点详情 + 全部邻居
python query.py neighbors <node_id>    # 仅查看邻居关系
python query.py community <社区id>     # 查看社区全部成员
python query.py source <node_id>       # 回溯节点对应的原文小节
```

**典型 agent 工作流**：`search` 定位节点 → `node` 查看关联结构 → `source` 取回原文段落作为上下文喂给大模型。

## 五、给 agent 的使用说明

1. **图谱是结构化索引，正文在语料里**：graph.json 的节点不存正文，正文在 `knowledge-base/` 的 markdown 中。agent 需要原文内容时，务必用节点的 `source_file + source_location` 回溯，不要假设节点自带内容。
2. **建议先读 GRAPH_REPORT.md**：其中给出社区划分、God Nodes（高连接度枢纽节点）与建议查询问题，可作为理解图谱结构的入口。
3. **边关系现状**：当前边均为 `contains` 结构关系，不是语义关系。做路径推理时按「包含/归属」理解，不要按语义相似理解。
4. **数据为静态快照**：图谱构建于 2026-11-17（graphify 0.9.111）。若语料后续更新，需重新执行构建流程生成新 graph.json 后重新交付。

## 六、重新构建（可选）

如语料有更新，可在源工程目录用 graphify 重新构建（需 Python + graphify 库），产物即 graph.json / graph.html。重建后替换本包内 graph.json 即可，其余文件无需变动。
