# Graph Report — knowledge-base (2026-11-17)

[简体中文](GRAPH_REPORT.md) | English

## Corpus Check
- Corpus: 14 Markdown files, ~2,500+ words. Includes the newly added *Programming Fundamentals for Embodied AI* teaching-system module and the Lingbo competition final-stage supplements.
- Note: The corpus is written in Chinese; this report is the English documentation layer.

## Summary
- 189 nodes · 175 edges · 14 communities
- All edges EXTRACTED from the corpus (100% EXTRACTED, 0% INFERRED, 0% AMBIGUOUS)
- Health check: 0 dangling edges · 0 self-loops · 0 isolated nodes ✅
- Token cost: full-corpus semantic extraction (14 files)

## Corpus Composition
| Source File | Nodes | Role |
|---|---|---|
| 02-教材精华/面向具身智能的编程基础.md | 22 | NEW — programming fundamentals teaching system (three-stage rocket, two volumes, six domains × four levels) |
| 02-教材精华/自动驾驶理论算法与实践.md | 20 | Autonomous-vehicle systems knowledge |
| 02-教材精华/智能机器人与具身智能.md | 17 | Embodied robotics knowledge |
| 02-教材精华/机器学习方法与应用.md | 17 | Machine learning knowledge |
| 02-教材精华/生成式人工智能.md | 17 | Generative AI knowledge |
| 03-MECE能力体系/MECE能力体系总览.md | 15 | 9 MECE competency domains (incl. new domain 9: programming fundamentals) |
| 02-教材精华/人工智能概论.md | 14 | AI fundamentals |
| 02-教材精华/自主智能系统基础.md | 11 | Autonomous-system closed loop |
| 04-赛事知识映射/新赛事扩展接口.md | 11 | Extension interface for new competitions |
| 04-赛事知识映射/IVFC2026赛事知识映射.md | 8 | IVFC mapping (incl. domain 9) |
| 04-赛事知识映射/蚂蚁灵波赛事知识映射.md | 10 | Lingbo mapping (incl. domain 9 + final-stage supplemental mapping) |
| 01-赛事目标/IVFC2026中国智能车未来挑战赛.md | 8 | IVFC competition objectives |
| 00-总纲/重组原则与使用说明.md | 7 | General principles (incl. programming-foundation layer) |
| 01-赛事目标/蚂蚁灵波具身大模型挑战赛.md | 12 | NEW final stage (three real-robot tasks, compute setup, capability requirements, team solutions, core lessons) |

## Community Hubs (Navigation)
- Knowledge System Essentials (79 nodes — aggregated community of the six textbook digests)
- **Programming Fundamentals for Embodied AI (Teaching System Essentials)** (22 nodes — new programming module)
- Part I: Intelligent Robots (17 nodes)
- II. MECE Competency Domain Partition (15 nodes — incl. domain 9)
- II. Extension Procedure (11 nodes)
- IVFC2026 · Competition–Competency–Knowledge Mapping (8 nodes)
- Organizing by the "Practice First, Learn Later" Path (8 nodes)
- IVFC2026 · China Intelligent Vehicle Future Challenge (8 nodes)
- Embodied-AI Competition Knowledge Graph · Principles of Reorganization (7 nodes)
- Lingbo Embodied Large-Model Challenge (12 nodes — incl. final-stage real-robot tasks, four gaps, team solutions)

## God Nodes (most connected — core abstractions)
1. `知识体系精华` (Knowledge System Essentials, multi-file aggregate) — 15 edges
2. `知识体系精华` — 12 edges
3. `知识体系精华` — 12 edges
4. **`面向具身智能的编程基础（教学体系精华）`** (Programming Fundamentals for Embodied AI) — 11 edges
5. `知识体系精华` — 10 edges
6. `二、能力域划分（MECE）` (MECE Domain Partition) — 10 edges
7. `IVFC2026 · 中国智能车未来挑战赛` — 7 edges
8. **`蚂蚁灵波具身大模型挑战赛`** (Lingbo Challenge, incl. final stage) — 7 edges
9. `第一部分 智能机器人` (Part I: Intelligent Robots) — 7 edges
10. `具身智能赛事知识图谱 · 重组原则与使用说明` (Graph Principles) — 6 edges

> *Programming Fundamentals for Embodied AI* ranks 4th among God Nodes with 11 edges — the hub of the programming module, linking both volumes, the competency map, teaching delivery, competition links and the relationship to the six textbooks.
>
 *Lingbo Embodied Large-Model Challenge* ranks 8th with 7 edges; its final stage adds three real-robot tasks, four gaps and team solutions, making it one of the richest nodes in the competition-objective layer.

## Surprising Connections (cross-file links)
- `面向具身智能的编程基础（教学体系精华）` --contains--> `与赛事的关联` [EXTRACTED]
  → the competition-links section inside the programming module
