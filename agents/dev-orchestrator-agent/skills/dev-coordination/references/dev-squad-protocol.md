# Dev Squad Protocol Reference (Orchestrator View)

Role-specific excerpt of `references/squad-communication-protocol.md`. This is not a verbatim copy; it contains the subset relevant to Dev Orchestrator operations.

## State Machine

```text
planned -> assigned -> worktree-created -> in-progress -> pr-opened -> under-review
  -> approved -> merged -> worktree-cleaned -> done
  -> revision-requested -> revision-in-progress -> pr-updated -> under-review (round N+1)
```

## Task Ledger Schema

```markdown
| # | Task | Slug | Multica Status | Internal State | Branch | Engineer | Reviewer | PR | Dependencies |
|---|------|------|----------------|----------------|--------|----------|----------|----|--------------|
| 1 | {description} | {task-slug} | {In Progress/In Review/Done} | {state} | dev/{project}/{task} | {agent} | {agent} | {url} | {blocked-by} |
```

Internal states: `planned`, `assigned`, `in-progress`, `pr-opened`, `under-review`, `revision-{n}`, `approved`, `merged`, `worktree-cleaned`, `done`.

## Status Transitions

Update Multica status immediately after posting the triggering comment:

| Action | Multica Status | CLI |
|---|---|---|
| Dispatch: implementation posted | `In Progress` | `multica issue update {issue_id} --status "In Progress"` |
| Dispatch: review posted | `In Review` | `multica issue update {issue_id} --status "In Review"` |
| Revision Request posted | `In Progress` | `multica issue update {issue_id} --status "In Progress"` |
| PR merged + done gate passed | `Done` | `multica issue update {issue_id} --status "Done"` |

## Dispatch Checklist

Before every dispatch:

1. Run `multica agent list --output json` for fresh UUIDs.
2. Build exactly one `mention://agent/` link for the target agent.
3. Include the complete squad roster in an Agent Directory as bare UUIDs only: Dev Orchestrator, Dev Engineer, and Dev CC Reviewer.
4. Verify no other in-flight task touches the same files unless dependencies or merge order are explicit.
5. Post the triggering comment before changing Multica status.

## Continuous Handoff and Resume

- Worker handoffs (`Implementation Ready`, `Revision Complete`, `Review Verdict`) must mention `Dev Orchestrator` in `Target agent`; otherwise Multica will not trigger Orchestrator automatically.
- Dispatches and continuous handoffs must contain exactly one `mention://agent/`.
- Terminal comments (`Merge Complete`, `BLOCKED`, project completion) use `Target agent: none`.
- On `/dev-resume`, `go on`, or any fresh squad/orchestrator mention, reconstruct state from `multica issue comment list {issue_id} --output json` and `multica issue runs {issue_id} --output json`, sorted by `created_at`, then continue the next required action.

## Worktree Coordination

- Branch format: `dev/{project-slug}/{task-slug}`.
- Engineer creates the worktree from latest `origin/main`.
- If task B depends on task A, task B rebases on task A's branch before starting.
- After merge, Orchestrator verifies integration and removes `.claude/worktrees/{task-slug}`.

## Done Gates

Per-task done gate:

1. Acceptance criteria met.
2. Tests pass.
3. Review approved or explicit accept-risk posted.
4. No unresolved critical findings.
5. PR merged to `main`.
6. Worktree cleaned up.
7. Closing comment posted.

Project done gate:

1. All tasks in the ledger are done.
2. `main` passes the full test suite.
3. No open BLOCKED issues remain.
4. Completion summary posted.
5. All worktrees cleaned up.

## Message Templates

Use the complete templates from `references/squad-communication-protocol.md` Section 7:

- 7.1 Dispatch: Implementation
- 7.2 Implementation Ready
- 7.3 Dispatch: Review
- 7.4 Review Verdict
- 7.5 Revision Request
- 7.6 Revision Complete
- 7.7 Merge Complete
- 7.8 Blocked
