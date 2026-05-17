# Research Squad Inter-Agent Communication Protocol

> **Document type**: Human reference. This file is not read by agents at runtime. Each agent prompt embeds its own role-specific subset of this protocol.
>
> **Last updated**: 2026-05-16

## 1. Scope and Runtime Boundary

This protocol governs inter-agent coordination for the five research squad agents running on **Multica**:

| Agent | Role |
|---|---|
| **Planner** | Creates project structure, assigns topic slugs, creates TW reserved issue |
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

- **`{project-slug}`**: Derived by Planner from the Multica project title. Stable across the entire project lifecycle. Lowercase, hyphen-separated.
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

## 3. Communication Channels

| Channel | Purpose | Notes |
|---|---|---|
| **Multica issue comments** | Primary channel for dispatches, updates, review feedback, blockers, artifact-ready messages, and completion reports | All structured messages use the templates in Section 8 |
| **@mentions** | Trigger the receiving agent to act | e.g., `@ResearchAgent`, `@Orchestrator` |
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

### States

```text
planned
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
  -> index-update-in-progress
  -> index-updated
  -> tw-handoff-in-progress
  -> reported-to-TW
  -> done
```

### State Ownership Table

| State / Transition | Owner | Required Condition |
|---|---|---|
| Dispatch outline | Orchestrator | Research issue unblocked |
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
| `final-promotion-ready` (Final Promotion Ready) | Research Agent | Final section persisted; Index Entry Proposal posted on research issue |
| `index-update-in-progress` | Orchestrator | Proposal validated against run ledger |
| `index-updated` | Orchestrator | Serialized `_index.md` commit completed |
| `tw-handoff-in-progress` | Research Agent | Posting Research Complete on TW reserved issue |
| `reported-to-TW` | Research Agent | Orchestrator supplied `_index.md` commit URL/SHA; Research Complete posted and Done Gate requested |
| `done` | Orchestrator | Done Gate passes (see Section 6) |

Only Orchestrator advances issue status. Worker agents may request status changes but cannot transition states directly.

## 6. Done Gate

A research issue may transition to `done` only when **all** of the following are true:

1. Outline consensus reached (state passed through `outline-approved`).
2. At least one Phase B draft was persisted before adversarial review.
3. The reviewed draft commit URL/SHA is recorded.
4. Adversarial Agent has posted approval, or Orchestrator posted explicit `accept-risk` for a major finding.
5. No unresolved critical finding remains.
6. Final section exists at `{project-slug}/research-sections/{topic-slug}/final.md`.
7. Orchestrator wrote the Index Entry Proposal into `{project-slug}/research-sections/_index.md` and recorded the commit.
8. Research Agent posted Research Complete on the TW reserved issue after `_index.md` commit, including: reviewed draft path, final section path, final commit, `_index.md` commit, and approval/accept-risk link.
9. Research Agent posted Done Gate Request on the research issue after TW handoff.
10. Orchestrator acknowledged the TW handoff comment with `seen`/ACK.
11. Orchestrator posted a closing comment summarizing outcome, artifact paths, TW handoff, and caveats.

## 7. Emoji Reaction Semantics

| Symbol | Alias | Meaning | Applied by | Notes |
|---|---|---|---|---|
| 👀 | `seen` | Message received, not acted upon | Orchestrator | **Not** approval |
| ✅ | `approved` | Gate pass | Orchestrator | Must be accompanied by state-transition comment |
| 🔄 | `action-needed` | Revision required | Orchestrator | Must be accompanied by action comment |

Blocked state is represented by a comment prefix (`BLOCKED:` or with warning emoji), **not** by reaction.

## 8. Message Type Templates

Every message comment must include: `issue_id`, `project_slug`, `topic_slug`, `phase`, `round`, `target_agent`, and `next_action`. Artifact-related messages must also include artifact paths and commit URL/SHA. Project-level messages without a research topic use `topic_slug: final-report`.

### 8.1 Dispatch

```markdown
## Dispatch: {phase}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: {outline | outline-review | deep-draft | draft-review | final-promotion | tw-handoff | final-report}
**Round**: {n}
**Target agent**: @{agent}
**Next action**: {explicit instruction}
**Inputs**: {paths or links}
```