- `面向具身智能的编程基础（教学体系精华）` --contains--> `与六本教材的关系` [EXTRACTED]
  → programming fundamentals as the foundation for the six textbooks
- `二、能力域划分（MECE）` --contains--> `能力域 9：编程基础与系统交付能力` [EXTRACTED]
  → programming fundamentals as the 9th MECE competency domain
- `具身智能赛事知识图谱 · 重组原则与使用说明` --contains--> programming-foundation layer [EXTRACTED]
  → the general principles incorporate the programming foundation
- `蚂蚁灵波具身大模型挑战赛` --contains--> `六、决赛阶段（2026-11-16 决赛答辩实录）` [EXTRACTED]
  → final-stage section with three real-robot tasks and four gaps

## Hyperedges
- No hyperedge metadata was generated in this rebuild (hyperedges=0). The 3 hyperedges in an earlier version (MECE framework, six-textbook knowledge base, VLA tech stack) came from an older extraction; the full rebuild left the hyperedge set empty. Core nodes and edges are unaffected; `graphify path` / `explain` queries work normally.

## Communities (14 total)

### Community "知识体系精华" (79 nodes)
Aggregated community of the six textbook digests, covering AI introduction, autonomous systems, machine learning, generative AI, intelligent robots and autonomous driving. Cohesion comes from the internal links of each textbook's "Knowledge System Essentials" section.

### Community "面向具身智能的编程基础（教学体系精华）" (22 nodes)
NEW. Core community of the embodied-AI programming teaching system: three-stage rocket, Volume I *Controllable & Observable*, Volume II *Stories Rewritten*, 95 TAOCP stories, 20 mandatory tasks, three hard constraints, six-domain × four-level matrix, self-driven engine, coverage checkup, two course-design scoring validations, competition links and the relationship to the six textbooks.

### Community "二、能力域划分（MECE）" (15 nodes)
MECE competency framework community, containing 9 competency domain nodes (incl. new domain 9: programming fundamentals and system delivery) and their logical relationships.

### Community "IVFC2026 · 赛事—能力域—知识模块映射" (8 nodes)
IVFC2026 mapping file community, with the mapping table and the "Practice First, Learn Later" path, including the domain-9 (programming fundamentals) row.

### Community "蚂蚁灵波赛事—能力域—知识模块映射" (10 nodes)
Lingbo mapping file community, with the domain-9 row, the "Practice First, Learn Later" path, and the **final-stage supplemental mapping** (three real-robot tasks, Sim-to-Real four gaps, training acceleration, data collection and distribution alignment).

### Community "蚂蚁灵波具身大模型挑战赛" (12 nodes)
Lingbo competition-objective community, **with a newly added final stage**: three real-robot tasks (grab fruit / cosmetic case / take out trash), compute setup (8×A5000 training + 5080 inference), eight capability requirements for the finals, on-site handling of the four gaps, team solutions and results, and core lessons.

## Knowledge Gaps
- **No isolated nodes**: health check shows 0 isolated nodes; every node has at least one edge.
- **No dangling edges**: all edge endpoints exist in the node set.
- **No self-loops**: no edge with source=target.
- **Hyperedges empty**: no hyperedge metadata in this full rebuild. To restore the 3 earlier hyperedges (MECE framework, six-textbook base, VLA tech stack), add hyperedge annotations in a later extraction. Core graph query functionality is unaffected.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **How does Programming Fundamentals for Embodied AI support the programming capability of both competitions?**
  From the programming-fundamentals hub, via the "competition links" node, trace how programming fundamentals serve as the entry ticket, system integration and audit/migration support for IVFC2026 and Lingbo.

- **Where does programming fundamentals sit in the MECE framework?**
  From the "MECE Domain Partition" community, find "Domain 9: Programming Fundamentals and System Delivery" — the 9th domain alongside the other 8 competition competency domains, positioned as the programming foundation for all.

- **What is the relationship between programming fundamentals and the six textbooks?**
  Via the "relationship to six textbooks" node: programming fundamentals make programs correct and well-written; the six textbooks cover how to build intelligent systems.

- **How do IVFC2026 and Lingbo map to programming fundamentals?**
  Both mapping tables include a "programming fundamentals and system delivery" row, listing C language & data structures, industrial algorithms, embedded delivery and their source textbooks.

- **What core capabilities does the Lingbo final stage test?**
  From the final-stage nodes: three real-robot tasks, compute setup, eight capability requirements, and the four Sim-to-Real gaps (dynamics / perception / distribution / dynamics uncertainty) with on-site responses and team results.

- **How do the Lingbo final-stage Sim-to-Real gaps map to textbook knowledge?**
  From the supplemental mapping table: inaccurate dynamics → motion control & residual learning; perception differences → robot sensing; distribution shift → model evaluation & validation; dynamic uncertainty → simulation testing & validation. This is the competition evidence for Chapter 6 "Crossing the Gap" theory.
