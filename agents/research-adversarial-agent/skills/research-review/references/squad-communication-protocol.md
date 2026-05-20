# Research Squad Inter-Agent Communication Protocol

> **Document type**: Human reference. This file is not read by agents at runtime. Each agent prompt embeds its own role-specific subset of this protocol.
>
> **Last updated**: 2026-05-19

## 1. Scope and Runtime Boundary

This protocol governs inter-agent coordination for the four runtime research squad agents running on **Multica**. Project Planner is a separate pre-planning tool and is not part of the runtime squad roster.

| Agent | Role |
|---|---|
| **Orchestrator** | Dispatches work, owns state transitions, serializes `_index.md` writes |
| **Research Agent** | Produces outlines, drafts, and final sections via research skills |
| **Adversarial Agent** | Reviews outlines and drafts, posts advisory verdicts |
| **Technical Writer (TW)** | Aggregates final sections into the project report |

Linear issues are implementation tracking only. All runtime issue IDs, comments, @mentions, reactions, and status transitions in this document refer to **Multica**, not Linear.

## 2. Unified GitHub Repo and Path Convention

All research output is persisted to a single repository.

- **Default repo**: `Whisker17/multica-research`
- **`github_repo`** defaults to `Whisker17/multica-research` for all agents.

### Directory Structure

```text
{project-slug}/
├── outlines/
│   └── {topic-slug}.md                    # candidate during Phase A; approved by state transition
├── research-sections/
│   ├── _index.md                           # issue mapping + execution order; Orchestrator-owned serialized writes
│   └── {topic-slug}/
│       ├── drafts/
│       │   └── round-{n}.md                # Phase B draft before adversarial review
│       └── final.md                        # approved/accepted final section
└── report/
    ├── final-report.md                     # TW final output
    └── assets/                             # diagram assets
```

### Slug Rules

- **`{project-slug}`**: Stable project identifier from pre-planned project metadata or Orchestrator issue context. Lowercase, hyphen-separated.
- **`{topic-slug}`**: Per research issue. Stable and human-readable. Must **not** use Linear `WHI-*` IDs or any implementation-tracking identifiers.

### Artifact Ownership

| Path | Owner | Notes |
|---|---|---|
| `{project-slug}/outlines/{topic-slug}.md` | Research Agent | Candidate during Phase A; approval tracked by Orchestrator state, not file path |
| `{project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md` | Research Agent | Must be persisted before adversarial review |
| `{project-slug}/research-sections/{topic-slug}/final.md` | Research Agent | Written only after approve / accept-risk |
| `{project-slug}/research-sections/_index.md` | Orchestrator | Serialized writes only; Research Agent provides Index Entry Proposal |
| `{project-slug}/report/final-report.md` | Technical Writer | Aggregated from all final sections |
| `{project-slug}/report/assets/` | Technical Writer | Diagram assets |

### Git Branch Convention

Research issue branches use `research/{project-slug}/{topic-slug}`. Technical Writer output uses `research/{project-slug}/final-report`.

Worker agents write outlines, drafts, final sections, and final reports only on their deterministic work branch. If Multica starts the runtime on a random branch, the worker must switch to the deterministic branch before writing.

`main` contains accepted research packages only. Orchestrator does not squash merge whole work branches, because that could copy random runtime files into `main`. Instead, Orchestrator selectively integrates allowlisted artifacts from the work branch into latest `main`: approved outline, persisted draft rounds, final section, and `_index.md` when needed. It then pushes `main` and deletes the work branch.

## 3. Communication Channels

| Channel | Purpose | Notes |
|---|---|---|
| **Multica issue comments** | Primary channel for dispatches, updates, review feedback, blockers, artifact-ready messages, and completion reports | All structured messages use the templates in Section 8 |
| **@mentions** | Trigger the receiving agent to act | Dispatch and handoff comments must contain exactly one Multica mention link: `[@AgentName](mention://agent/{uuid})`. Plain text `@AgentName` does **not** trigger a task. Non-target agent UUIDs come from the non-triggering Agent Directory (see Section 8). |
| **Emoji reactions** | Orchestrator acknowledges messages | Reactions never replace decision comments |
| **GitHub artifacts** | Persisted outline/draft/final files | Referenced from comments and run ledger by path and commit URL/SHA |

## 4. Skill Interface Alignment (WHI-435)

The protocol uses three research skills:

