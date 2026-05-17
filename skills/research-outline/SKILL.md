---
name: research-outline
description: >
  Use when creating or revising a structured research outline, breaking a topic into researchable
  items, defining investigation fields, planning diagrams, source requirements, and persisted
  outline artifacts for the research squad.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
---

# Research Outline

Generate a persisted structured outline for systematic research.

## References

Load as needed:

- `references/outline-workflow.md` — topic analysis, item/field/diagram design, persistence, quality checklist, and errors.
- `references/research-outline-schema.md` — required outline format.
- `references/research-methodology.md` — source hierarchy and integrity principles.
- `references/squad-communication-protocol.md` — squad handoff templates.

## Required Inputs

`topic`, `project_slug`, and `topic_slug`.

Optional inputs include `github_repo`, `artifact_paths`, `scope`, `audience`, `expected_output`, `source_requirements`, `diagram_expectations`, and `codebase_path`.

## Rules

- Persist the outline before review.
- Use stable human-readable slugs; never use Linear IDs as `topic_slug`.
- Make outlines independently reviewable by an adversarial agent.
- Do not skip source requirements or diagram expectations unless the topic makes them genuinely unnecessary and you say why.
