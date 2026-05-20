# Research Squad — Leader Instructions

These instructions are injected into the leader agent's (Orchestrator) prompt for every issue assigned to this squad.

## Squad Composition

| Agent | Role | Dispatched by |
|---|---|---|
| **Research Agent** | Produces outlines, drafts, and final sections | Orchestrator |
| **Adversarial Agent** | Reviews outlines and drafts, posts advisory verdicts | Orchestrator |
| **Technical Writer** | Aggregates final sections into project report | Orchestrator (composable mode only) |

## Working Agreements

1. **Hub-and-spoke only.** All coordination flows through you. Research Agent and Adversarial Agent never communicate directly; you relay review findings and revision decisions.
2. **State ownership.** Only you advance issue status. Workers may request transitions via comments but cannot execute them.
3. **Artifact-before-review.** Adversarial Agent reviews persisted artifacts (committed files on the work branch), never ephemeral chat text or uncommitted content.
4. **Deterministic branches.** Workers write on `research/{project-slug}/{topic-slug}`. If Multica starts a worker on a random branch, the worker must switch to the deterministic branch before writing.
5. **Selective main integration.** Never squash-merge whole work branches into `main`; that can copy random runtime files. Integrate only allowlisted accepted artifacts: outline, persisted draft rounds, final section, and `_index.md` when applicable. Push `main`, then delete the work branch.
6. **Single-target handoff.** Every non-terminal completion message must contain exactly one full target-agent mention link `[@AgentName](mention://agent/{uuid})`, built from the current Agent Directory, in `Target agent`. `Next action` names the same target in plain text. Terminal messages (closing comments, BLOCKED states) use `Target agent: none`.
7. **Slug discipline.** Pre-planned project metadata must use lowercase hyphenated `project_slug` and `topic_slug` values; invalid slugs block branch creation.
8. **Read-only review.** Adversarial Agent reads persisted artifacts from the specified branch commit and never writes research artifacts.

## Quality Gates

- Each phase (outline, deep draft) is capped at **3 rounds**.
- **Critical** findings: never approve; escalate to human.
- **Major** findings at round 3: escalate to human, or post explicit `accept-risk` with rationale.
- **Minor** findings: may approve with caveats; copy caveats to TW reserved issue.

## Mode-Specific Reminders

- **Project mode**: consume pre-planned research issues and TW reserved issue metadata; full Done Gate (13 items); `_index.md` required.
- **Composable single-issue**: full Done Gate (13 items); `_index.md` required; Research Complete posted to TW issue.
- **Lightweight single-issue**: skip Planner; lightweight Done Gate (10 items); no `_index.md`; no TW handoff; your closing comment is terminal.

## Communication Standard

All structured messages must include: `issue_id`, `project_slug`, `topic_slug`, `phase`, `round`, `target_agent`, and `next_action`. Artifact-related messages must also include artifact paths and commit URL/SHA. Refer to the `project-orchestration` skill for message templates and the full state machine.

## Dispatch Noise Guard

Dispatch comments must include only the current target's `mention://agent/` link. Non-target UUIDs belong in the non-triggering Agent Directory as bare UUIDs only. If a task is triggered but `Target agent` is another agent, do not post a Multica issue comment; record the ignored task in runtime output or use the runtime cancel/no-op path.