| Skill | Used by | Phase |
|---|---|---|
| `/research-outline` | Research Agent | Phase A: generate structured outline |
| `/research-review` | Adversarial Agent | Phase A: review outline |
| `/research-deep-output` | Research Agent | Phase B: produce full research section draft |

All three skills share a common outline schema and must accept and propagate: `project_slug`, `topic_slug`, `github_repo`, and `artifact_paths` (`outline`, `draft`, `final`, `index`).

## 5. Protocol State Machine

### States (Project Mode / Composable Single-Issue)

```text
planned
  -> branch-created
  -> outline-in-progress
  -> outline-ready
  -> outline-under-review
  -> outline-approved
  -> deep-draft-in-progress
  -> deep-draft-ready
  -> deep-draft-under-review
  -> approved-for-final
  -> final-promotion-in-progress
  -> final-promotion-ready
  -> merge-ready
  -> main-merge-in-progress
  -> main-merged
  -> branch-deleted
  -> tw-handoff-in-progress
  -> reported-to-TW
  -> done
```

### States (Lightweight Single-Issue — no `report_issue_id`)

```text
planned
  -> branch-created
  -> outline-in-progress
  -> outline-ready
  -> outline-under-review
  -> outline-approved
  -> deep-draft-in-progress
  -> deep-draft-ready
  -> deep-draft-under-review
  -> approved-for-final
  -> final-promotion-in-progress
  -> final-promotion-ready
  -> merge-ready
  -> main-merge-in-progress
  -> main-merged
  -> branch-deleted
  -> done
```

In lightweight mode, the `tw-handoff-*` and `reported-to-TW` states are skipped. After `final-promotion-ready`, Orchestrator selectively integrates the allowlisted research package (outline, persisted draft rounds, and final section) to `main`, deletes the work branch, runs the lightweight Done Gate, and transitions to `done`.

### State Ownership Table

| State / Transition | Owner | Required Condition |
|---|---|---|
| Dispatch outline | Orchestrator | Research issue unblocked |
| `branch-created` | Research Agent | Deterministic work branch exists and is pushed |
| `outline-in-progress` | Research Agent | Outline work started via `/research-outline` |
| `outline-ready` (Artifact Ready: outline) | Research Agent | Candidate outline persisted at `{project-slug}/outlines/{topic-slug}.md` with commit |
| `outline-under-review` | Adversarial Agent | `/research-review` output posted as advisory verdict |
| `outline-approved` / revise | Orchestrator | No unresolved critical/major blocker, or revision requested |
| Dispatch deep draft | Orchestrator | Outline state is `outline-approved` |
| `deep-draft-in-progress` | Research Agent | Deep draft work started via `/research-deep-output` |
| `deep-draft-ready` (Artifact Ready: deep-draft) | Research Agent | Draft persisted at `drafts/round-{n}.md` with commit |
| `deep-draft-under-review` | Adversarial Agent | Persisted draft reviewed (not ephemeral chat text) |
| `approved-for-final` / accept-risk / revise | Orchestrator | Advisory verdict handled; critical cannot pass |
| `final-promotion-in-progress` | Research Agent | Writing `final.md` from approved draft |
| `final-promotion-ready` (Final Promotion Ready) | Research Agent | Final section persisted on work branch; Index Entry Proposal posted when applicable |
| `merge-ready` | Orchestrator | Quality gates passed and allowlisted integration paths validated |
| `main-merge-in-progress` | Orchestrator | Final branch commit and proposal validated against run ledger |
| `main-merged` | Orchestrator | Allowlisted research package and optional `_index.md` written to `main` in one integration commit |
| `branch-deleted` | Orchestrator | Remote work branch deleted after `main` push |
| `tw-handoff-in-progress` | Research Agent | Posting Research Complete on TW reserved issue |
| `reported-to-TW` | Research Agent | Orchestrator supplied main integration commit URL/SHA; Research Complete posted and Done Gate requested |
| `done` | Orchestrator | Done Gate passes (see Section 6) |

Only Orchestrator advances issue status. Worker agents may request status changes but cannot transition states directly.

## 6. Done Gate

### Project Mode / Composable Single-Issue Done Gate (13 items)

A research issue may transition to `done` only when **all** of the following are true:

