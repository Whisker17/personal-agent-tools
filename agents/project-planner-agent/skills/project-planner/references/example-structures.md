# Example Structures for Research Squad Planning

last_updated: 2026-05-17

Reference examples showing the expected quality level for Planner output in the research squad workflow. Covers input schema, research issue templates, parallel waves, TW reserved issue, and completion notification.

## Example 1: Planner Input

```yaml
project_id: "proj_abc123"
project_description: |
  深入研究 Paladin 隐私框架的技术架构，评估其与 Mantle L2 的集成可行性，
  设计集成方案并进行 PoC 验证。输出一份完整的技术研究报告。
github_repo: "Whisker17/multica-research"
orchestrator_context: "Dispatched from project kickoff issue #MULTICA-42"
research_depth: "deep-dive"
project_slug: ""  # empty — Planner derives it
```

Derived `project_slug`: `paladin-mantle-integration` (from project title, lowercase, hyphen-separated, no Linear IDs).

## Example 2: Research Issue (Full Template)

```markdown
# Paladin 整体架构与设计理念研究

## Goal

深入理解 Paladin 的整体架构设计，形成对项目全貌的认知，为后续集成分析打下理论基础。

## Research Scope

- 三层架构模型分析（Base EVM Ledger / Private TX Manager / Private EVM）
- 核心设计原则（Pluggable Domain、Sidecar 模式、UTXO 状态模型）
- 关键源代码文件阅读（README, core/go/, domains/）

## Out of Scope

- Mantle 集成可行性（covered by separate issue）
- PoC 实现（Phase 3）
- 性能基准测试

## Key Questions

1. Paladin 的三层架构如何协作处理一笔隐私交易？
2. Pluggable Domain 架构的扩展边界在哪里？
3. Sidecar 模式对底层 EVM 链的兼容性要求是什么？

## Expected Output

- 架构概览文档，包含三层架构的详细分析
- 核心设计决策记录
- 与后续集成分析的接口说明
- Evidence: 至少引用 3 个 primary sources（官方文档/源码/白皮书）

## Required Evidence / Sources

1. Primary: Paladin 官方文档、GitHub 源码、白皮书
2. Expert: Kaleido 团队的技术博客和演讲
3. Secondary: 社区讨论、第三方分析

## Diagram Expectations

- Paladin 三层架构总览图（Mermaid）
- 隐私交易生命周期序列图（Mermaid）
- Pluggable Domain 组件关系图（Mermaid）

## Artifact Paths

- **Project slug**: `paladin-mantle-integration`
- **Topic slug**: `paladin-architecture`
- **Branch**: `research/paladin-mantle-integration/paladin-architecture`
- **Order**: 1
- **Outline path**: `paladin-mantle-integration/outlines/paladin-architecture.md`
- **Draft persistence path**: `paladin-mantle-integration/research-sections/paladin-architecture/drafts/round-{n}.md`
- **Final persistence path**: `paladin-mantle-integration/research-sections/paladin-architecture/final.md`
- **Sections index path**: `paladin-mantle-integration/research-sections/_index.md`

## Artifact and Handoff Contract

Outline artifact:
  paladin-mantle-integration/outlines/paladin-architecture.md
  - written on branch `research/paladin-mantle-integration/paladin-architecture`
  - written before drafting begins
  - Phase A candidate until Orchestrator approves by state transition
  - may be revised across rounds; commit history preserves rounds

Draft artifacts:
  paladin-mantle-integration/research-sections/paladin-architecture/drafts/round-{n}.md
  - written on branch `research/paladin-mantle-integration/paladin-architecture`
  - written every Phase B round before adversarial review
  - includes branch commit URL/SHA in Artifact Ready comment
  - reviewed by Adversarial Agent

Final research section:
  paladin-mantle-integration/research-sections/paladin-architecture/final.md
  - written on branch `research/paladin-mantle-integration/paladin-architecture`
  - written only after Adversarial approve or Orchestrator accept-risk
  - followed by Final Promotion Ready on the research issue

Sections index:
  paladin-mantle-integration/research-sections/_index.md
  - aggregate index of all research sections in the project
  - written exclusively by Orchestrator during selective main integration
  - Research Agent provides Index Entry Proposal in Final Promotion Ready
  - Research Complete to TW happens only after Orchestrator returns `main_merge_commit`

## Dependencies

blocked_by: []
blocks: ["MULTICA-45/noto-domain-analysis", "MULTICA-46/zeto-domain-analysis", "MULTICA-47/pente-domain-analysis", "MULTICA-48/runtime-core-components"]

## Done Criteria

- [ ] Outline persisted and approved (or revised until consensus)
- [ ] At least one draft persisted before adversarial review
- [ ] Draft branch commit URL/SHA recorded
- [ ] Adversarial Agent approval or Orchestrator accept-risk posted
- [ ] No unresolved critical findings
- [ ] Final section persisted on branch at paladin-mantle-integration/research-sections/paladin-architecture/final.md
- [ ] Final Promotion Ready posted with Index Entry Proposal
- [ ] Orchestrator integrated allowlisted research package (outline, draft rounds, final) and _index.md to main in one commit
- [ ] Remote work branch deleted after main push
- [ ] Research Complete posted on TW issue after `main_merge_commit`

## Agent Assignment

label: `agent:research-agent`
agent_role: research-agent

## Final Promotion Ready Format

## Final Promotion Ready: Paladin 整体架构与设计理念研究

**Issue**: MULTICA-44
**Project slug**: paladin-mantle-integration
**Topic slug**: paladin-architecture
**Branch**: research/paladin-mantle-integration/paladin-architecture
**Reviewed draft**: paladin-mantle-integration/research-sections/paladin-architecture/drafts/round-2.md
**Reviewed draft branch commit/URL**: abc1234
**Final section**: paladin-mantle-integration/research-sections/paladin-architecture/final.md
**Final branch commit/URL**: bcd2345
**Adversarial approval or accept-risk**: {link to approval comment}

**Index Entry Proposal**:
| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|-----------|-----------------|------------|--------------|--------|
| 1 | paladin-architecture | MULTICA-44 | paladin-mantle-integration/research-sections/paladin-architecture/final.md | - | done |

**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator validates proposal, integrates allowlisted research package (outline, draft rounds, final) and _index.md to main, deletes branch, then dispatches TW handoff

## TW Research Complete Format

## Research Complete: Paladin 整体架构与设计理念研究

**Issue**: MULTICA-44
**Project slug**: paladin-mantle-integration
**Topic slug**: paladin-architecture
**Branch**: research/paladin-mantle-integration/paladin-architecture
**Summary**: 完成了 Paladin 三层架构分析，记录了核心设计决策，明确了与 Mantle 集成的接口要求。
**Draft reviewed**: paladin-mantle-integration/research-sections/paladin-architecture/drafts/round-2.md
**Draft reviewed branch commit/URL**: abc1234
**Final section**: paladin-mantle-integration/research-sections/paladin-architecture/final.md
**Final branch commit/URL**: bcd2345
**Sections index**: paladin-mantle-integration/research-sections/_index.md
**Main integration commit/URL**: def5678
**Adversarial approval or accept-risk**: {link}
**Round count**: outline rounds=1, deep rounds=2
**Key findings**:
- Paladin 采用 Sidecar 架构，不修改底层 EVM 链
- 三大隐私域通过 Pluggable Domain 接口实现可扩展性
- UTXO 状态模型是并发隐私交易的核心基础

Target agent: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
```

