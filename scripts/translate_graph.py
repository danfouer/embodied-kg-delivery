#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate graph.en.json from graph.json by translating node labels,
normalized labels and community names into English.

Design goals
------------
* Node ``id``, ``source_file`` and ``source_location`` are kept UNCHANGED so
  that provenance and ``query.py source`` still resolve to the Chinese corpus.
* The translation is a plain dictionary in this file -- contributors can add
  or fix translations via a pull request (see CONTRIBUTING.md).
* ``--check`` reports untranslated labels and exits non-zero, so CI can guard
  translation coverage whenever the corpus grows.

Usage
-----
    python scripts/translate_graph.py            # write graph.en.json
    python scripts/translate_graph.py --check    # verify coverage (CI mode)
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH_PATH = os.path.join(BASE_DIR, "graph.json")
EN_PATH = os.path.join(BASE_DIR, "graph.en.json")

# ---------------------------------------------------------------------------
# Chinese -> English translation dictionary. Add / improve entries via PR.
# Keys are exact node labels or community names from graph.json.
# ---------------------------------------------------------------------------
LABEL_EN = {
    # ---- file-level page nodes ----
    "人工智能概论.md": "Introduction to Artificial Intelligence.md",
    "人工智能概论（精华）": "Introduction to Artificial Intelligence (Essentials)",
    "智能机器人与具身智能.md": "Intelligent Robots and Embodied AI.md",
    "智能机器人与具身智能（精华）": "Intelligent Robots and Embodied AI (Essentials)",
    "机器学习方法与应用.md": "Machine Learning Methods and Applications.md",
    "机器学习方法与应用（精华）": "Machine Learning Methods and Applications (Essentials)",
    "生成式人工智能.md": "Generative Artificial Intelligence.md",
    "生成式人工智能（精华）": "Generative Artificial Intelligence (Essentials)",
    "自主智能系统基础.md": "Foundations of Autonomous Intelligent Systems.md",
    "自主智能系统基础（精华）": "Foundations of Autonomous Intelligent Systems (Essentials)",
    "自动驾驶理论算法与实践.md": "Autonomous Driving: Theory, Algorithms and Practice.md",
    "自动驾驶理论、算法与实践（精华）": "Autonomous Driving: Theory, Algorithms and Practice (Essentials)",
    "面向具身智能的编程基础.md": "Programming Fundamentals for Embodied AI.md",
    "面向具身智能的编程基础（教学体系精华）": "Programming Fundamentals for Embodied AI (Teaching System Essentials)",
    "IVFC2026中国智能车未来挑战赛.md": "IVFC2026 China Intelligent Vehicle Future Challenge.md",
    "IVFC2026赛事知识映射.md": "IVFC2026 Competition Knowledge Mapping.md",
    "蚂蚁灵波具身大模型挑战赛.md": "Ant Lingbo Embodied Large Model Challenge.md",
    "蚂蚁灵波赛事知识映射.md": "Lingbo Competition Knowledge Mapping.md",
    "MECE能力体系总览.md": "MECE Competency Framework Overview.md",
    "MECE 能力体系总览": "MECE Competency Framework Overview",
    "新赛事扩展接口.md": "New Competition Extension Interface.md",
    "新赛事扩展接口": "New Competition Extension Interface",
    "重组原则与使用说明.md": "Reorganization Principles and Usage Guide.md",
    "具身智能赛事知识图谱 · 重组原则与使用说明": "Embodied-AI Competition Knowledge Graph - Reorganization Principles and Usage Guide",

    # ---- corpus-level section nodes ----
    "知识体系精华": "Knowledge System Essentials",
    "第一部分 智能机器人": "Part I: Intelligent Robots",
    "第二部分 具身智能": "Part II: Embodied AI",
    "核心方法论": "Core Methodology",
    "定位": "Positioning",
    "关键说明": "Key Notes",
    "映射总表": "Master Mapping Table",
    "双主线结构": "Dual-Mainline Structure",
    "核心架构：三阶火箭": "Core Architecture: The Three-Stage Rocket",
    "自驱引擎": "Self-Driven Engine",
    "覆盖率体检与前置缺口": "Coverage Checkup and Prerequisite Gaps",
    "三道硬约束": "Three Hard Constraints",
    "六个能力域（读 · 写 · 算 · 审 · 构 · 迁）": "Six Competency Domains (Read, Write, Compute, Audit, Build, Migrate)",
    "四能级阶梯（L1–L4）": "Four-Level Ladder (L1-L4)",
    "结构：能控 → 能观 → 综合": "Structure: Controllable -> Observable -> Synthesis",
    "能力图谱：六域四能级矩阵": "Competency Map: Six-Domain x Four-Level Matrix",
    "两册的域分工规律": "Domain Division Rule Across the Two Volumes",
    "上册《能控能观》：C 程序设计与数据结构": "Volume I 'Controllable & Observable': C Programming and Data Structures",
    "下册《故事新编》：从 TAOCP 到具身智能": "Volume II 'Stories Rewritten': From TAOCP to Embodied AI",
    "与六本教材的关系": "Relationship with the Six Textbooks",
    "与赛事的关联": "Links to Competitions",
    "教学方法：95 个 TAOCP 发明者故事": "Teaching Method: 95 TAOCP Inventor Stories",
    "20 个必做 TAOCP 复现清单": "20 Mandatory TAOCP Reproduction Tasks",
    "教学落地：两门课程设计的评分验证": "Teaching Delivery: Scoring Validation of Two Course Designs",
    "程序语言与数据结构课程设计（上册对应）": "Programming Language and Data Structures Course Design (Volume I)",
    "微处理器与控制器课程设计（下册 B 主线对应）": "Microprocessor and Controller Course Design (Volume II, Mainline B)",

    # ---- general principles / MECE ----
    "一、核心理念：先习而后学，赛事牵引": "I. Core Philosophy: Practice First, Learn Later, Competition-Driven",
    "一、MECE 划分原则": "I. MECE Partitioning Principles",
    "一、扩展原则": "I. Extension Principles",
    "一、赛事概况": "I. Competition Overview",
    "二、MECE 重组原则": "II. MECE Reorganization Principles",
    "二、能力域划分（MECE）": "II. Competency Domain Partition (MECE)",
    "二、扩展操作步骤": "II. Extension Procedure",
    "二、评测口径": "II. Evaluation Criteria",
    "二、赛事平台（CARLA 0.9.16）": "II. Competition Platform (CARLA 0.9.16)",
    "三、六本教材的定位": "III. Positioning of the Six Textbooks",
    "三、能力域之间的逻辑关系": "III. Logical Relationships Among Competency Domains",
    "三、扩展示例（假设新增「无人机自主导航挑战赛」）": "III. Extension Example (Assuming a New 'UAV Autonomous Navigation Challenge')",
    "三、提交要求": "III. Submission Requirements",
    "三、本地测试环境要求": "III. Local Test Environment Requirements",
    "四、与教材知识模块的对应": "IV. Correspondence with Textbook Knowledge Modules",
    "四、接口的可查询性": "IV. Queryability of the Interface",
    "四、模型与环境": "IV. Models and Environment",
    "四、知识图谱的构建与管理": "IV. Knowledge Graph Construction and Management",
    "四、算法接入接口": "IV. Algorithm Integration Interface",
    "五、学习路径建议": "V. Recommended Learning Path",
    "五、对参赛者的能力要求（赛事牵引的能力域）": "V. Competitor Requirements (Competition-Driven Domains)",
    "五、评分口径": "V. Scoring Criteria",
    "六、对参赛者的能力要求（赛事牵引的能力域）": "VI. Competitor Requirements (Competition-Driven Domains)",
    "按「先习而后学」的路径组织": "Organized by the 'Practice First, Learn Later' Path",
    "第一阶：先参赛（习）——直接动手": "Stage 1: Compete First (Practice) - Hands On",
    "第二阶：再补学（学）——按问题回溯知识": "Stage 2: Learn Later - Trace Back from Problems",
    "第三阶：验证迭代（验）": "Stage 3: Validate and Iterate",
    "第四阶：决赛跃迁（真机交付）": "Stage 4: Leap to the Finals (Real-Robot Delivery)",

    # ---- MECE competency domains ----
    "能力域 1：仿真环境与系统接入能力": "Domain 1: Simulation Environment and System Integration",
    "能力域 2：多传感器感知与融合能力": "Domain 2: Multi-Sensor Perception and Fusion",
    "能力域 3：定位与地图能力": "Domain 3: Localization and Mapping",
    "能力域 4：决策与任务规划能力": "Domain 4: Decision Making and Task Planning",
    "能力域 5：运动规划与控制能力": "Domain 5: Motion Planning and Control",
    "能力域 6：具身大模型与多模态能力": "Domain 6: Embodied Large Models and Multimodality",
    "能力域 7：策略学习与训练能力": "Domain 7: Policy Learning and Training",
    "能力域 8：仿真测试与验证能力": "Domain 8: Simulation Testing and Validation",
    "能力域 9：编程基础与系统交付能力": "Domain 9: Programming Fundamentals and System Delivery",
    "三、能力域之间的逻辑关系": "III. Logical Relationships Among Competency Domains",

    # ---- extension interface ----
    "步骤 1：登记赛事目标": "Step 1: Register Competition Objectives",
    "步骤 2：评估能力域": "Step 2: Assess Competency Domains",
    "步骤 3：建立知识映射": "Step 3: Build Knowledge Mapping",
    "步骤 4：补充知识模块（如需）": "Step 4: Add Knowledge Modules (if needed)",
    "步骤 5：重建图谱": "Step 5: Rebuild the Graph",

    # ---- competitions ----
    "IVFC2026 · 中国智能车未来挑战赛": "IVFC2026 - China Intelligent Vehicle Future Challenge",
    "IVFC2026 · 赛事—能力域—知识模块映射": "IVFC2026 - Competition-Competency-Knowledge Mapping",
    "蚂蚁灵波具身大模型挑战赛": "Ant Lingbo Embodied Large Model Challenge",
    "蚂蚁灵波具身大模型挑战赛 · 赛事—能力域—知识模块映射": "Ant Lingbo Embodied Large Model Challenge - Competition-Competency-Knowledge Mapping",
    "决赛阶段补充映射（2026-11-16 真机决赛）": "Final-Stage Supplemental Mapping (2026-11-16 Real-Robot Finals)",
    "6.1 决赛基本配置": "6.1 Finals Basic Setup",
    "6.2 决赛对能力域的具体要求": "6.2 Specific Competency Requirements for the Finals",
    "6.3 决赛各团队方案与成绩": "6.3 Team Solutions and Results in the Finals",
    "6.4 决赛核心教训（与第 6 章跨越鸿沟的呼应）": "6.4 Core Lessons from the Finals (Echoing Chapter 6: Crossing the Gap)",
    "六、决赛阶段（2026-11-16 决赛答辩实录）": "VI. Final Stage (2026-11-16 Finals Defense Record)",

    # ---- textbook chapter headings (generic) ----
    "第1章 绪论": "Chapter 1: Introduction",
    "三、六本教材的定位": "III. Positioning of the Six Textbooks",

    # Introduction to AI
    "第2章 知识表示": "Chapter 2: Knowledge Representation",
    "第3章 搜索求解": "Chapter 3: Search and Problem Solving",
    "第4章 博弈搜索": "Chapter 4: Adversarial Search",
    "第5章 确定性推理": "Chapter 5: Deterministic Reasoning",
    "第6章 不确定性推理": "Chapter 6: Reasoning under Uncertainty",
    "第7章 机器学习": "Chapter 7: Machine Learning",
    "第8章 概率图模型": "Chapter 8: Probabilistic Graphical Models",
    "第9章 大语言模型": "Chapter 9: Large Language Models",
    "第10章 神经网络": "Chapter 10: Neural Networks",
    "第10章 大模型": "Chapter 10: Large Models",
    "第11章 生成式人工智能的评估、安全与伦理": "Chapter 11: Evaluation, Safety and Ethics of Generative AI",

    # Machine Learning
    "第1章 机器学习基础": "Chapter 1: Foundations of Machine Learning",
    "第2章 非参数化模型": "Chapter 2: Nonparametric Models",
    "第3章 线性模型": "Chapter 3: Linear Models",
    "第4章 聚类方法": "Chapter 4: Clustering Methods",
    "第5章 决策树": "Chapter 5: Decision Trees",
    "第6章 EM 算法与隐变量模型": "Chapter 6: EM Algorithm and Latent Variable Models",
    "第7章 集成学习": "Chapter 7: Ensemble Learning",
    "第8章 神经网络与深度学习": "Chapter 8: Neural Networks and Deep Learning",
    "第13章 强化学习基础": "Chapter 13: Foundations of Reinforcement Learning",

    # Generative AI
    "第1章 生成式人工智能概述": "Chapter 1: Overview of Generative AI",
    "第2章 生成模型基础": "Chapter 2: Foundations of Generative Models",
    "第3章 Transformer": "Chapter 3: Transformer",
    "第4章 生成对抗网络（GAN）": "Chapter 4: Generative Adversarial Networks (GAN)",
    "第5章 自回归模型": "Chapter 5: Autoregressive Models",
    "第6章 流模型": "Chapter 6: Flow Models",
    "第7章 能量模型": "Chapter 7: Energy-Based Models",
    "第8章 扩散模型": "Chapter 8: Diffusion Models",
    "第9章 大语言模型": "Chapter 9: Large Language Models",
    "第10章 多模态生成及应用": "Chapter 10: Multimodal Generation and Applications",
    "第11章 生成式模型": "Chapter 11: Generative Models",

    # Autonomous Systems
    "第1章 自主智能系统概述": "Chapter 1: Overview of Autonomous Intelligent Systems",
    "第2章 自主智能系统反馈理论": "Chapter 2: Feedback Theory for Autonomous Systems",
    "第4章 自主决策系统": "Chapter 4: Autonomous Decision Systems",
    "第5章 智能控制系统": "Chapter 5: Intelligent Control Systems",
    "第13章 认知和神经科学启发的自动驾驶系统": "Chapter 13: Cognition- and Neuroscience-Inspired Autonomous Driving",
    "第14章 基于数据驱动的学习型自动驾驶系统": "Chapter 14: Data-Driven Learning-Based Autonomous Driving",

    # Autonomous Driving
    "第2章 自动驾驶的传感器系统": "Chapter 2: Sensor Systems for Autonomous Driving",
    "第3章 交通场景感知与理解": "Chapter 3: Traffic Scene Perception and Understanding",
    "第4章 弱势道路使用者（VRU）的行为识别与预测": "Chapter 4: Vulnerable Road User (VRU) Behavior Recognition and Prediction",
    "第5章 自动驾驶周围车辆行为预测与驾驶风格识别": "Chapter 5: Surrounding Vehicle Behavior Prediction and Driving Style Recognition",
    "第6章 自动驾驶的高精度地图": "Chapter 6: High-Definition Maps for Autonomous Driving",
    "第7章 自动驾驶的空间定位": "Chapter 7: Spatial Localization for Autonomous Driving",
    "第8章 自动驾驶的行为决策": "Chapter 8: Behavioral Decision Making for Autonomous Driving",
    "第9章 自动驾驶的运动规划": "Chapter 9: Motion Planning for Autonomous Driving",
    "第10章 自动驾驶的控制": "Chapter 10: Control for Autonomous Driving",
    "第11章 自动驾驶的仿真、测试与验证": "Chapter 11: Simulation, Testing and Validation for Autonomous Driving",
    "第12章 室内智能移动机器人": "Chapter 12: Indoor Intelligent Mobile Robots",

    # Robotics and Embodied AI
    "第1章 机器人构成": "Chapter 1: Robot Composition",
    "第2章 机器人学基础": "Chapter 2: Fundamentals of Robotics",
    "第3章 机器人感知与传感": "Chapter 3: Robot Perception and Sensing",
    "第4章 运动控制": "Chapter 4: Motion Control",
    "第5章 导航与路径规划": "Chapter 5: Navigation and Path Planning",
    "第6章 决策与任务规划": "Chapter 6: Decision Making and Task Planning",
    "第7章 具身智能概论": "Chapter 7: Introduction to Embodied AI",
    "第8章 具身多模态大模型": "Chapter 8: Embodied Multimodal Large Models",
    "第9章 具身交互学习": "Chapter 9: Embodied Interactive Learning",
    "第3章 环境感知系统": "Chapter 3: Environmental Perception Systems",

    # ---- dynamic material-tracking file & mapping supplements (daily collection) ----
    "教材建设动态素材追踪.md": "Textbook Development Material Tracker.md",
    "具身智能教材建设动态素材追踪": "Embodied-AI Textbook Development Material Tracker",
    "2026-11-18 采集（关键词 6 组）": "2026-11-18 Collection (6 Keyword Groups)",
    "一、具身智能新教材出版动态": "I. New Embodied-AI Textbook Publications",
    "二、重点专题：《具身智能机器人实践与应用》（清华社，2026-04）": "II. Featured: 'Embodied Intelligence Robot Practice and Applications' (Tsinghua UP, 2026-04)",
    "三、教材建设机制动态：智元启动具身智能教材体系建设": "III. Textbook Development Mechanism: AgiBot Launches Embodied-AI Textbook System",
    "四、核心教材补充信息：《智能机器人与具身智能》（张涛主编）": "IV. Core Textbook Update: 'Intelligent Robots and Embodied AI' (ed. Zhang Tao)",
    "五、英文参考：Building Embodied AI（第二版，2026）": "V. English Reference: Building Embodied AI (2nd ed., 2026)",
    "六、系统建模与仿真教材": "VI. Systems Modeling and Simulation Textbooks",
    "七、平行智能 / ACP 方法 / 数字孪生（学术资源，无新教材）": "VII. Parallel Intelligence / ACP / Digital Twin (Academic Resources, No New Textbooks)",
    "八、数字孪生课程设计案例（国际/国内）": "VIII. Digital Twin Course Design Cases (International / Domestic)",
    "九、人形机器人建模仿真平台生态（2025–2026 更新）": "IX. Humanoid Robot Modeling & Simulation Platform Ecosystem (2025-2026 Update)",
    "十、认知架构 / 具身认知课程资源（无新中文教材）": "X. Cognitive Architecture / Embodied Cognition Course Resources (No New Chinese Textbooks)",
    "待跟进清单（滚动）": "Follow-up Checklist (Rolling)",
    "外部生态资源映射（2026-11-18 素材采集）": "External Ecosystem Resource Mapping (2026-11-18 Collection)",

    # ---- methodology assessment of the embodied-AI introductory textbook ----
    "具身智能专业导论方法论与赛事指导价值评估.md": "Methodology Assessment of the Embodied-AI Introductory Textbook and Its Guiding Value for Competitions.md",
    "具身智能专业导论方法论与赛事指导价值评估": "Methodology Assessment of the Embodied-AI Introductory Textbook and Its Guiding Value for Competitions",
    "一、结论": "I. Conclusion",
    "二、教材概况": "II. Textbook Overview",
    "三、方法论骨架：七章一条主线": "III. Methodology Framework: Seven Chapters, One Main Line",
    "四、普适性的三个硬依据": "IV. Three Hard Reasons for Universality",
    "依据一：教材用真实赛事自证方法论，而非空谈": "Basis 1: The Textbook Proves Its Methodology with a Real Competition, Not Empty Talk",
    "依据二：PCA 闭环 + ACP 是赛事的通用范式": "Basis 2: The PCA Loop + ACP Is the Universal Paradigm of Competitions",
    "依据三：配套 6 个递进实验，天然对应参赛全生命周期": "Basis 3: Six Progressive Labs Map Naturally onto the Full Competition Lifecycle",
    "五、与赛事知识的关系：方法论层 × 赛事层互补": "V. Relation to Competition Knowledge: Methodology Level x Competition Level, Complementary",
    "六、边界与局限（如实说明）": "VI. Boundaries and Limitations (Stated as They Are)",
    "七、使用建议": "VII. Usage Suggestions",
    "来源说明": "Source Notes",

    # ---- usage case study (Ant LingBot embodied large model challenge path) ----
    "知识图谱使用案例-蚂蚁灵波参赛路径.md": "Knowledge Graph Usage Case - Ant LingBot Participation Path.md",
    "知识图谱使用案例 · 以蚂蚁灵波具身大模型挑战赛参赛路径为例": "Knowledge Graph Usage Case: The Ant LingBot Embodied Large Model Challenge Participation Path",
    "二、案例背景：一名学生想参加蚂蚁灵波具身大模型挑战赛": "II. Case Background: A Student Wants to Join the Ant LingBot Embodied Large Model Challenge",
    "步骤 2｜定位赛事节点:搜索「蚂蚁灵波」": "Step 2 | Locate Event Nodes: Search 'Ant LingBot'",
    "步骤 3｜锁定关键问题:评测口径": "Step 3 | Pin Down the Key Question: Evaluation Rules",

    # ---- usage case study (IVFC2026 participation path) ----
    "知识图谱使用案例-IVFC2026参赛路径.md": "Knowledge Graph Usage Case - IVFC2026 Participation Path.md",
    "知识图谱使用案例 · 以 IVFC2026 参赛路径为例": "Knowledge Graph Usage Case: The IVFC2026 Participation Path",
    "一、核心用法：图谱是索引,原文才是内容": "I. Core Usage: The Graph Is an Index, the Corpus Is the Content",
    "二、案例背景：一名学生想参加 IVFC2026": "II. Case Background: A Student Wants to Join IVFC2026",
    "步骤 1｜全局感知：先问图谱有多大、有哪些社区": "Step 1 | Global View: How Large Is the Graph and What Communities Exist",
    "步骤 2｜定位赛事节点:搜索「IVFC2026」": "Step 2 | Locate Event Nodes: Search 'IVFC2026'",
    "步骤 3｜锁定关键问题:评分口径": "Step 3 | Pin Down the Key Question: Scoring Rules",
    "步骤 4｜溯源:把原文取回来（关键一步）": "Step 4 | Trace to Source: Retrieve the Original Text (Key Step)",
    "步骤 5｜从赛事反查学习路径:能力域—知识模块—教材": "Step 5 | Reverse-Map the Learning Path: Ability Domain - Knowledge Module - Textbook",
    "步骤 6｜按「先习而后学」排出学习顺序": "Step 6 | Sequence Learning by 'Practice Before Theory'",
    "三、案例小结:图谱的正确打开方式": "III. Case Summary: The Right Way to Use the Graph",
    "四、给 agent 的一段可复用提示词": "IV. A Reusable Prompt for Agents",
    "五、相关阅读": "V. Further Reading",
}


