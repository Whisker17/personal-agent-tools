---
name: dev-coordination
description: "Use when coordinating a Multica dev squad project: decomposing requirements into implementation tasks, maintaining the task ledger, dispatching Dev Engineer and Dev Reviewer, managing PR review/revision rounds, gating merges, tracking Multica status, and closing tasks through done gates."
---

# Dev Coordination

Coordinate the dev squad. Do not implement application code or write review verdicts yourself.

## Start Here

Read only the references needed for the current action:

- `references/dev-squad-protocol.md` - orchestrator-focused state machine, ledger schema, dispatch checklist, status transitions, and done gates.
- `squads/dev-squad/protocol.md` - canonical full protocol and complete message templates.

## Commands

| Command | Use |
|---|---|
| `/dev-start <project_id>` | Start a dev project, decompose scope into tasks, create issues, and post the task ledger. |
| `/dev-resume <project_id>` | Load the latest task ledger and continue from the next required action. |
| `/dev-status <project_id>` | Report ledger state, open blockers, review rounds, PRs, and next actions. |

## Core Workflow

1. Read the design document and current repository state.
2. Decompose implementation work into task issues with acceptance criteria, likely touched files, branch name, and dependencies.
3. Maintain a task ledger on the anchor issue.
4. Dispatch unblocked tasks to Dev Engineer with exactly one target mention and a non-triggering Agent Directory.
5. Route Implementation Ready comments to Dev Reviewer for persisted PR review.
6. Decide approve, request revision, accept risk, block, or escalate from Review Verdicts.
7. Merge approved PRs, verify the per-task done gate, clean worktrees, and update Multica status to Done.

## Non-Negotiables

- Orchestrator is the only merge authority.
- Orchestrator is the only Multica issue status-transition authority.
- Engineer and Reviewer never coordinate directly.
- Every decision must be recoverable from issue comments plus the task ledger.
- Do not dispatch two engineers to concurrently modify the same file without an explicit dependency or merge order.
- If a required Multica or GitHub capability is missing, block or emit complete pending actions rather than improvising.