## Example 3: Parallel Waves Output

```
Project: Paladin 隐私框架与 Mantle L2 集成可行性研究
Project slug: paladin-mantle-integration
Type: research
Research issues: 8
Waves: 4

━━━ Wave 1 (parallel, no blockers) ━━━
  1. [order=1] Paladin 整体架构与设计理念研究     topic_slug: paladin-architecture
  2. [order=5] Mantle L2 架构梳理与差异分析       topic_slug: mantle-architecture
  3. [order=2] Paladin 本地环境搭建与运行验证     topic_slug: paladin-local-setup

━━━ Wave 2 (blocked by Wave 1 completions) ━━━
  4. [order=3] Noto 域深入分析                     topic_slug: noto-domain  ← blocked_by: #1
  5. [order=4] Zeto 域深入分析                     topic_slug: zeto-domain  ← blocked_by: #1
  6. [order=6] EVM 兼容性需求 vs Mantle 差异分析   topic_slug: evm-compatibility  ← blocked_by: #1, #2

━━━ Wave 3 (blocked by Wave 2 completions) ━━━
  7. [order=7] 集成路径识别与对比分析             topic_slug: integration-paths  ← blocked_by: #4, #5, #6

━━━ Wave 4 (blocked by Wave 3 completions) ━━━
  8. [order=8] 最终技术方案与推荐报告             topic_slug: final-recommendation  ← blocked_by: #7

━━━ TW Reserved Issue ━━━
  9. [TW] Final Report Synthesis                   ← blocked_by: #1, #2, #3, #4, #5, #6, #7, #8

Block graph edges:
  #1 → #4, #5, #6
  #2 → #6
  #4 → #7
  #5 → #7
  #6 → #7
  #7 → #8

Real dependencies vs ordering preferences:
  Real: #1 → #4 (Noto analysis needs Paladin architecture understanding)
  Real: #1 → #5 (Zeto analysis needs Paladin architecture understanding)
  Real: #1, #2 → #6 (compatibility analysis needs both architectures)
  Real: #4, #5, #6 → #7 (integration paths need domain + compatibility analysis)
  Real: #7 → #8 (final recommendation needs integration path analysis)
  Preference only: order=1 before order=2 (Paladin and Mantle are independent research topics)
  Preference only: order=3 before order=4 (Noto and Zeto are independent domains)
```

