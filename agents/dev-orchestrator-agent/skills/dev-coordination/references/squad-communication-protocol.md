# Dev Squad Inter-Agent Communication Protocol

> **Document type**: Human reference. This file is not read by agents at runtime. Each agent prompt embeds its own role-specific subset of this protocol.
>
> **Last updated**: 2026-05-30

## 1. Scope and Runtime Boundary

This protocol governs inter-agent coordination for the three runtime dev squad agents running on **Multica**. Linear issues and GitHub PRs are external mirrors or delivery surfaces only. All runtime issue IDs, comments, @mentions, reactions, task runs, and status transitions in this document refer to **Multica, not Linear**.

| Agent | Role |
|---|---|
| **Dev Orchestrator** | Decomposes requirements, dispatches work, owns state transitions, merges PRs |
| **Dev Engineer** | Implements features, writes tests, opens PRs in isolated worktrees |
| **Dev Reviewer** | Adversarially reviews PRs for correctness, security, performance, and test coverage, posts advisory verdicts |

## 2. Repository and Branch Convention

### Branch Naming

```
dev/{project-slug}/{task-slug}
```

- `{project-slug}`: stable project identifier, lowercase hyphenated.
- `{task-slug}`: stable task identifier, lowercase hyphenated. Must not use Multica issue IDs or any implementation-tracking identifiers.

### Worktree Layout

```text
{repo-root}/
├── .claude/worktrees/
│   ├── {task-slug-1}/     # Engineer instance 1 worktree
│   ├── {task-slug-2}/     # Engineer instance 2 worktree
│   └── {task-slug-3}/     # Engineer instance 3 worktree
├── .git/                  # Shared git directory
└── (main checkout)        # Orchestrator reference
```

Each engineer instance works in a fully isolated worktree. Worktrees share the `.git` directory but have independent file trees, `node_modules`, build artifacts, and test state.

### Worktree Exclusion

Before creating the first worktree, Engineer must ensure `.claude/worktrees/` is excluded via `.git/info/exclude` (not `.gitignore`). This is a local-only exclusion that prevents worktree directories from appearing as untracked files without creating uncommitted changes in the main checkout.

```bash
grep -qxF '.claude/worktrees/' .git/info/exclude 2>/dev/null || echo '.claude/worktrees/' >> .git/info/exclude
```

### Worktree Lifecycle

| Phase | Actor | Action |
|---|---|---|
| Fresh base | Orchestrator | Before dispatch, run `git fetch --prune origin`, resolve `base_main_sha="$(git rev-parse origin/main)"`, and include that SHA in the Dispatch comment |
| Create | Engineer | Run `git fetch --prune origin`, record `base_main_sha="$(git rev-parse origin/main)"`, then create the worktree with `git worktree add .claude/worktrees/{task-slug} -b dev/{project-slug}/{task-slug} origin/main` |
| Resume | Engineer | If worktree/branch already exists, run `git fetch --prune origin` and verify `git merge-base --is-ancestor "$base_main_sha" HEAD`; if false, run `git rebase origin/main` before coding |
| Dependent rebase | Engineer | `git rebase {dependent-branch}` inside worktree (when `dependent_branches` is provided) after verifying the dependency branch itself contains the latest `origin/main` |
| Work | Engineer | All coding, testing, commits inside worktree |
| PR | Engineer | Push branch, open PR to `main` |
| Merge | Orchestrator | Merge PR via GitHub |
| Cleanup | Orchestrator | After merge is verified, run `git push origin --delete dev/{project-slug}/{task-slug}`, `git fetch --prune origin`, and `git worktree remove .claude/worktrees/{task-slug}` |

The `base_main_sha` in Engineer's handoff must match the latest `origin/main` observed at worktree creation or stale-branch rebase time. If `origin/main` has moved and the branch does not contain it, Engineer must rebase, rerun tests, and only then post `Implementation Ready` or `Revision Complete`.

### Shared-File Dependency Rule

If two tasks modify the same file (e.g., `schema.ts`, `index.ts`, config files), they must have:
- An explicit `blockedBy` dependency in the task ledger, OR
- An explicit merge order documented by Orchestrator.

Orchestrator must never dispatch two engineers to concurrently modify the same file without one of these relationships. Violation creates unpredictable merge conflicts.

## 2.5 Multica Issue Status

Orchestrator must keep each task's Multica issue status in sync with the workflow:

| Multica Status | Trigger | CLI |
|---|---|---|
| `In Progress` | Dispatch: implementation posted, or Revision Request posted | `multica issue update {issue_id} --status "In Progress"` |
| `In Review` | Dispatch: review posted | `multica issue update {issue_id} --status "In Review"` |
| `Done` | PR merged + remote branch deleted + per-task done gate passed | `multica issue update {issue_id} --status "Done"` |

