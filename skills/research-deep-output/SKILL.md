---
name: research-deep-output
description: "Use when producing a persisted research section draft from an approved outline, revising a draft from adversarial feedback, promoting an approved draft to final.md, or preparing Research Agent handoff data for the squad protocol."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
---

# Research Deep Output

Produce persisted research section artifacts. This skill owns Phase B draft generation, revision, and final promotion.

## References

Load as needed:

- `references/deep-output-workflow.md` — modes, draft structure, persistence, promotion, quality gates, and errors.
- `references/research-outline-schema.md` — outline schema.
- `references/research-methodology.md` — source hierarchy and integrity rules.
- `references/squad-communication-protocol.md` — message templates and handoff boundaries.

## Inputs

Required for draft mode: `outline_path` or `outline_content`, `topic`, `project_slug`, `topic_slug`, `round`, and artifact paths from the outline.

Optional: `github_repo`, `codebase_path`, `adversarial_feedback`.

Required for promotion mode: `promote: true`, `approved_draft_path`, `approved_draft_round`, `approved_draft_commit`, `approval_evidence`, `multica_issue_id`, `order`, and `dependencies`.

## Rules

- Never draft from a candidate outline; status must be approved.
- Persist drafts before review.
- Revision mode targets flagged issues; do not restart unless instructed.
- Promotion performs file promotion and metadata assembly only; no new research.
- Never write `_index.md`.
- Never post or imply Research Complete before Orchestrator provides the `_index.md` commit.