## Example 4: TW Reserved Issue

```markdown
# Final Report Synthesis: Paladin 隐私框架与 Mantle L2 集成可行性研究

## Goal

Aggregate all completed research sections into a single coherent project report covering Paladin architecture, domain analysis, Mantle integration feasibility, and final recommendations.

## Research Section Index

| Order | Multica Issue ID | Topic Slug | Outline Path | Draft Path Convention | Final Path |
|-------|-----------------|------------|--------------|----------------------|------------|
| 1 | MULTICA-44 | paladin-architecture | paladin-mantle-integration/outlines/paladin-architecture.md | paladin-mantle-integration/research-sections/paladin-architecture/drafts/round-{n}.md | paladin-mantle-integration/research-sections/paladin-architecture/final.md |
| 2 | MULTICA-46 | paladin-local-setup | paladin-mantle-integration/outlines/paladin-local-setup.md | paladin-mantle-integration/research-sections/paladin-local-setup/drafts/round-{n}.md | paladin-mantle-integration/research-sections/paladin-local-setup/final.md |
| 3 | MULTICA-47 | noto-domain | paladin-mantle-integration/outlines/noto-domain.md | paladin-mantle-integration/research-sections/noto-domain/drafts/round-{n}.md | paladin-mantle-integration/research-sections/noto-domain/final.md |
| 4 | MULTICA-48 | zeto-domain | paladin-mantle-integration/outlines/zeto-domain.md | paladin-mantle-integration/research-sections/zeto-domain/drafts/round-{n}.md | paladin-mantle-integration/research-sections/zeto-domain/final.md |
| 5 | MULTICA-45 | mantle-architecture | paladin-mantle-integration/outlines/mantle-architecture.md | paladin-mantle-integration/research-sections/mantle-architecture/drafts/round-{n}.md | paladin-mantle-integration/research-sections/mantle-architecture/final.md |
| 6 | MULTICA-49 | evm-compatibility | paladin-mantle-integration/outlines/evm-compatibility.md | paladin-mantle-integration/research-sections/evm-compatibility/drafts/round-{n}.md | paladin-mantle-integration/research-sections/evm-compatibility/final.md |
| 7 | MULTICA-50 | integration-paths | paladin-mantle-integration/outlines/integration-paths.md | paladin-mantle-integration/research-sections/integration-paths/drafts/round-{n}.md | paladin-mantle-integration/research-sections/integration-paths/final.md |
| 8 | MULTICA-51 | final-recommendation | paladin-mantle-integration/outlines/final-recommendation.md | paladin-mantle-integration/research-sections/final-recommendation/drafts/round-{n}.md | paladin-mantle-integration/research-sections/final-recommendation/final.md |

## Project Context

- **GitHub repo**: Whisker17/multica-research
- **Project slug**: paladin-mantle-integration
- **Sections index**: paladin-mantle-integration/research-sections/_index.md (Orchestrator-owned; written during main integration)
- **Final report target path**: paladin-mantle-integration/report/final-report.md
- **Diagram asset target path**: paladin-mantle-integration/report/assets/
- **Final report branch**: research/paladin-mantle-integration/final-report

## Trigger Condition

Begin only after ALL listed research issues have Research Complete comments posted on this issue with `main_merge_commit` references.

## TW Research Complete Format

Each Research Agent completion posts a comment on this issue in this format:

(see Research Complete template in `squad-communication-protocol.md`)

## Completion Format

## Final Report Ready

**Issue**: {multica_tw_issue_id}
**Project slug**: paladin-mantle-integration
**Topic slug**: final-report
**Branch**: research/paladin-mantle-integration/final-report
**Phase**: final-report
**Round**: 1
**Final report path**: paladin-mantle-integration/report/final-report.md
**Final report branch commit/URL**: {commit hash or permalink}
**Diagram assets path**: paladin-mantle-integration/report/assets/
**Diagram assets branch commit/URL**: {commit hash or permalink}
**Source sections aggregated**: MULTICA-44, MULTICA-45, MULTICA-46, MULTICA-47, MULTICA-48, MULTICA-49, MULTICA-50, MULTICA-51
**Sections index**: paladin-mantle-integration/research-sections/_index.md
**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator integrates final report to main, deletes branch, verifies, and closes project

## Orchestrator-Only Dispatch Note

This issue is dispatched exclusively by Orchestrator. Technical Writer must not begin work until Orchestrator explicitly dispatches it after all research sections are complete.

## Dependencies

blocked_by: ["MULTICA-44", "MULTICA-45", "MULTICA-46", "MULTICA-47", "MULTICA-48", "MULTICA-49", "MULTICA-50", "MULTICA-51"]
blocks: []

## Agent Assignment

label: `agent:technical-writer-agent`
agent_role: technical-writer-agent
```