### 8.2 Artifact Ready: Outline

```markdown
## Artifact Ready: outline

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: outline
**Round**: {n}
**Artifact**: {project-slug}/outlines/{topic-slug}.md
**Commit/URL**: {commit hash or permalink}
**Target agent**: @Orchestrator
**Next action**: Dispatch adversarial outline review
**Summary**: {1-2 sentences}
```

### 8.3 Artifact Ready: Deep Draft

```markdown
## Artifact Ready: deep-draft

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: deep-draft
**Round**: {n}
**Draft path**: {project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md
**Draft commit/URL**: {commit hash or permalink}
**Target agent**: @Orchestrator
**Next action**: Dispatch adversarial draft review
**Summary**: {1-2 sentences}
```

### 8.4 Review Verdict

```markdown
## Review Verdict: {approve | needs-attention | reject | outline-approved | outline-needs-revision}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: {outline-review | draft-review}
**Round**: {n}
**Artifact reviewed**: {outline path or draft path}
**Recommendation**: {approve | needs-attention | reject | outline-approved | outline-needs-revision}
**Severity**: {critical | major | minor | none}
**Findings**:
- {finding 1}
- {finding 2}
**Target agent**: @Orchestrator
**Next action**: {advance state | dispatch revision | accept-risk decision required | escalate}
```

### 8.5 Revision Request

```markdown
## Revision Request

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: {outline | deep-draft}
**Round**: {n} -> {n+1}
**Target agent**: @ResearchAgent
**Original artifact**: {outline path or draft path}
**Original artifact commit/URL**: {commit hash or permalink}
**Next artifact path**: {project-slug}/outlines/{topic-slug}.md (if outline) | {project-slug}/research-sections/{topic-slug}/drafts/round-{n+1}.md (if deep-draft)
**Required changes**:
- {change 1}
- {change 2}
**Next action**: Produce revised artifact and post Artifact Ready
```

### 8.6 Final Promotion Ready

```markdown
## Final Promotion Ready: {issue title}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: final-promotion
**Round**: {n}
**Reviewed draft**: {project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md
**Reviewed draft commit/URL**: {commit hash or permalink}
**Final section**: {project-slug}/research-sections/{topic-slug}/final.md
**Final commit/URL**: {commit hash or permalink}
**Adversarial approval or accept-risk**: {link}

**Index Entry Proposal**:
| order | topic_slug | multica_issue_id | final_path | dependencies | status |
|-------|-----------|-----------------|------------|--------------|--------|
| {order} | {topic-slug} | {multica_issue_id} | {project-slug}/research-sections/{topic-slug}/final.md | {upstream-slugs or -} | done |

**Target agent**: @Orchestrator
**Next action**: Validate proposal, serialize `_index.md` update, then dispatch TW handoff
```

### 8.7 Research Complete

Research Complete is posted on the **TW reserved issue** only after Orchestrator commits `_index.md`.

```markdown
## Research Complete: {issue title}

**Issue**: {multica_issue_id}
**Project slug**: {project-slug}
**Topic slug**: {topic-slug}
**Phase**: tw-handoff
**Round**: {n}
**Adversarial approval or accept-risk comment**: {link}
**Summary**: {2-3 sentences}
**Draft reviewed**: {project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md
**Draft reviewed commit/URL**: {commit hash or permalink}
**Final section**: {project-slug}/research-sections/{topic-slug}/final.md
**Final commit/URL**: {commit hash or permalink}
**Sections index**: {project-slug}/research-sections/_index.md
**Sections index commit/URL**: {commit hash or permalink from Orchestrator}
**Round count**: outline rounds={N}, deep rounds={M}
**Key findings**:
- {finding 1}
- {finding 2}
- {finding 3}
**Target agent**: @TechnicalWriter (via TW reserved issue)
**Next action**: Aggregate into final report
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
**Sections index commit/URL**: {commit hash or permalink from Orchestrator}
**Target agent**: @Orchestrator
**Next action**: Run Done Gate checklist and close research issue
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
**Target agent**: @Orchestrator
**Next action**: Human intervention or alternative path needed
```

### 8.10 Final Report Ready