1. Outline consensus reached (state passed through `outline-approved`).
2. At least one Phase B draft was persisted before adversarial review.
3. The reviewed draft work branch commit URL/SHA is recorded.
4. Adversarial Agent has posted approval, or Orchestrator posted explicit `accept-risk` for a major finding.
5. No unresolved critical finding remains.
6. Final section exists on the work branch at `{project-slug}/research-sections/{topic-slug}/final.md`.
7. Orchestrator wrote the accepted outline, persisted draft rounds, and final section to `main`, and recorded `main_merge_commit`.
8. Orchestrator wrote the Index Entry Proposal into `{project-slug}/research-sections/_index.md` in the same `main_merge_commit`.
9. Orchestrator deleted the remote work branch after `main` push.
10. Research Agent posted Research Complete on the TW reserved issue after main integration, including: reviewed draft path, final section path, final branch commit, `main_merge_commit`, and approval/accept-risk link.
11. Research Agent posted Done Gate Request on the research issue after TW handoff.
12. Orchestrator acknowledged the TW handoff comment with `seen`/ACK.
13. Orchestrator posted a closing comment summarizing outcome, artifact paths, TW handoff, and caveats.

### Lightweight Single-Issue Done Gate (10 items — no `report_issue_id`)

A research issue may transition to `done` only when **all** of the following are true:

1. Outline consensus reached (state passed through `outline-approved`).
2. At least one Phase B draft was persisted before adversarial review.
3. The reviewed draft work branch commit URL/SHA is recorded.
4. Adversarial Agent has posted approval, or Orchestrator posted explicit `accept-risk` for a major finding.
5. No unresolved critical finding remains.
6. Final section persisted on the work branch at `{project-slug}/research-sections/{topic-slug}/final.md`.
7. Final Promotion Ready posted on research issue with final section path and branch commit; Index Entry Proposal is not required.
8. Orchestrator wrote the accepted outline, persisted draft rounds, and final section to `main`, and recorded `main_merge_commit`.
9. Orchestrator deleted the remote work branch after `main` push.
10. Orchestrator posted closing comment on research issue.

## 7. Emoji Reaction Semantics

| Symbol | Alias | Meaning | Applied by | Notes |
|---|---|---|---|---|
| 👀 | `seen` | Message received, not acted upon | Orchestrator | **Not** approval |
| ✅ | `approved` | Gate pass | Orchestrator | Must be accompanied by state-transition comment |
| 🔄 | `action-needed` | Revision required | Orchestrator | Must be accompanied by action comment |

Blocked state is represented by a comment prefix (`BLOCKED:` or with warning emoji), **not** by reaction.

## 8. Message Type Templates

Every message comment must include: `issue_id`, `project_slug`, `topic_slug`, `phase`, `round`, `target_agent`, and `next_action`. Artifact-related messages must also include artifact paths and commit URL/SHA. Project-level messages without a research topic use `topic_slug: final-report`.

### Agent Directory

Multica treats every `mention://agent/{uuid}` in a comment as a trigger. It does not distinguish a reference list from the actual target. Therefore every dispatch and continuous handoff comment must contain exactly one full agent mention link, and that mention must be the current target agent.

**Orchestrator** is responsible for providing the roster:

1. Before each Dispatch comment, Orchestrator runs `multica agent list --output json` to obtain the current `{name, id}` mapping. This ensures the roster is never stale, even if agents are redeployed mid-pipeline.
2. Every Dispatch comment includes an **Agent Directory** block with bare UUIDs only:

```markdown
**Agent Directory** (non-triggering, for handoff construction):
- Orchestrator: `{orchestrator-id}`
- Deep Research Agent: `{research-id}`
- Research Review Agent: `{review-id}`
- Technical Writer Agent: `{tw-id}`
```

3. The dispatch `Target agent` field contains the only full `mention://agent/` link in the dispatch body. `Next action` names the same target in plain text unless the protocol template explicitly places the single mention there instead of `Target agent`.
4. Worker agents build exactly one target mention link from the Agent Directory UUID when writing `Target agent` and use plain text for the same target in `Next action`. Never write plain text `@AgentName` as a trigger, and never turn the whole Agent Directory into mention links.
5. Worker agents do not call `multica agent list` for handoff construction; Orchestrator is the roster provider.
6. Project Planner is not a runtime squad member. Do not include Project Planner in runtime dispatch mentions or the Agent Directory.
7. If a dispatch does not include an Agent Directory, the Worker must post `BLOCKED: missing agent directory in dispatch — cannot generate valid handoff mention` instead of guessing an agent UUID.

