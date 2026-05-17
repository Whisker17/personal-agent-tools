---
name: project-planner
description: >
  Use when decomposing a Multica research project into issues, stable slugs, artifact paths,
  dependency waves, agent assignment labels, a Technical Writer reserved issue, or a Planner
  completion notification.
---

# Project Planner

Create the project issue structure that downstream agents can execute without reading the planner's prompt.

## References

Load references only when needed:

- `references/squad-communication-protocol.md` — required message and artifact handoff contract.
- `references/planning-workflow.md` — planning steps, required issue sections, wave rules, TW issue contract, and CLI notes.
- `references/design-patterns.md` — issue structure patterns and acceptance criteria examples.
- `references/example-structures.md` — full research-squad planning examples.

## Workflow

1. Read the Multica project and project description.
2. Resolve `github_repo` or default to `Whisker17/multica-research`; verify write access.
3. Derive `project_slug` and one stable `topic_slug` per research issue.
4. Design research issues with full artifact paths and handoff contracts.
5. Group issues into parallel waves with real dependency edges.
6. Create exactly one Technical Writer reserved issue.
7. Present the plan for approval before creating issues.
8. Create labels, issues, dependencies, and the Planner completion notification through Multica CLI.

## Required Outputs

- Research issues with Goal, Scope, Out of Scope, Key Questions, Evidence, Diagram Expectations, Artifact Paths, Dependencies, Done Criteria, Agent Assignment, and handoff formats.
- A TW reserved issue containing the section index, final report target, trigger condition, and completion format.
- A Planner Complete comment on the Orchestrator issue with created IDs, slugs, waves, paths, and risks.

## Rules

- Do not invent requirements not supported by the project description.
- Use agent labels as the primary routing mechanism; include `agent_role:` fallback when labels fail.
- Use `--description-file` for multi-line Multica issue content.
- Never use Linear `WHI-*` IDs as runtime artifact slugs.
- Match the project language.