```markdown
## Final Report Ready

**Issue**: {multica_tw_issue_id}
**Project slug**: {project-slug}
**Topic slug**: final-report
**Phase**: final-report
**Round**: 1
**Final report path**: {project-slug}/report/final-report.md
**Final report commit/URL**: {commit hash or permalink}
**Diagram assets path**: {project-slug}/report/assets/
**Diagram assets commit/URL**: {commit hash or permalink, or same as final report commit if committed together}
**Source sections aggregated**: {list of multica_issue_ids}
**Sections index**: {project-slug}/research-sections/_index.md
**Target agent**: @Orchestrator
**Next action**: Verify and close project
```

## 9. Two-Phase Adversarial Loop

### Phase A: Outline Consensus

1. Orchestrator dispatches outline work to Research Agent.
2. Research Agent uses `/research-outline` to generate a structured outline.
3. Research Agent persists the candidate outline at `{project-slug}/outlines/{topic-slug}.md` and posts **Artifact Ready: outline**.
4. Orchestrator dispatches outline review to Adversarial Agent.
5. Adversarial Agent uses `/research-review` and posts a **Review Verdict** (advisory).
6. Orchestrator decides: approve (advance to `outline-approved`) or revise (dispatch **Revision Request**).
7. On revision, Research Agent overwrites the same outline path and posts a new Artifact Ready with incremented round.

### Phase B: Draft Quality Check

1. Orchestrator dispatches deep draft work to Research Agent.
2. Research Agent uses `/research-deep-output` to produce a full research section draft.
3. Research Agent persists the draft at `{project-slug}/research-sections/{topic-slug}/drafts/round-{n}.md` and posts **Artifact Ready: deep-draft**.
4. Orchestrator dispatches draft review to Adversarial Agent.
5. Adversarial Agent reviews the **persisted draft** (not ephemeral chat text) and posts a **Review Verdict**.
6. Orchestrator decides: approve, accept-risk, or revise.

### Final Promotion

1. After approve or accept-risk, Research Agent writes `final.md` and posts **Final Promotion Ready** with Index Entry Proposal.
2. Orchestrator validates the proposal against the run ledger and serializes an `_index.md` commit.
3. Research Agent posts **Research Complete** on the TW reserved issue, including the `_index.md` commit URL/SHA, then posts **Done Gate Request** on the research issue.

## 10. Max-Round and Risk Escalation Policy

Each phase is capped at **3 rounds**. If round 3 still yields a revise / needs-attention / reject recommendation, Orchestrator must post a decision comment.

### Disposition Rules

| Severity | Action |
|---|---|
| **Critical** unresolved | Escalate to human. Do not approve. |
| **Major** unresolved | Escalate to human, or post explicit `accept-risk` with rationale. |
| **Minor** unresolved | May approve with caveats. Caveats must be copied to TW reserved issue. |

## 11. Technical Writer Reserved Issue

Planner always creates a dedicated TW reserved issue with the following required content:

| Field | Value |
|---|---|
| GitHub repo | `Whisker17/multica-research` |
| Project slug | `{project-slug}` |
| Research section index | Multica research issue IDs, `topic_slug`, draft convention, final path |
| Sections index path | `{project-slug}/research-sections/_index.md` |
| Final report path | `{project-slug}/report/final-report.md` |
| Diagram asset path | `{project-slug}/report/assets/` |
| Trigger condition | Begin only after all listed research issues have Research Complete comments with `_index.md` commit references |

**Assignment**: Prefer `agent:technical-writer-agent` label. Fallback: `agent_role: technical-writer-agent` in the issue description.

## 12. Index Entry Proposal Format

Research Agent includes this proposal in the Final Promotion Ready comment. Orchestrator validates and serializes the write to `_index.md`.

| Field | Description |
|---|---|
| `order` | Section order number (assigned by Planner) |
| `topic_slug` | Stable topic slug |
| `multica_issue_id` | Corresponding Multica research issue ID |
| `final_path` | `{project-slug}/research-sections/{topic-slug}/final.md` |
| `dependencies` | Upstream `topic_slug` list (or `-` if none) |
| `status` | `done` |

`_index.md` is **Orchestrator-owned**. Research Agent provides the proposal; Orchestrator performs the serialized commit and records the commit URL/SHA.

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