### Single-Target Trigger Self-Check

Before posting any dispatch or continuous handoff, the posting agent must check:

- The comment body contains exactly one `mention://agent/`.
- The only full mention points to the `Target agent`.
- The Agent Directory contains only bare UUIDs and contains no `mention://agent/`.

If a dispatch fails this check, Orchestrator must not post it as-is. It must post `BLOCKED: dispatch has multiple trigger mentions` or emit a complete `=== PENDING MULTICA ACTIONS ===` payload with a corrected single-target dispatch body.

### Handoff Rules

All agents must follow these rules when posting completion messages:

- **Continuous tasks** (handoff required): the completion message must include exactly one full target-agent mention link, constructed from the Agent Directory, in `Target agent`. Use plain text for the same target in `Next action`.
- **Terminal tasks** (stoppable): closing comments, BLOCKED messages awaiting human intervention, and final pipeline endpoints do not require a mention link. Use `Target agent: none` and `Next action: none` or `Next action: awaiting human input`.
- **Handoff self-check**: before posting a continuous-task comment, verify the comment body contains exactly one `mention://agent/`. If it does not, the handoff is malformed and must be corrected before posting.
- **Non-target guard**: if an agent task is triggered but the comment's `Target agent` is another agent, do not post a Multica issue comment. Record the ignored task only in runtime output. If Multica runtime does not allow a task to end without a comment, use the platform's cancel/no-op mechanism and record that limitation; do not write "not for me" noise into the issue thread.
- In composable/project mode, the relay chain is: Final Promotion Ready -> Orchestrator, Research Complete -> Technical Writer, Done Gate Request -> Orchestrator, Final Report Ready -> Orchestrator.
- In lightweight single-issue mode, Final Promotion Ready is still a continuous task: `Target agent: [@Orchestrator](mention://agent/{id})`, `Next action: Orchestrator integrates the allowlisted research package to main, deletes the branch, runs the lightweight Done Gate, and closes the research issue`. The Orchestrator closing comment is terminal.

### Orchestrator Continuous-Action Rule

Orchestrator is not a daemon and will not wake itself after a stalled handoff. When Orchestrator handles a continuous stage in one run, it must finish that run by doing one of the following:

1. Post the next dispatch comment.
2. Post a clear terminal state with `Target agent: none` and `Next action: awaiting human input`.
3. Emit `=== PENDING MULTICA ACTIONS ===` with the complete next dispatch body if runtime capability prevents immediate posting.

This applies after applying outline revisions, applying draft revisions, handling outline review verdicts, handling draft review verdicts, and handling Final Promotion Ready.

### Timeline Reading Rule

Do not read `multica issue runs` default output as chronological flow. For timeline display, sort comments and runs by `created_at` ascending, then use `phase` and `round` as the logical sequence markers. For concurrent runs under the same `trigger_comment_id`, show `started_at` and `completed_at` inside that group.

### 8.1 Dispatch

```markdown
## Dispatch: {phase}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: {outline | outline-review | deep-draft | draft-review | final-promotion | tw-handoff | final-report}
**Round**: {n}
**Target agent**: {single target mention link}
**Next action**: {explicit instruction for target agent, plain text target name}
**Inputs**: {paths or links}

**Agent Directory** (non-triggering, for handoff construction):
- Orchestrator: `{orchestrator-id}`
- Deep Research Agent: `{research-id}`
- Research Review Agent: `{review-id}`
- Technical Writer Agent: `{tw-id}`
```

### 8.2 Artifact Ready: Outline

```markdown
## Artifact Ready: outline

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: outline
**Round**: {n}
**Artifact**: {project-slug}/outlines/{topic-slug}.md
**Branch commit/URL**: {commit hash or permalink}
**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator dispatches adversarial outline review
**Summary**: {1-2 sentences}
```

### 8.3 Artifact Ready: Deep Draft

```markdown
## Artifact Ready: deep-draft

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: deep-draft
**Round**: {n}
**Draft path**: {project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md
**Draft branch commit/URL**: {commit hash or permalink}
**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator dispatches adversarial draft review
**Summary**: {1-2 sentences}
```

### 8.4 Review Verdict

