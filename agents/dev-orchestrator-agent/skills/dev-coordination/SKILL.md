---
name: dev-coordination
description: "Use when coordinating a Multica dev squad project: decomposing requirements into implementation tasks, maintaining the task ledger, dispatching Dev Engineer and Dev CC Reviewer, managing PR review/revision rounds, gating merges, tracking Multica status, and closing tasks through done gates."
---

# Dev Coordination

Coordinate the dev squad. Do not implement application code or write review verdicts yourself.

## Start Here

Read only the references needed for the current action:

- `references/dev-squad-protocol.md` - orchestrator-focused state machine, ledger schema, dispatch checklist, status transitions, and done gates.
- `references/squad-communication-protocol.md` - full dev squad protocol and complete message templates.

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
5. Route Implementation Ready comments to Dev CC Reviewer for persisted PR review.
6. Decide approve, request revision, accept risk, block, or escalate from Review Verdicts.
7. Merge approved PRs, delete remote task branches, verify the per-task done gate, clean worktrees, and update Multica status to Done.

Worker handoffs are continuous tasks: `Implementation Ready`, `Revision Complete`, and `Review Verdict` must mention Dev Orchestrator in `Target agent`, or Multica will not trigger the next orchestration run. On `/dev-resume`, `go on`, or a fresh mention, reconstruct state from issue comments and `multica issue runs`, then perform the next required action without waiting for another human prompt unless the task is blocked.

## Non-Negotiables

- Orchestrator is the only merge authority.
- Orchestrator is the only Multica issue status-transition authority.
- Engineer and Reviewer never coordinate directly.
- Every decision must be recoverable from issue comments plus the task ledger.
- Dispatches and continuous handoffs must contain exactly one `mention://agent/`; terminal comments use `Target agent: none`.
- Every dispatch Agent Directory must include Dev Orchestrator, Dev Engineer, and Dev CC Reviewer as bare UUIDs only.
- Do not dispatch two engineers to concurrently modify the same file without an explicit dependency or merge order.
- Before implementation or revision dispatch, run `git fetch --prune origin` and include `Base main SHA`.
- Do not accept an Engineer handoff unless its branch contains the reported base (`git merge-base --is-ancestor`) or the Engineer rebased onto `origin/main` and reran tests.
- After merge, run `git push origin --delete {branch}`, prune refs, remove the task worktree, and report `Remote branch deleted` before marking Done.
- If a required Multica or GitHub capability is missing, block or emit complete pending actions rather than improvising.