## Example 5: Planner Completion Notification

```markdown
## Planner Complete

**Project**: Paladin 隐私框架与 Mantle L2 集成可行性研究
**Project slug**: paladin-mantle-integration
**Project slug derivation**: Lowercase hyphenated from project title keywords "Paladin" + "Mantle" + "Integration"
**GitHub repo**: Whisker17/multica-research

### Created Issues

| # | Multica ID | Title | Topic Slug | Order | Wave |
|---|-----------|-------|------------|-------|------|
| 1 | MULTICA-44 | Paladin 整体架构与设计理念研究 | paladin-architecture | 1 | 1 |
| 2 | MULTICA-45 | Mantle L2 架构梳理与差异分析 | mantle-architecture | 5 | 1 |
| 3 | MULTICA-46 | Paladin 本地环境搭建与运行验证 | paladin-local-setup | 2 | 1 |
| 4 | MULTICA-47 | Noto 域深入分析 | noto-domain | 3 | 2 |
| 5 | MULTICA-48 | Zeto 域深入分析 | zeto-domain | 4 | 2 |
| 6 | MULTICA-49 | EVM 兼容性需求 vs Mantle 差异分析 | evm-compatibility | 6 | 2 |
| 7 | MULTICA-50 | 集成路径识别与对比分析 | integration-paths | 7 | 3 |
| 8 | MULTICA-51 | 最终技术方案与推荐报告 | final-recommendation | 8 | 4 |

### Artifact Paths

| Topic Slug | Outline | Draft Convention | Final |
|-----------|---------|-----------------|-------|
| paladin-architecture | paladin-mantle-integration/outlines/paladin-architecture.md | paladin-mantle-integration/research-sections/paladin-architecture/drafts/round-{n}.md | paladin-mantle-integration/research-sections/paladin-architecture/final.md |
| mantle-architecture | paladin-mantle-integration/outlines/mantle-architecture.md | paladin-mantle-integration/research-sections/mantle-architecture/drafts/round-{n}.md | paladin-mantle-integration/research-sections/mantle-architecture/final.md |
| paladin-local-setup | paladin-mantle-integration/outlines/paladin-local-setup.md | paladin-mantle-integration/research-sections/paladin-local-setup/drafts/round-{n}.md | paladin-mantle-integration/research-sections/paladin-local-setup/final.md |
| noto-domain | paladin-mantle-integration/outlines/noto-domain.md | paladin-mantle-integration/research-sections/noto-domain/drafts/round-{n}.md | paladin-mantle-integration/research-sections/noto-domain/final.md |
| zeto-domain | paladin-mantle-integration/outlines/zeto-domain.md | paladin-mantle-integration/research-sections/zeto-domain/drafts/round-{n}.md | paladin-mantle-integration/research-sections/zeto-domain/final.md |
| evm-compatibility | paladin-mantle-integration/outlines/evm-compatibility.md | paladin-mantle-integration/research-sections/evm-compatibility/drafts/round-{n}.md | paladin-mantle-integration/research-sections/evm-compatibility/final.md |
| integration-paths | paladin-mantle-integration/outlines/integration-paths.md | paladin-mantle-integration/research-sections/integration-paths/drafts/round-{n}.md | paladin-mantle-integration/research-sections/integration-paths/final.md |
| final-recommendation | paladin-mantle-integration/outlines/final-recommendation.md | paladin-mantle-integration/research-sections/final-recommendation/drafts/round-{n}.md | paladin-mantle-integration/research-sections/final-recommendation/final.md |

**Sections index**: paladin-mantle-integration/research-sections/_index.md
**Final report path**: paladin-mantle-integration/report/final-report.md
**Diagram assets path**: paladin-mantle-integration/report/assets/

### Parallel Waves

Wave 1 (3 issues, parallel): #1 paladin-architecture, #2 mantle-architecture, #3 paladin-local-setup
Wave 2 (3 issues, parallel): #4 noto-domain, #5 zeto-domain, #6 evm-compatibility
Wave 3 (1 issue): #7 integration-paths
Wave 4 (1 issue): #8 final-recommendation

### Block Graph

#1 → #4, #5, #6
#2 → #6
#4, #5, #6 → #7
#7 → #8

### TW Reserved Issue

**Multica ID**: MULTICA-52
**Blocked by**: MULTICA-44, MULTICA-45, MULTICA-46, MULTICA-47, MULTICA-48, MULTICA-49, MULTICA-50, MULTICA-51

### Risks / Ambiguities

- Paladin 本地环境搭建可能需要特定版本的 Go 和 Node.js，需要验证环境依赖
- 如果 Paladin 文档不完整，UTXO 模型分析可能需要深入源码阅读

Target agent: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
```