def translate(text):
    """Translate a label/community name. Untranslated strings are marked but
    never block graph generation, so daily corpus growth cannot break CI."""
    if text in LABEL_EN:
        return LABEL_EN[text], "translated"
    return text, "untranslated"


def collect_missing(g):
    labels = {n.get("label", "") for n in g["nodes"]}
    comms = {n.get("community_name", "") for n in g["nodes"] if n.get("community_name")}
    return sorted(s for s in labels | comms if s and s not in LABEL_EN)


def check_coverage(g, strict=True):
    strings = {n.get("label", "") for n in g["nodes"]} | {
        n.get("community_name", "") for n in g["nodes"] if n.get("community_name")}
    missing = collect_missing(g)
    print(f"Translatable strings: {len(strings - {''})}; dictionary entries: {len(LABEL_EN)}")
    if missing:
        print(f"UNTRANSLATED ({len(missing)}) -- contributions welcome:")
        for s in missing:
            print("  -", s)
        if strict:
            return False
        print("Coverage: partial (non-strict mode: generation continues).")
        return True
    print("Coverage: 100% - every label and community name has an English entry.")
    return True


def build_en(g):
    en = json.loads(json.dumps(g))  # deep copy
    untranslated = 0
    for n in en["nodes"]:
        label = n.get("label", "")
        cn = n.get("community_name", "")
        label_en, lstatus = translate(label)
        n["label"] = label_en
        n["norm_label"] = label_en.lower()
        if cn:
            cn_en, cstatus = translate(cn)
            n["community_name"] = cn_en
            if cstatus == "untranslated":
                n["translation_status"] = "partial"
        if lstatus == "untranslated":
            n["translation_status"] = "untranslated"
            untranslated += 1
        n["label_zh"] = label  # keep original for bilingual traceability
        if cn:
            n["community_name_zh"] = cn
    en["graph"] = dict(en.get("graph", {}))
    en["graph"]["language"] = "en"
    en["graph"]["translation_source"] = "scripts/translate_graph.py"
    total = len(en["nodes"])
    en["graph"]["translated_nodes"] = total - untranslated
    en["graph"]["total_nodes"] = total
    return en


