# Milestone & Issue Design Patterns

Real-world examples showing the expected quality level. Read this file when you need inspiration for structuring milestones and issues.

**Implementation note**: Milestones are implemented as **labels** in Multica (not parent issues). All issues are flat. The `Issues:` lists below show which issues receive each milestone label.

## Table of Contents

1. [Research Project Example](#research-project)
2. [Engineering Project Example](#engineering-project)
3. [Monitoring Project Example](#monitoring-project)
4. [Deep Dive Series Pattern](#deep-dive-series)
5. [Issue Description Examples](#issue-description-examples)
6. [Anti-Patterns](#anti-patterns)

---

## Research Project

**Project**: Paladin 隐私框架与 Mantle L2 集成可行性研究

```
M1: Paladin 架构与核心概念研究
    → 深入理解 Paladin 的整体架构、核心设计理念、三大隐私域以及与 EVM 的交互模式。
    Issues:
      [high]   Paladin 整体架构与设计理念研究
      [medium] Noto（Notarized Tokens）域深入分析
      [medium] Zeto（ZKP Tokens）域深入分析
      [medium] Pente（Private EVM）域深入分析
      [medium] Paladin 运行时核心组件分析
      [high]   Paladin 本地环境搭建与运行验证

M2: Mantle 架构分析与集成可行性评估
    → 分析 Mantle L2 架构，评估集成的技术可行性，识别路径和潜在冲突。
    Issues:
      [high]   Mantle L2 架构梳理与差异分析
      [high]   Paladin EVM 兼容性需求 vs Mantle op-geth 差异分析
      [high]   集成路径识别与对比分析
      [medium] 技术冲突与风险分析
      [medium] 企业级隐私场景需求定义与能力映射

M3: 集成方案设计与 PoC 验证
    → 设计具体的集成方案，进行 PoC 实验验证，输出最终技术推荐报告。
    Issues:
      [high]   推荐集成方案详细架构设计
      [urgent] PoC 环境搭建与集成验证
      [high]   最终技术方案对比与推荐报告
```

**Key patterns**: Progressive depth (overview → analysis → synthesis), each milestone builds on the previous, issues within a milestone cover distinct subtopics.

---

## Engineering Project

**Project**: 自维护 agents 工具 (Multica agent config repo)

```
M0: Project Setup & Design Review
    → Lock v1 positioning, align docs/schema, run review, add validation.
    Issues:
      [urgent] Define repo directory structure and create scaffolding
      [urgent] Review and harden CLAUDE.md with full project conventions
      [urgent] Review and harden README.md and AGENTS.md
      [high]   Standardize agent init config YAML schema
      [urgent] GPT review of architecture and design decisions
      [high]   Decide v1 skill source strategy
      [urgent] Lock project direction and update design references
      [high]   Add minimal config validator (scripts/validate)

M1: Research Pipeline (First Experiment)
    → Implement and validate the first agent pair with prompts, configs, fixtures, E2E runs.
    Issues:
      [urgent] Write research-agent system prompt
      [urgent] Write research-review-agent system prompt
      [high]   Write shared prompt fragments
      [high]   Create agent YAML configs
      [high]   Create agents on Multica and run end-to-end test
      [medium] Add research pipeline fixtures and example briefs

M2: Knowledge Base & Scaling
    → Use M1 evidence to decide how to scale.
    Issues:
      [high]   M1 retrospective and scaling decision
      [medium] Design and implement knowledge base structure
      [medium] Add third agent to validate scaling patterns
      [low]    Write helper scripts (init-agent, sync-skills)
      [medium] Third-party skill safety checklist
```

**Key patterns**: M0 for foundation, includes explicit "decision issues" (skill source strategy, lock direction), includes "review issues" (GPT review), clear dependency chains.

**Dependency highlights**:
- Parallelizable starts: scaffolding, CLAUDE.md review, README review, GPT review can all begin simultaneously
- Convergence point: "Lock project direction" blocks on reviews + decisions before M1 can begin
- M1/#3 (shared prompt fragments) has no blockers — can start in parallel with M0 work

---

## Monitoring Project

**Project**: Mantle AAVE Monitor

```
Phase 1: Hello World Pipeline
    → Prove end-to-end: RPC → indexer → TimescaleDB → Grafana. One event, one panel.
    Issues: environment setup, single event indexer, basic Grafana panel

Phase 2: Full Event Indexer
    → All 6 AAVE V3 event types, backfill, reconnection, Event List Dashboard.
    Issues: per-event-type indexer, backfill logic, gap-fill, dashboard

Phase 3: State Poller + Pool Dashboards
    → State Poller service, Overview and Per-Pool dashboards.
    Issues: state poller, oracle data, overview dashboard, per-pool dashboard

Phase 4: Whale Monitor
    → Whale watchlist, position poller with Multicall3, Whale Dashboard.
    Issues: whale identification, position polling, dashboard

Phase 5: Oracle Health + Alerting
    → Oracle Health Dashboard, TWAP deviation, staleness detection, Grafana alerts.
    Issues: oracle health checks, alerting rules, notification channels
```

**Key patterns**: Uses "Phase" instead of "M" for infra projects, each phase is a self-contained deployable increment, Phase 1 is always a "hello world" proving the pipeline.

---

## Deep Dive Series

When a milestone contains a research series, issues are numbered sequentially:

```
Deep Dive #1: 核心设计哲学 — 为什么不改 EVM？
Deep Dive #2: 隐私交易全生命周期 — 从 API 调用到链上落账
Deep Dive #3: UTXO 状态模型与分布式并发控制
Deep Dive #4: 零知识证明系统 — Zeto 的密码学全栈解析
Deep Dive #5: Pente 临时 EVM — 链下执行、链上锚定
Deep Dive #6: 原子跨域结算 — Atom/AtomFactory 与 DvP 模式
Deep Dive #7: 企业级基础设施 — 密钥管理、身份体系与节点通信
Deep Dive #8: 综合评估 — 技术定位

综合文章大纲设计 (synthesis outline issue)
综合文章撰写 (final article issue)
```

---

## Issue Description Examples

### Decision Issue

```markdown
## Goal

Decide the v1 strategy for finding and attaching skills to agents. This is a decision issue, not a build issue.

## Dependencies

blocked_by: ["M0/GPT review of architecture and design decisions"]
blocks: ["M0/Lock project direction", "M1/Create agent YAML configs"]

## Why This Matters

Each Multica agent has a `skills` field. We need a strategy for populating it before E2E testing. Premature skill discovery wastes effort; no strategy means ad-hoc decisions.

## Options to Evaluate

### Option 1: Multica Built-in Discovery
Browse and import skills via Multica UI during agent creation.

### Option 2: Curated Allowlist
Maintain a YAML file mapping agent roles to recommended skills.

### Option 3: Defer Skills Entirely
Keep skills: [] for v1. Add when E2E testing reveals a need.

## Acceptance Criteria

- [ ] One option selected with documented rationale
- [ ] Decision recorded in knowledge/shared/decisions/
- [ ] Affected agent configs updated if necessary
```

### Research Issue

```markdown
## Goal

深入理解 Paladin 的整体架构设计，形成对项目全貌的认知。

## Dependencies

blocked_by: []
blocks: ["M1/Noto 域深入分析", "M1/Zeto 域深入分析", "M1/Pente 域深入分析", "M1/运行时核心组件分析"]

## Task Breakdown

### 1. 三层架构模型

* Layer A — Base EVM Ledger
* Layer B — Private TX Manager (Paladin Sidecar)
* Layer C — Private EVM (Pente)

### 2. 核心设计原则

* Pluggable Domain 架构
* Sidecar 模式：不修改底层 EVM 链
* UTXO 状态模型

### 3. 关键文件阅读清单

* README.md — 项目概述
* core/go/ — 核心运行时
* domains/ — 各隐私域实现

## Acceptance Criteria

- [ ] 架构总览文档完成
- [ ] 关键设计决策已记录
- [ ] 与后续 M2 集成分析的接口明确
```

---

## Anti-Patterns

Things to avoid when designing milestones and issues:

| Anti-Pattern | Why It's Bad | Do This Instead |
|---|---|---|
| Mega-issue covering 5+ tasks | Untrackable, hard to review | Split into focused issues |
| "TBD" or empty descriptions | Can't start working on it | Write enough detail to begin |
| All issues at same priority | Priority loses meaning | Differentiate by blocking impact |
| No `## Dependencies` section | Executors can't determine parallel order | Every issue gets `blocked_by` + `blocks`, even if empty |
| Sequential blocking by default | Kills parallelism — forces serial execution | Only block when there's a real data/artifact dependency |
| Title-only references after creation | Not machine-parseable, brittle | Backfill with issue IDs (WHI-3) after creation |
| Milestones without success criteria | Can't tell when it's done | Add concrete "done" definition |
| Adding scope not in the description | Scope creep | Decompose only what's there |