```markdown
## Review Verdict: {approve | needs-attention | reject | outline-approved | outline-needs-revision}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: {outline-review | draft-review}
**Round**: {n}
**Artifact reviewed**: {outline path or draft path}
**Recommendation**: {approve | needs-attention | reject | outline-approved | outline-needs-revision}
**Severity**: {critical | major | minor | none}
**Findings**:
- {finding 1}
- {finding 2}
**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator {advance state | dispatch revision | accept-risk decision required | escalate}
```

### 8.5 Revision Request

```markdown
## Revision Request

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: {outline | deep-draft}
**Round**: {n} -> {n+1}
**Target agent**: [@Deep Research Agent](mention://agent/{research-id-from-directory})
**Original artifact**: {outline path or draft path}
**Original artifact branch commit/URL**: {commit hash or permalink}
**Next artifact path**: {project-slug}/outlines/{topic-slug}.md (if outline) | {project-slug}/research-sections/{topic-slug}/drafts/round-{n+1}.md (if deep-draft)
**Required changes**:
- {change 1}
- {change 2}
**Next action**: Deep Research Agent produces revised artifact and posts Artifact Ready
```

### 8.6 Final Promotion Ready

```markdown
## Final Promotion Ready: {issue title}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: final-promotion
**Round**: {n}
**Reviewed draft**: {project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md
**Reviewed draft branch commit/URL**: {commit hash or permalink}
**Final section**: {project-slug}/research-sections/{topic-slug}/final.md
**Final branch commit/URL**: {commit hash or permalink}
**Adversarial approval or accept-risk**: {link}

**Index Entry Proposal**:
| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|-----------|-----------------|------------|--------------|--------|
| {order} | {topic-slug} | {multica_issue_id} | {project-slug}/research-sections/{topic-slug}/final.md | {upstream-slugs or -} | done |

**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator validates proposal, integrates allowlisted research package (outline, draft rounds, final) and `_index.md` to main, deletes branch, then dispatches TW handoff
```

#### 8.6.1 Final Promotion Ready (Lightweight — no `report_issue_id`)

```markdown
## Final Promotion Ready: {issue title}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: final-promotion
**Round**: {n}
**Reviewed draft**: {project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md
**Reviewed draft branch commit/URL**: {commit hash or permalink}
**Final section**: {project-slug}/research-sections/{topic-slug}/final.md
**Final branch commit/URL**: {commit hash or permalink}
**Adversarial approval or accept-risk**: {link}

**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator integrates allowlisted research package to main, deletes branch, runs lightweight Done Gate, and closes research issue
```

The lightweight variant omits the Index Entry Proposal table. It is still a continuous task requiring an Orchestrator mention link handoff.

### 8.7 Research Complete

Research Complete is posted on the **TW reserved issue** only after Orchestrator commits `_index.md`.

```markdown
## Research Complete: {issue title}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Branch**: research/{project-slug}/{topic-slug}
**Phase**: tw-handoff
**Round**: {n}
**Adversarial approval or accept-risk comment**: {link}
**Summary**: {2-3 sentences}
**Draft reviewed**: {project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md
**Draft reviewed branch commit/URL**: {commit hash or permalink}
**Final section**: {project-slug}/research-sections/{topic-slug}/final.md
**Final branch commit/URL**: {commit hash or permalink}
**Sections index**: {project-slug}/research-sections/_index.md
**Main integration commit/URL**: {commit hash or permalink from Orchestrator}
**Round count**: outline rounds={N}, deep rounds={M}
**Key findings**:
- {finding 1}
- {finding 2}
- {finding 3}
**Target agent**: [@Technical Writer Agent](mention://agent/{tw-id-from-directory}) (via TW reserved issue)
**Next action**: Technical Writer Agent aggregates into final report
```

### 8.8 Done Gate Request

Done Gate Request is posted on the **research issue** after Research Complete is posted on the TW reserved issue.

```markdown
## Done Gate Request

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: reported-to-TW
**Round**: {n}
**Research Complete posted to**: {tw-issue-id}
**Main integration commit/URL**: {commit hash or permalink from Orchestrator}
**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator runs Done Gate checklist and closes research issue
```

### 8.9 Blocked

```markdown
## BLOCKED: {brief reason}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: {phase}
**Round**: {n}
**Blocker**: {description}
**Attempted resolution**: {what was tried}
**Target agent**: none (BLOCKED is terminal — awaiting human intervention)
**Next action**: Human intervention or alternative path needed
```

### 8.10 Final Report Ready