def write_gaps(g):
    """Write I18N_GAPS.md -- an open call for translation contributions."""
    missing = collect_missing(g)
    path = os.path.join(BASE_DIR, "I18N_GAPS.md")
    lines = [
        "# 待译标签 / Translation Gaps",
        "",
        "这些节点标签尚未英译。欢迎通过 PR 在 `scripts/translate_graph.py` 的",
        "`LABEL_EN` 字典中补充条目 —— 这是一个很好的首次贡献入口。",
        "",
        "These labels have no English translation yet. Add them to `LABEL_EN`",
        "in `scripts/translate_graph.py` via a PR — a great first contribution.",
        "",
    ]
    if missing:
        lines += [f"共 {len(missing)} 条 / {len(missing)} entries:", ""]
        lines += [f"- `{s}`" for s in missing]
    else:
        lines += ["当前无缺口 / No gaps — 100% covered ✅"]
    lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {path} ({len(missing)} gaps)")


def main():
    with open(ZH_PATH, "r", encoding="utf-8") as f:
        g = json.load(f)
    if "--check" in sys.argv:
        sys.exit(0 if check_coverage(g, strict=True) else 1)
    en = build_en(g)
    ok = check_coverage(g, strict=False)
    with open(EN_PATH, "w", encoding="utf-8") as f:
        json.dump(en, f, ensure_ascii=False, indent=2)
    write_gaps(g)
    print(f"Wrote {EN_PATH} ({len(en['nodes'])} nodes, {len(en['links'])} links); coverage_ok={ok}")


if __name__ == "__main__":
    main()
