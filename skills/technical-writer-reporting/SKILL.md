---
name: technical-writer-reporting
description: >
  Use when synthesizing completed research sections into a final report, validating upstream
  Research Complete handoffs, preserving source traceability, handling cross-section conflicts,
  deciding diagram rendering, or posting Final Report Ready.
---

# Technical Writer Reporting

Synthesize completed research sections into a final report. Do not perform new research.

## References

Load as needed:

- `references/reporting-workflow.md` — preflight, synthesis process, output paths, and completion behavior.
- `references/diagram-upgrade-guide.md` — diagram rendering decisions.
- `references/research-methodology.md` — source and integrity principles.
- `references/squad-communication-protocol.md` — message templates and fallback payloads.

## Core Rules

- Validate upstream completion before synthesis.
- Organize by theme, not by issue.
- Surface conflicts instead of smoothing them over.
- Every key conclusion needs traceability to a research issue and GitHub section path.
- Mark TW-added conclusions as `[TW inference]`.
- Write only to `{project_slug}/report/final-report.md` and `{project_slug}/report/assets/`.
- Report blockers to Orchestrator, never directly to Research Agent.
