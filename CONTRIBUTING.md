# 贡献指南 / Contributing

简体中文 | [English](#contributing-english)

欢迎来到具身智能赛事知识图谱！这个项目的信念很简单：**认知不该只装在一个人的脑子里**。每个参赛者、教师、研究者都在实践中积累了自己的认知——一条赛事经验、一个知识模块的正确解读、一份教材的新版摘要、一条英译——都值得被沉淀下来，让下一个人少走弯路。

Welcome! Our belief is simple: **knowledge should not live in only one person's head**. Every competitor, teacher and researcher accumulates insights worth preserving — a competition lesson, a corrected explanation, a new textbook digest, an English translation.

---

## 三种贡献方式 / Three ways to contribute

| 方式 / Way | 适合 / Best for | 怎么做 / How |
|---|---|---|
| **补一条认知** Add an insight | 任何人，5 分钟 | 在对应语料文件追加小节，或在 `02-教材精华/教材建设动态素材追踪.md` 记录新素材 |
| **修一处译文** Fix a translation | 懂英文/中文的读者 | 编辑 `scripts/translate_graph.py` 的 `LABEL_EN` 字典，运行 `python scripts/translate_graph.py` 重新生成 |
| **纠错与补充** Fix & extend | 发现事实错误或过时信息 | 直接改语料 Markdown，说明依据（来源/日期） |

## 贡献流程 / Workflow

```bash
# 1. Fork 本仓库，然后 clone 你的 fork
git clone https://github.com/<你的用户名>/embodied-kg-delivery.git
cd embodied-kg-delivery

# 2. 建分支（命名建议：contrib/<主题> 或 fix/<主题>）
git checkout -b contrib/lingbo-sim2real-notes

# 3. 修改语料 / 译文 / 文档
#    若改了语料或译文，务必重新生成英文图谱：
python scripts/translate_graph.py
python query.py --en stats   # 确认图谱可正常加载

# 4. 提交并推送
git add -A && git commit -m "docs: add Lingbo Sim-to-Real lesson"
git push origin contrib/lingbo-sim2real-notes

# 5. 在 GitHub 上开 Pull Request，按模板填写
```

## 内容规范 / Content guidelines

- **溯源**：每条素材注明来源（URL/书名）与日期，不编造。
- **口径**：图谱是"先习而后学"的结构化索引，正文在 `knowledge-base/`；保持 MECE 能力域口径一致。
- **最小改动**：一次 PR 聚焦一个主题，便于审阅与合并。
- **敏感信息**：绝不提交 token、密码、私钥（`.gitignore` 已设拦截，但请自查）。
- **中文为主、英文索引**：语料正文保持中文以确保术语准确；英文通过 `graph.en.json` 与 `CORPUS_INDEX_EN.md` 提供。

## 合并标准 / Review criteria

- CI 校验通过（图谱结构、溯源、译文覆盖、敏感信息扫描）。
- 新增节点/标签若未翻译，请在 PR 中同步补上 `LABEL_EN` 条目。
- 事实性内容有可核对的来源。

---

<a name="contributing-english"></a>

## Contributing (English)

This knowledge graph grows through shared cognition. You can contribute in three ways:

1. **Add an insight** — append a section to a corpus file in `knowledge-base/`, or log new material in `02-教材精华/教材建设动态素材追踪.md`.
2. **Fix a translation** — edit the `LABEL_EN` dictionary in `scripts/translate_graph.py`, then run `python scripts/translate_graph.py` to regenerate `graph.en.json`.
3. **Correct and extend** — fix factual errors in the Markdown corpus, always citing the source and date.

**Workflow**: fork → create a branch (`contrib/<topic>`) → edit → (if labels changed) regenerate `graph.en.json` → commit → push → open a Pull Request using the template.

**Guidelines**: cite sources and dates; never fabricate; keep one PR per topic; never commit secrets; keep the corpus in Chinese with English provided via the graph labels and `CORPUS_INDEX_EN.md`.

**Review**: CI checks graph integrity, provenance, translation coverage and secret scanning. Add `LABEL_EN` entries for any new labels. Every merged contributor is added to [CONTRIBUTORS.md](CONTRIBUTORS.md).