Rules:
- Update status immediately after posting the triggering comment.
- Only Orchestrator updates Multica issue status.
- BLOCKED tasks keep their current status until the block resolves.
- Status transitions are logged in the task ledger's Multica Status column.

## 2.6 Multica CLI Contract

Standardized commands for all Multica operations. If a command fails, the agent must output the action as a `=== PENDING MULTICA ACTIONS ===` block (see Section 9).

| Operation | Command | Used by |
|---|---|---|
| Create task issue | See body-file example below | Orchestrator |
| Post comment | See body-file example below | All agents |
| Update status | `multica issue update {issue_id} --status "In Progress"` | Orchestrator |
| Add reaction | `multica issue react {issue_id} --comment {comment_id} --emoji {seen\|approved\|action-needed}` | Orchestrator |
| List agents | `multica agent list --output json` | Orchestrator only |
| Close issue | `multica issue close {issue_id}` | Orchestrator |

For commands with multi-line markdown bodies (create, comment), write the body to a temporary file and pass it by file. Do not inline large markdown bodies into shell quotes; issue comments contain newlines, backticks, and mention links that are easy to corrupt with ad hoc quoting.

```bash
body_file="$(mktemp)"
trap 'rm -f "$body_file"' EXIT
cat > "$body_file" <<'BODY'
## Implementation Ready

**Issue**: {multica_issue_id}
**Target agent**: [@Dev Orchestrator](mention://agent/{uuid})
BODY

multica issue comment {issue_id} --body-file "$body_file"
multica issue create --project {project_id} --title "{title}" --body-file "$body_file"
```

If the installed Multica CLI does not support `--body-file`, do not improvise a quoted multi-line command. Output the complete comment or issue body as a `=== PENDING MULTICA ACTIONS ===` block so Orchestrator or a human relay can execute it with the correct runtime.

Workers must never call `multica agent list`. Agent UUIDs come from the Orchestrator's Agent Directory in dispatch comments.

## 3. Communication Channels

| Channel | Purpose | Notes |
|---|---|---|
| **Multica issue comments** | Primary channel for dispatches, updates, review feedback, blockers, and completion reports | All structured messages use the templates in Section 7 |
| **@mentions** | Trigger the receiving agent to act | Dispatch and continuous handoff comments must contain exactly one Multica mention link. Plain text `@AgentName` does not trigger a task. |
| **Emoji reactions** | Orchestrator acknowledges messages | Reactions never replace decision comments |
| **GitHub PRs** | Code delivery and review | Referenced from comments by URL |

## 4. Protocol State Machine

```text
planned
  -> assigned
  -> worktree-created
  -> in-progress
  -> pr-opened
  -> under-review
  -> approved | revision-requested
      |               |
      v               v
    merged      revision-in-progress
      |               |
      v               v
  worktree-cleaned  pr-updated -> under-review (round N+1)
      |
      v
    done
```

### State Ownership Table

| State / Transition | Owner | Required Condition | Multica Status |
|---|---|---|---|
| `planned` | Orchestrator | Task created in ledger | — |
| `assigned` | Orchestrator | Dispatch posted with engineer mention | `In Progress` |
| `worktree-created` | Engineer | Worktree exists and branch is pushed | — |
| `in-progress` | Engineer | Implementation started | — |
| `pr-opened` | Engineer | PR opened to `main`, Implementation Ready posted | — |
| `under-review` | Orchestrator | Dispatch: review posted | `In Review` |
| `approved` / `revision-requested` | Orchestrator | Reviewer verdict handled | `In Progress` (if revision) |
| `merged` | Orchestrator | PR merged to `main` | — |
| `worktree-cleaned` | Orchestrator | Remote branch deleted and worktree removed after merge verified | — |
| `done` | Orchestrator | Done gate passes | `Done` |

Only Orchestrator advances task status. Workers may request status changes but cannot transition states directly.

### Continuous Handoff and Resume

Multica continues the workflow only when the next actor is explicitly mentioned in the issue thread. A worker's final chat output is not enough; the worker must post the structured issue comment that mentions the next target.

