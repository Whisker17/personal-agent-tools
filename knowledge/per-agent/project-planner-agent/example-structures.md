# Example Milestone & Issue Structures

last_updated: 2026-05-16

Reference examples from real projects showing the expected quality level for milestones and issues.

## Example 1: Research Project (Paladin Research)

### Milestone Structure

```
M1: Paladin 架构与核心概念研究
  Description: 深入理解 Paladin 的整体架构、核心设计理念、三大隐私域以及与 EVM 的交互模式。为后续集成分析打下理论基础。

M2: Mantle 架构分析与集成可行性评估
  Description: 分析 Mantle L2 架构，评估 Paladin 与 Mantle 集成的技术可行性，识别集成路径和潜在冲突。

M3: 集成方案设计与 PoC 验证
  Description: 设计具体的集成方案，进行 PoC 实验验证，输出最终技术推荐报告。

M4: Paladin Deep Dive — 企业级区块链技术深度解析
  Description: 从纯技术视角深度解析 Paladin 如何实现企业级区块链隐私方案。聚焦于设计哲学、核心机制、密码学实现和工程架构。
```

### Issue Examples (M1)

**Issue: Paladin 整体架构与设计理念研究**
- Priority: High
- Goal: 深入理解 Paladin 的整体架构设计，形成对项目全貌的认知。
- Includes: 三层架构模型分析、核心设计原则、关键文件阅读清单

**Issue: Noto（Notarized Tokens）域深入分析**
- Priority: Medium
- Goal: 深入研究 Noto 隐私域的设计与实现。
- Includes: 核心机制、适用场景、关键文件

**Issue: Paladin 本地环境搭建与运行验证**
- Priority: High
- Goal: 在本地搭建 Paladin 完整环境，实际运行并验证三大域的基本功能。
- Includes: 环境准备、本地网络启动、域功能验证 checklist

## Example 2: Engineering Project (自维护 agents 工具)

### Milestone Structure

```
M0: Project Setup & Design Review
  Description: Lock v1 positioning, align repo/docs/schema, run GPT review, add minimal validation, and decide the v1 skill-source posture.

M1: Research Pipeline (First Experiment)
  Description: Implement and validate the first Multica agent pair. Includes prompts, configs, fixtures, validator pass, Multica creation, E2E runs, and saved test artifacts.

M2: Knowledge Base & Scaling
  Description: Use M1 evidence to decide how to scale: knowledge base conventions, third agent selection, helper-script trigger conditions, and third-party skill safety.
```

### Issue Examples (M0)

**Issue: Define repo directory structure and create scaffolding**
- Priority: Urgent
- Milestone: M0

```markdown
## Goal

Establish the base directory structure for the repo. This scaffolding defines the separation of concerns.

## Directory Structure

(concrete directory tree with explanations)

## Acceptance Criteria

- [ ] All directories exist
- [ ] .gitkeep files in empty dirs
- [ ] No stale files from previous structure
```

**Issue: GPT review of architecture and design decisions**
- Priority: Urgent
- Milestone: M0
- Type: Decision/Review issue

```markdown
## Goal

Have GPT independently review the architecture and design decisions. The goal is adversarial: find blind spots, challenge assumptions, identify risks.

## Why This Matters

(justification for why this review is needed)

## Review Scope

(what to review, what to ignore)

## Deliverables

- Review document with findings categorized by severity
- Action items for each finding
```

## Example 3: Monitoring Project (Mantle AAVE Monitor)

### Milestone Structure

```
Phase 1: Hello World Pipeline
  Description: Prove the end-to-end pipeline works: RPC -> indexer -> TimescaleDB -> Grafana. Single event type, one panel, Docker Compose.

Phase 2: Full Event Indexer
  Description: Extend indexer to all 6 AAVE V3 event types, add backfill, reconnection/gap-fill, and the Event List Dashboard.

Phase 3: State Poller + Pool Dashboards
  Description: Add the State Poller service and build the Overview and Per-Pool dashboards.

Phase 4: Whale Monitor
  Description: Build the whale watchlist, position poller with Multicall3 batching, and the Whale Monitor Dashboard.

Phase 5: Oracle Health + Alerting
  Description: Build the Oracle Health Dashboard with TWAP deviation and staleness detection. Wire up Grafana alerting.
```

## Example 4: Deep Dive Series (within a milestone)

When a milestone contains a series of research threads, issues are numbered:

```
Deep Dive #1: 核心设计哲学 — 为什么不改 EVM？
Deep Dive #2: 隐私交易全生命周期 — 从 API 调用到链上落账
Deep Dive #3: UTXO 状态模型与分布式并发控制
Deep Dive #4: 零知识证明系统 — Zeto 的密码学全栈解析
...
Deep Dive #8: 综合评估 — 技术定位

综合文章大纲设计 (synthesis outline)
综合文章撰写 (final article)
```

## Key Patterns Summary

1. **Milestones are outcomes, not tasks** — "Prove the pipeline works" not "Write indexer code"
2. **Issues have rich structured descriptions** — Goal, Prerequisites, Task Breakdown, Acceptance Criteria
3. **Prerequisites create a clear execution order** — DAG of dependencies within and across milestones
4. **Priority reflects blocking impact** — Urgent/High for critical path, Medium/Low for depth/quality
5. **Language matches the project** — Chinese descriptions for Chinese projects, English for English
6. **Review/synthesis issues appear at milestone boundaries** — Retrospectives, design reviews, final reports
7. **Decision issues are explicit** — "Decide v1 skill source strategy" is its own issue, not buried in an implementation issue
