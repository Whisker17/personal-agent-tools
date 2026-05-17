---
name: project-orchestration
description: "Use when coordinating a Multica research squad project, dispatching planner/research/review/TW agents, resuming orchestration, managing a run ledger, serializing _index.md writes, or deciding approve/revise/accept-risk/block transitions."
---

# Project Orchestration

Coordinate the research squad. Do not perform worker-agent tasks yourself.

## Start Here

Read only the references needed for the current action:

- `references/squad-communication-protocol.md` — state machine, message templates, done gates, risk escalation, and `_index.md` ownership.
- `references/orchestration-workflow.md` — preflight, ledger schema, dispatch flow, dispatch parameters, and serialization rules.
- `references/research-outline-schema.md` — outline schema when validating Planner/Research artifacts.

## Commands

| Command | Use |
|---|---|
| `/orchestrate <project_id>` | Start or continue the full project flow. |
| `/resume <project_id>` | Load the latest run ledger and continue. |
| `/status <project_id>` | Report current ledger state and next actions. |

## Core Workflow

1. Resolve or create the orchestration anchor issue.
2. Run Multica/GitHub capability preflight.
3. Dispatch `project-planner-agent`; validate the returned plan.
4. Maintain a run ledger on the anchor issue.
5. Dispatch unblocked research issues, up to 5 concurrent research tasks.
6. Route every artifact through outline review, draft review, final promotion, `_index.md` serialization, and TW handoff.
7. Dispatch `technical-writer-agent` after all research issues pass the done gate.

## Non-Negotiables

- Orchestrator is the only status-transition authority.
- Orchestrator is the only writer of `{project_slug}/research-sections/_index.md`.
- Research Agent and Adversarial Agent never communicate directly.
- Every decision must be recoverable from issue comments plus the run ledger.
- If a required capability is missing, block or escalate rather than improvising.

## Multica CLI

Use the installed `multica` CLI. For exact dispatch parameters and message templates, load `references/squad-communication-protocol.md`.