- **Continuous worker handoffs**: `Implementation Ready`, `Revision Complete`, and `Review Verdict` must include exactly one full target-agent mention link in `Target agent`, and that link must point to `Dev Orchestrator`: `[@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})`.
- **Dispatches**: `Dispatch: implementation`, `Dispatch: review`, and `Revision Request` must include exactly one full target-agent mention link in `Target agent`, pointing to the worker being dispatched.
- **Terminal comments**: `Merge Complete`, `BLOCKED`, and project completion comments do not include an agent mention. Use `Target agent: none`.
- **Handoff self-check**: before posting any continuous handoff or dispatch, verify the comment body contains exactly one `mention://agent/`. If it contains zero, the workflow will stall. If it contains more than one, Multica may trigger non-target agents.
- **Non-target guard**: if an agent task is triggered but the comment's `Target agent` is another agent, do not post a Multica issue comment. Record the ignored task only in runtime output. If Multica runtime requires an issue-visible terminal action, use the platform's cancel/no-op mechanism rather than writing "not for me" noise into the issue thread.
- **Resume rule**: when Orchestrator is invoked by `/dev-resume`, `go on`, a fresh mention, or a worker handoff, it must reconstruct state from `multica issue comment list {issue_id}` and `multica issue runs {issue_id}` sorted by `created_at`, then perform the next required action without waiting for human confirmation unless a `BLOCKED` state or missing capability requires it.

## 5. Done Gate

### Per-Task Done Gate (8 items)

A task may transition to `done` only when **all** of the following are true:

1. Implementation meets acceptance criteria from the task description.
2. Tests pass (project test suite, not just task-specific tests).
3. Reviewer has posted approval, or Orchestrator posted explicit `accept-risk`.
4. No unresolved critical finding remains.
5. PR is merged to `main`.
6. Remote task branch is deleted from `origin`.
7. Worktree is cleaned up (removed).
8. Orchestrator posted a closing comment on the task issue.

### Project Done Gate (6 items)

A project is complete when **all** of the following are true:

1. All tasks in the ledger have status `done`.
2. `main` branch passes the full test suite.
3. No open BLOCKED issues remain.
4. Orchestrator posted a project completion summary on the anchor issue.
5. All task branches have been deleted from `origin`.
6. All worktrees are cleaned up.

## 6. Emoji Reaction Semantics

| Symbol | Alias | Meaning | Applied by |
|---|---|---|---|
| :eyes: | `seen` | Message received, not acted upon | Orchestrator |
| :white_check_mark: | `approved` | Gate pass | Orchestrator |
| :arrows_counterclockwise: | `action-needed` | Revision required | Orchestrator |

## 7. Message Type Templates

Every message comment must include: `issue_id`, `project_slug`, `task_slug`, `phase`, `round`, `target_agent`, and `next_action`.

### Agent Directory

Orchestrator provides the complete roster in every Dispatch comment:

```markdown
**Agent Directory** (non-triggering, for handoff construction; bare UUIDs only):
- Dev Orchestrator: `{orchestrator-id}`
- Dev Engineer: `{engineer-id}`
- Dev Reviewer: `{reviewer-id}`
```

### 7.1 Dispatch: Implementation

```markdown
## Dispatch: implementation

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**Branch**: dev/{project-slug}/{task-slug}
**Base main SHA**: {base_main_sha from `git fetch --prune origin`}
**Phase**: implementation
**Round**: 1
**Target agent**: [@Dev Engineer](mention://agent/{engineer-id})
**Multica status**: In Progress
**Next action**: Dev Engineer verifies latest origin/main base, creates or rebases worktree, implements task, opens PR, posts Implementation Ready

**Task description**:
{scope, acceptance criteria, technical constraints}

**Files likely touched**:
- {file1}
- {file2}

**Dependencies**: {blocked-by task slugs, or "none"}

**Agent Directory** (non-triggering, for handoff construction):
- Dev Orchestrator: `{orchestrator-id}`
- Dev Engineer: `{engineer-id}`
- Dev Reviewer: `{reviewer-id}`
```

### 7.2 Implementation Ready

```markdown
## Implementation Ready

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**Branch**: dev/{project-slug}/{task-slug}
**Base main SHA**: {base_main_sha used for worktree creation or stale-branch rebase}
**Base verification**: `git merge-base --is-ancestor {base_main_sha} HEAD` passed after latest `git fetch --prune origin`
**Phase**: implementation
**Round**: {n}
**PR**: {pr_url}
**Commits**: {count} commits, {files_changed} files changed
**Tests**: {pass | fail — detail if fail}
**Summary**: {1-2 sentences on what was implemented}
**Target agent**: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Dev Orchestrator dispatches code review
```

### 7.3 Dispatch: Review

```markdown
## Dispatch: review

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**Branch**: dev/{project-slug}/{task-slug}
**Phase**: review
**Round**: {n}
**PR**: {pr_url}
**Multica status**: In Review
**Target agent**: [@Dev Reviewer](mention://agent/{reviewer-id})
**Next action**: Dev Reviewer reviews PR and posts Review Verdict

**Review focus**: {areas to focus on, or "general"}
**Design doc**: {path, or "none"}

**Agent Directory** (non-triggering, for handoff construction):
- Dev Orchestrator: `{orchestrator-id}`
- Dev Engineer: `{engineer-id}`
- Dev Reviewer: `{reviewer-id}`
```

