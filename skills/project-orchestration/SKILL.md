---
name: project-orchestration
description: >
  Research squad orchestration engine for Multica projects. Dispatches agents through
  a planning → outline consensus → draft quality check → final promotion → TW report
  pipeline, managing run ledger state, _index.md serialization, and parallelism.
  Use whenever orchestrating a research project, dispatching agents, or coordinating
  multi-agent workflows.
---

# Project Orchestration Engine

This skill provides command entry points for the Orchestrator agent. The full workflow logic, state machine, run ledger schema, communication protocol, and error handling are defined in the system prompt — this skill supplies the operational commands and CLI reference.

## Commands

| Command | What it does |
|---------|-------------|
| `/orchestrate <project_id>` | Full orchestration flow: preflight → planning → research execution → final report |
| `/resume <project_id>` | Resume from the latest run ledger on the anchor issue |
| `/status <project_id>` | Show current orchestration status from run ledger |

## `/orchestrate` Flow

Executes the full pipeline defined in the system prompt:

1. **Anchor resolution** — Use `anchor_issue_id` if provided. If omitted, reuse an existing `[Orchestration] {project title}` issue when present; only create a new tracking issue when no existing anchor is available.
2. **Preflight** — Verify Multica capabilities, document on anchor issue
3. **Phase 1: Planning** — Read project, dispatch Planner, run quality gate
4. **Phase 2: Research Execution** — For each unblocked issue (max 5 parallel):
   - Phase 2A: Outline consensus (Research Agent → Adversarial review → Orchestrator decision)
   - Phase 2B: Deep draft + quality check (Research Agent → Adversarial review → Orchestrator decision)
   - Final promotion → `_index.md` serialization → TW handoff
5. **Phase 3: Final Report** — Dispatch Technical Writer, verify output, close project

All state transitions, dispatch decisions, and risk assessments follow the system prompt rules. The run ledger (posted as JSON on the anchor issue) is the source of truth.

## `/resume` Flow

1. Resolve the anchor issue using the system prompt rules: explicit `anchor_issue_id` first, otherwise the existing `[Orchestration] {project title}` issue with the newest ledger.
2. Read the latest run ledger JSON from the anchor issue comments.
3. For each issue in the ledger:
   - `done` → skip
   - `blocked` → check if blocker resolved, unblock if so
   - Any in-progress phase → check task status via `multica task status`, pick up where left off
   - `planned` → queue for dispatch if unblocked and within parallelism cap
4. Continue the dispatch loop from current state.

## `/status` Flow

1. Resolve the anchor issue using the system prompt rules.
2. Read the latest run ledger from the anchor issue.
3. Produce a summary table:
   ```
   Issue          Topic Slug       Phase                  Round  Agent
   -----------    ---------------  ---------------------  -----  ------
   <issue_id>     <topic-slug>     <phase>                <n>    <agent>
   ```
4. Report: total issues, in-progress count, done count, blocked count, next actions.

## Multica CLI Quick Reference

| Operation | Command |
|-----------|---------|
| Read project | `multica project get <id>` |
| List issues | `multica project issues <id>` |
| Get issue details | `multica issue get <id>` |
| Create issue | `multica issue create --project <id> --title "..." --description "..."` |
| Update issue status | `multica issue status <id> "<status>"` |
| Add issue comment | `multica issue comment add <id> --content "..."` |
| List issue comments | `multica issue comments <id>` |
| Add emoji reaction | `multica issue comment react <comment-id> --emoji "<emoji>"` |
| Create task | `multica task create --agent <name> --param k=v` |
| Check task | `multica task status <task-id>` |
| Get task output | `multica task output <task-id>` |

## Agent Dispatch Parameters

### project-planner-agent

```bash
multica task create \
  --agent project-planner-agent \
  --param project_id="<project_id>" \
  --param project_description="<description>" \
  --param github_repo="Whisker17/multica-research" \
  --param orchestrator_context="<anchor issue context>" \
  --param research_depth="<quick-scan|standard|deep-dive>" \
  --param project_slug="<optional>"
```

### research-agent (outline)

```bash
multica task create \
  --agent research-agent \
  --param multica_issue_id="<issue-id>" \
  --param topic="<title>" \
  --param scope="<scope>" \
  --param expected_output="<expected_output>" \
  --param project_slug="<project-slug>" \
  --param topic_slug="<topic-slug>" \
  --param report_issue_id="<tw-issue-id>" \
  --param github_repo="Whisker17/multica-research" \
  --param round="<n>"
```

### research-agent (deep draft)

```bash
multica task create \
  --agent research-agent \
  --param multica_issue_id="<issue-id>" \
  --param topic="<title>" \
  --param project_slug="<project-slug>" \
  --param topic_slug="<topic-slug>" \
  --param report_issue_id="<tw-issue-id>" \
  --param github_repo="Whisker17/multica-research" \
  --param outline_path="{project-slug}/outlines/{topic-slug}.md" \
  --param round="<n>"
```

### research-agent (final promotion)

```bash
multica task create \
  --agent research-agent \
  --param multica_issue_id="<issue-id>" \
  --param promote="true" \
  --param topic="<title>" \
  --param project_slug="<project-slug>" \
  --param topic_slug="<topic-slug>" \
  --param round="<n>" \
  --param report_issue_id="<tw-issue-id>" \
  --param github_repo="Whisker17/multica-research" \
  --param approved_draft_path="<draft-path>" \
  --param approved_draft_round="<n>" \
  --param approved_draft_commit="<commit>" \
  --param approval_evidence="<link>" \
  --param order="<order>" \
  --param dependencies="<upstream-slugs-or-dash>"
```

### research-agent (TW handoff)

```bash
multica task create \
  --agent research-agent \
  --param multica_issue_id="<issue-id>" \
  --param project_slug="<project-slug>" \
  --param topic_slug="<topic-slug>" \
  --param report_issue_id="<tw-issue-id>" \
  --param github_repo="Whisker17/multica-research" \
  --param final_commit="<commit>" \
  --param sections_index_commit="<index-commit>" \
  --param approved_draft_path="<reviewed-draft-path>" \
  --param approved_draft_commit="<reviewed-draft-commit>" \
  --param outline_rounds="<total>" \
  --param deep_rounds="<total>" \
  --param round="<deep-round>" \
  --param order="<order>" \
  --param approval_evidence="<link>"
```

### research-adversarial-agent

```bash
multica task create \
  --agent research-adversarial-agent \
  --param multica_issue_id="<issue-id>" \
  --param review_type="<outline|draft>" \
  --param artifact_path="<path>" \
  --param artifact_commit="<commit>" \
  --param project_slug="<project-slug>" \
  --param topic_slug="<topic-slug>" \
  --param github_repo="Whisker17/multica-research" \
  --param round="<n>"
```

### technical-writer-agent

```bash
multica task create \
  --agent technical-writer-agent \
  --param project_id="<project_id>" \
  --param report_issue_id="<tw-issue-id>" \
  --param project_slug="<project-slug>" \
  --param github_repo="Whisker17/multica-research"
```