```markdown
## Final Report Ready

**Issue**: {multica_tw_issue_id}
**Project slug**: {project-slug}
**Topic slug**: final-report
**Branch**: research/{project-slug}/final-report
**Phase**: final-report
**Round**: 1
**Final report path**: {project-slug}/report/final-report.md
**Final report branch commit/URL**: {commit hash or permalink}
**Diagram assets path**: {project-slug}/report/assets/
**Diagram assets branch commit/URL**: {commit hash or permalink, or same as final report commit if committed together}
**Source sections aggregated**: {list of multica_issue_ids}
**Sections index**: {project-slug}/research-sections/_index.md
**Target agent**: [@Orchestrator](mention://agent/{orchestrator-id-from-directory})
**Next action**: Orchestrator integrates allowlisted TW artifacts (final report and assets) to main, deletes branch, records main_merge_commit, verifies, and closes project
```

## 9. Two-Phase Adversarial Loop

### Phase A: Outline Consensus

1. Orchestrator dispatches outline work to Research Agent.
2. Research Agent creates or switches to `research/{project-slug}/{topic-slug}`.
3. Research Agent uses `/research-outline` to generate a structured outline.
4. Research Agent persists the candidate outline at `{project-slug}/outlines/{topic-slug}.md` on the work branch and posts **Artifact Ready: outline**.
5. Orchestrator dispatches outline review to Adversarial Agent.
6. Adversarial Agent uses `/research-review` and posts a **Review Verdict** (advisory).
7. Orchestrator decides: approve (advance to `outline-approved`) or revise (dispatch **Revision Request**).
8. On revision, Research Agent overwrites the same outline path on the work branch and posts a new Artifact Ready with incremented round.

### Phase B: Draft Quality Check

1. Orchestrator dispatches deep draft work to Research Agent.
2. Research Agent uses `/research-deep-output` to produce a full research section draft.
3. Research Agent persists the draft at `{project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md` on the work branch and posts **Artifact Ready: deep-draft**.
4. Orchestrator dispatches draft review to Adversarial Agent.
5. Adversarial Agent reviews the **persisted draft** (not ephemeral chat text) and posts a **Review Verdict**.
6. Orchestrator decides: approve, accept-risk, or revise.

### Final Promotion

#### Composable / Project Mode (with `report_issue_id`)

1. After approve or accept-risk, Research Agent writes `final.md` on the work branch and posts **Final Promotion Ready** with Index Entry Proposal.
2. Orchestrator validates the proposal against the run ledger, reads latest `main`, selectively integrates the allowlisted research package (outline, persisted draft rounds, final section) and `_index.md` in one main commit, pushes `main`, then deletes the work branch.
3. Research Agent posts **Research Complete** on the TW reserved issue, including the `main_merge_commit`, then posts **Done Gate Request** on the research issue.

#### Lightweight Single-Issue Mode (no `report_issue_id`)

1. After approve or accept-risk, Research Agent writes `final.md` on the work branch and posts **Final Promotion Ready** (lightweight variant, no Index Entry Proposal).
2. Orchestrator selectively integrates the allowlisted research package (outline, persisted draft rounds, final section) to `main`, pushes `main`, deletes the work branch, runs the lightweight Done Gate (10 items), and posts a closing comment on the research issue.
3. Research Agent does not post Research Complete or Done Gate Request. The pipeline ends at the Orchestrator closing comment.

## 10. Max-Round and Risk Escalation Policy

Each phase is capped at **3 rounds**. If round 3 still yields a revise / needs-attention / reject recommendation, Orchestrator must post a decision comment.

### Disposition Rules

| Severity | Action |
|---|---|
| **Critical** unresolved | Escalate to human. Do not approve. |
| **Major** unresolved | Escalate to human, or post explicit `accept-risk` with rationale. |
| **Minor** unresolved | May approve with caveats. Caveats must be copied to TW reserved issue. |

## 11. Technical Writer Reserved Issue

Project pre-planning must create or identify a dedicated TW reserved issue with the following required content:

| Field | Value |
|---|---|
| GitHub repo | `Whisker17/multica-research` |
| Project slug | `{project-slug}` |
| Research section index | Multica research issue IDs, `topic_slug`, draft convention, final path |
| Sections index path | `{project-slug}/research-sections/_index.md` |
| Final report path | `{project-slug}/report/final-report.md` |
| Diagram asset path | `{project-slug}/report/assets/` |
| Trigger condition | Begin only after all listed research issues have Research Complete comments with `main_merge_commit` references |