### 7.4 Review Verdict

```markdown
## Review Verdict: {approve | request-changes}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**PR**: {pr_url}
**Phase**: review
**Round**: {n}
**Recommendation**: {approve | request-changes}
**Severity**: {critical | major | minor | none}

**Structural findings**:
- [{severity}] {file}:{line} — {description}. Fix: {recommendation}.

**Adversarial findings**:
- [{severity}] [{lens}] {file}:{line} — {challenge}. Alternative: {alternative}.

**Target agent**: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Dev Orchestrator {merges PR | dispatches revision to Engineer}
```

### 7.5 Revision Request

```markdown
## Revision Request

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**Branch**: dev/{project-slug}/{task-slug}
**Base main SHA**: {base_main_sha after latest stale-branch check}
**Phase**: revision
**Round**: {n} -> {n+1}
**Multica status**: In Progress
**Target agent**: [@Dev Engineer](mention://agent/{engineer-id-from-directory})
**PR**: {pr_url}
**Required changes**:
- {change 1}
- {change 2}
**Next action**: Dev Engineer addresses findings, pushes commits, posts Revision Complete

**Agent Directory** (non-triggering, for handoff construction):
- Dev Orchestrator: `{orchestrator-id}`
- Dev Engineer: `{engineer-id}`
- Dev Reviewer: `{reviewer-id}`
```

### 7.6 Revision Complete

```markdown
## Revision Complete

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**Branch**: dev/{project-slug}/{task-slug}
**Base main SHA**: {base_main_sha used for revision branch check or rebase}
**Base verification**: `git merge-base --is-ancestor {base_main_sha} HEAD` passed after latest `git fetch --prune origin`
**Phase**: revision
**Round**: {n}
**PR**: {pr_url}
**Changes addressed**:
- {change 1}: {how addressed}
- {change 2}: {how addressed}
**Tests**: {pass | fail}
**Target agent**: [@Dev Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Dev Orchestrator dispatches re-review
```

### 7.7 Merge Complete

```markdown
## Merge Complete

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**Branch**: dev/{project-slug}/{task-slug}
**Phase**: merged
**PR**: {pr_url}
**Merge commit**: {sha}
**Remote branch deleted**: yes (`git push origin --delete dev/{project-slug}/{task-slug}`)
**Worktree removed**: yes (`git worktree remove .claude/worktrees/{task-slug}`)
**Review rounds**: {n}
**Caveats**: {any accepted risks or minor findings, or "none"}
**Multica status**: Done
**Target agent**: none
**Next action**: none (task complete)
```

### 7.8 Blocked

```markdown
## BLOCKED: {brief reason}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Task slug**: {task-slug}
**Phase**: {phase}
**Round**: {n}
**Blocker**: {description}
**Attempted resolution**: {what was tried}
**Target agent**: none (BLOCKED is terminal — awaiting human intervention)
**Next action**: Human intervention or alternative path needed
```

## 8. Review Round Cap and Risk Escalation

Each task review cycle is capped at **3 rounds**.

| Severity | Action |
|---|---|
| **Critical** unresolved | Do not merge. Dispatch revision or escalate to human. |
| **Major** unresolved at round 3 | Escalate to human, or post explicit `accept-risk` with rationale. |
| **Minor** unresolved | May merge with caveats noted. |

## 9. Runtime Capability Fallback

If an agent cannot perform a required Multica comment, reaction, or status action, it outputs:

```text
=== PENDING MULTICA ACTIONS ===
target_issue: {multica_issue_id}
actions:
  - type: comment
    body: |
      {full comment markdown}
  - type: reaction
    target_comment: {comment_link_or_id}
    emoji: {seen | approved | action-needed}
=== END PENDING MULTICA ACTIONS ===
```

Only Orchestrator or a human relay executes pending actions. Pending action payloads must be complete and self-contained.

### Mention Link Failure Fallback

If a Worker agent cannot generate a valid mention link because the dispatch did not include an Agent Directory, the Worker must:

1. Complete the work normally.
2. Output the handoff comment in a `=== PENDING MULTICA ACTIONS ===` block with `Target agent: BLOCKED — no directory`.
3. In the pending action body, include a note: `Orchestrator: re-dispatch with Agent Directory so this handoff can be posted with the correct mention link.`

This ensures the completed work is not lost and the pending action block alerts Orchestrator or a human relay to re-send the dispatch with a valid Agent Directory. The Worker must never guess agent UUIDs or call `multica agent list` to resolve the gap.
