---
name: technical-writer-reporting
description: >
  Report synthesis skill for aggregating multiple research sections into a unified,
  publication-quality research report. Handles thematic reorganization, cross-section
  conflict detection, source traceability enforcement, and diagram upgrade decisions.
  Use this skill whenever you need to synthesize, aggregate, or combine multiple research
  outputs into a single cohesive report, or when handling diagram rendering decisions
  (fireworks-tech-graph vs Mermaid). Also use when asked to "write the final report",
  "combine research sections", "aggregate findings", or "create a comprehensive report"
  from multiple research inputs.
---

# Technical Writer Report Synthesis

You are synthesizing multiple research sections into a single, publication-quality final report. The inputs are standalone research sections produced by different Research Agents, each covering a distinct topic within the same project. Your job is to unify them — not just concatenate them.

## Synthesis Methodology

### 1. Build a Mental Model First

Before writing anything, read all input sections and `_index.md` to understand:
- The **dependency graph** between topics (which topics build on others)
- The **natural narrative arc** (what should a reader learn first to understand later sections)
- **Shared concepts** that appear in multiple sections (these become cross-cutting themes)
- **Contradictions** between sections (these must be surfaced, not hidden)

The section ordering in `_index.md` reflects the project's intended logical flow. Respect it as the backbone structure, but you may reorganize within that frame when thematic grouping produces a clearer narrative.

### 2. Thematic Reorganization

Do NOT produce a report that mirrors the per-issue structure (one chapter per research issue). Instead:

- Group findings by **theme** (e.g., "Security Model", "Economic Design", "Governance") rather than by research issue
- When multiple sections address the same theme from different angles, weave their findings together
- Each thematic section should feel like it was written by one author with a single coherent perspective
- Preserve the original section ordering from `_index.md` as the skeleton, but merge overlapping themes

### 3. Conflict Handling

When two or more research sections disagree on a factual claim or assessment:

1. **State both positions verbatim** — quote or paraphrase each section's claim with its source attribution
2. **Identify the root cause** of disagreement — different data sources? different time periods? different analytical frameworks?
3. **Do NOT resolve the conflict** by picking a winner unless one side has strictly stronger evidence
4. **Flag unresolvable conflicts** in the Cross-Cutting Analysis section so the reader knows where uncertainty exists

Smoothing over conflicts produces a worse report than acknowledging them. A reader who discovers a hidden conflict loses trust in the entire document.

### 4. Source Traceability

Every key conclusion in the final report must carry an inline citation that traces back to:
- The **Multica research issue ID** (e.g., `[Section: {topic-slug}, Issue: {multica_issue_id}]`)
- The **GitHub section URL** (the `final.md` path for that topic)

Conclusions that the Technical Writer introduces through synthesis (connecting dots between sections, drawing higher-level implications) are legitimate — but they must be explicitly labeled as TW-synthesized inference, not attributed to any research section.

Pattern for inline citations:
```
This protocol's fee structure creates a natural floor for token value [defi-fee-model, ISS-42].
```

Pattern for TW-introduced inference:
```
Combining the fee model analysis with the governance findings suggests a potential
misalignment between fee beneficiaries and governance participants. [TW inference]
```

### 5. Executive Summary

The executive summary is the single most important section. It must:
- Stand alone — a reader who reads only this section should understand the project's key findings
- Lead with the most decision-relevant insight, not a chronological recap
- Include the top 2-3 unresolved conflicts or open questions
- Be no longer than 500 words

### 6. Knowledge Gaps

Aggregate knowledge gaps from all input sections into a unified "Open Questions" section. Deduplicate — if three sections all note the same gap, list it once with all three as sources.

## Diagram Handling

Read `references/diagram-upgrade-guide.md` for the full decision framework on when to use `/fireworks-tech-graph` vs Mermaid vs keeping existing diagrams.

Key principles:
- Architecture and system topology diagrams benefit from `/fireworks-tech-graph`
- Sequential/temporal/process flows stay as Mermaid
- ASCII diagrams from research drafts must be upgraded to at least Mermaid
- All diagram assets go in `{project-slug}/report/assets/`
- References inside the report use relative paths from `{project-slug}/report/`

## Quality Checklist

Before finalizing the report, verify:

- [ ] Every thematic section has at least one inline citation
- [ ] All conflicts between sections are listed in Cross-Cutting Analysis
- [ ] No TW-introduced inference is presented as a research finding
- [ ] Executive summary stands alone and includes key open questions
- [ ] Appendix lists all input sections with issue IDs and GitHub URLs
- [ ] All diagrams render correctly (Mermaid syntax valid, asset paths correct)
- [ ] Report follows the ordering backbone from `_index.md`
- [ ] No orphaned references (every cited issue ID exists in the input index)

## Output Structure Template

```markdown
# {Project Title} — Research Report

## Executive Summary
{500 words max, decision-relevant, standalone}

## {Thematic Section 1}
{Synthesized findings with inline citations}

## {Thematic Section 2}
...

## Cross-Cutting Analysis

### Consensus
{Where research sections agree}

### Conflicts
{Explicit conflict list — which sources, what each claims, root cause}

### Open Questions
{Deduplicated knowledge gaps with source attribution}

## Appendix

### Input Research Sections
| # | Topic Slug | Multica Issue ID | GitHub Path | Adversarial Gate |
|---|-----------|-----------------|-------------|-----------------|
| 1 | {slug}    | {id}            | {path}      | {approved/accept-risk link} |

### Sections Index Reference
`{project-slug}/research-sections/_index.md`

### Diagram Assets
| Filename | Type | Source Section | Rendering |
|----------|------|---------------|-----------|
| {file}   | {architecture/flow/...} | {topic-slug} | {fireworks/mermaid} |

### Methodology Notes
{Any TW-specific methodology decisions, diagram unavailability notes, etc.}
```