**Assignment**: Prefer `agent:technical-writer-agent` label. Fallback: `agent_role: technical-writer-agent` in the issue description.

## 12. Index Entry Proposal Format

Research Agent includes this proposal in the Final Promotion Ready comment. Orchestrator validates it and writes `_index.md` during the selective main integration commit. This section applies only to project mode and composable single-issue mode (with `report_issue_id`). In lightweight single-issue mode, no Index Entry Proposal is produced or required.

| Field | Description |
|---|---|
| `order` | Section order number from pre-planned project metadata |
| `topic_slug` | Stable topic slug |
| `multica_issue_id` | Corresponding Multica research issue ID |
| `final_path` | `{project-slug}/research-sections/{topic-slug}/final.md` |
| `dependencies` | Upstream `topic_slug` list (or `-` if none) |
| `status` | `done` |

`_index.md` is **Orchestrator-owned**. Research Agent provides the proposal; Orchestrator performs the main integration commit and records the commit URL/SHA as `main_merge_commit`.

## 13. Runtime Capability Fallback

If an agent cannot perform a required Multica comment, reaction, or status action, it outputs a **Structured Action Payload**:

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
  - type: status_request
    requested_state: {state_name}
=== END PENDING MULTICA ACTIONS ===
```

Rules:
- Only Orchestrator or a human relay executes pending actions.
- Worker agents may request status changes via this payload, but Orchestrator remains the sole agent that advances issue status.
- Pending action payloads must be complete and self-contained so they can be executed without additional context.

### Mention Link Failure Fallback

If a Worker agent cannot generate a valid mention link because the dispatch did not include an Agent Directory, the Worker must:

1. Post the handoff comment with `Target agent: BLOCKED — no directory` instead of guessing an agent UUID.
2. Include a `=== PENDING MULTICA ACTIONS ===` block requesting that Orchestrator or a human relay re-post the handoff with the correct mention link.

Never write plain text `@AgentName` as a substitute for a missing mention link — it will silently fail to trigger the target agent.

## 14. Single-Issue Mode

Single-issue mode allows Orchestrator to run the full research pipeline on a single issue without full-project batch management. Mode is triggered by passing `single_issue_id` to Orchestrator.

### Mode Entry Rules

| Condition | Mode |
|---|---|
| `single_issue_id` present | Single-issue mode |
| `single_issue_id` absent, `project_id` present | Project mode (existing) |
| Both absent | Error |

### Two Paths

- **Composable** (with `report_issue_id`): full pipeline including selective main integration, `_index.md`, branch deletion, Research Complete, 13-item Done Gate. Compatible with later TW aggregation across multiple single-issue runs.
- **Lightweight** (no `report_issue_id`): pipeline ends after `final.md` is integrated to `main`, the work branch is deleted, and Orchestrator posts the closing comment. 10-item Done Gate. No `_index.md`, no TW handoff.

### Composability Scenario

Users can run single-issue mode multiple times to incrementally build a project:

1. Create or identify a TW reserved issue during pre-planning.
2. Run `@orchestrator single_issue_id=X report_issue_id=TW-issue` for each topic.
3. Each completion auto-posts Research Complete to the TW issue; `_index.md` is rewritten on latest `main` with auto-incremented `order`.
4. After all topics are done, dispatch TW agent for final aggregation.

### Ledger

Single-issue mode uses a single-row ledger with `mode: single-issue`. On `/resume`, the `mode` field determines which flow to follow.

### Rerun Protection

If `{project_slug}/research-sections/{topic_slug}/final.md` already exists:

- Default: BLOCKED. Orchestrator refuses to start and comments on the issue.
- Exception: active ledger resume where phase < `done`.
- Override: user comments explicit confirmation; Orchestrator cleans up old artifacts and restarts.

### Handoff Rules (Repeated for Emphasis)

- Continuous tasks: completion messages must include exactly one target agent mention link, constructed from the Agent Directory, in `Target agent`. `Next action` names the same target in plain text.
- Terminal tasks: closing comments and BLOCKED states use `Target agent: none` / `Next action: none` or `Next action: awaiting human input`.
- Lightweight Final Promotion Ready is continuous: `Target agent: [@Orchestrator](mention://agent/{id})`, `Next action: Orchestrator integrates allowlisted research package to main, deletes branch, runs lightweight Done Gate, and closes research issue`.
- Orchestrator closing comment is terminal.