## Example 6: Dependency Graph (Engineering Project — Legacy Reference)

Showing how `## Dependencies` sections map across an engineering project. This pattern still applies but research projects use the enriched template above.

```
M0: Project Setup & Design Review
  #1 [urgent] Define repo directory structure
      blocked_by: []
      blocks: [M0/#4, M0/#8]

  #2 [urgent] Review and harden CLAUDE.md
      blocked_by: []
      blocks: [M0/#7]

  #3 [urgent] Review and harden README.md and AGENTS.md
      blocked_by: []
      blocks: [M0/#7]

  #4 [high]   Standardize agent init config YAML schema
      blocked_by: [M0/#1]
      blocks: [M0/#8, M1/#4]

  #5 [urgent] GPT review of architecture and design decisions
      blocked_by: []
      blocks: [M0/#6, M0/#7]

  #6 [high]   Decide v1 skill source strategy
      blocked_by: [M0/#5]
      blocks: [M0/#7, M1/#4]

  #7 [urgent] Lock project direction and update design references
      blocked_by: [M0/#2, M0/#3, M0/#5, M0/#6]
      blocks: [M1/#1, M1/#2]

  #8 [high]   Add minimal config validator
      blocked_by: [M0/#1, M0/#4]
      blocks: [M1/#4]

Parallelizable entry points: M0/#1, M0/#2, M0/#3, M0/#5, M1/#3
Critical path: M0/#5 → M0/#6 → M0/#7 → M1/#1 → M1/#4 → M1/#5 → M2/#1
```

## Key Patterns Summary

1. **Research issues use the full template** — Goal, Research Scope, Out of Scope, Key Questions, Expected Output, Required Evidence, Diagram Expectations, Artifact Paths, Artifact and Handoff Contract, Dependencies, Done Criteria, Agent Assignment, Final Promotion Ready Format, TW Research Complete Format
2. **Stable slugs identify all artifacts** — `project_slug` namespaces the project; `topic_slug` identifies each research section; neither uses Linear `WHI-*` IDs
3. **Parallel waves group concurrent work** — max 5 issues per wave; waves start only when upstream dependencies are Done
4. **Real dependencies vs ordering preferences** — only block when there's an actual data/artifact dependency; reading order is captured in `order` field independently
5. **Deterministic order** — `order` values reflect final report reading sequence, not execution order
6. **TW reserved issue aggregates all context** — research section index, paths, trigger condition, completion format, Orchestrator-only dispatch
7. **Agent assignment via labels** — `agent:research-agent`, `agent:technical-writer-agent`; fallback `agent_role:` in description
8. **Completion notification is comprehensive** — created issues, slugs, paths, waves, block graph, TW issue, risks
9. **`_index.md` is Orchestrator-owned** — Research Agent proposes entries; Orchestrator serializes writes
10. **Drafts are persisted before review** — adversarial review operates on persisted artifacts with commit references, not ephemeral text
