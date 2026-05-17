# Orchestration Workflow Reference

## Inputs

- `project_id`: Multica project ID or name. Required in project mode. Optional context in single-issue mode.
- `anchor_issue_id`: optional issue used for preflight, run ledger, and orchestration comments. In single-issue mode, defaults to the research issue itself if omitted.
- `single_issue_id`: optional. When present, triggers single-issue mode.
- `report_issue_id`: optional in single-issue mode. TW reserved issue ID. Determines composable vs lightweight path.
- `project_slug`: optional in single-issue mode. Derived from issue context if omitted.
- Default GitHub repo: `Whisker17/multica-research`.

### Mode Selection

Mode is determined by parameter combination (mutually exclusive):

| Condition | Mode |
|---|---|
| `single_issue_id` present | Single-issue mode |
| `single_issue_id` absent, `project_id` present | Project mode (existing behavior) |
| Both absent | Error — require at least one |

## Agent Roster

| Agent | Responsibility |
|---|---|
| `project-planner-agent` | Issue design, dependency graph, slugs, artifact paths, TW reserved issue |
| `research-agent` | Outline, draft, final promotion, TW handoff |
| `research-adversarial-agent` | Outline and draft review |
| `technical-writer-agent` | Final report aggregation |

Research Agent and Adversarial Agent never communicate directly; Orchestrator relays all feedback.

## Preflight

Before dispatching workers, verify:

1. Multica can dispatch named agents.
2. Multica issue comments work.
3. Emoji reactions or text ACK fallback work.
4. Issue status changes work or can be requested.
5. GitHub artifacts can be read.
6. `_index.md` can be written to the target repo.
7. Parameters can be passed to worker agents.

If dispatch, comments, or parameter passing fail, stop and escalate. If `_index.md` write fails, hold affected issues at `final-promotion-ready` and do not dispatch TW handoff.

## Run Ledger

Store the ledger as JSON on the anchor issue (in single-issue mode, defaults to the research issue itself). Read it before decisions and update it before dispatches or state changes.

The ledger must include a top-level `mode` field: `project` or `single-issue`. On `/resume`, read this field to determine which flow to follow.

Required row fields:

| Field | Meaning |
|---|---|
| `issue_id` | Multica research issue ID |
| `project_slug`, `topic_slug` | Stable artifact identifiers |
| `phase` | Current state |
| `outline_round`, `deep_round` | Review loop counters |
| `blocked_by` | Upstream issue IDs not Done |
| `assigned_agent` | Current agent or `none` |
| `outline_path`, `draft_artifact_path`, `final_artifact_path` | Artifact paths |
| `draft_commit`, `final_commit`, `index_commit` | Commit references |
| `index_entry_proposal`, `index_committed` | Index write status |
| `tw_handoff_comment` | Research Complete comment URL |
| `next_action`, `updated_at` | Resume information |

Valid phases are defined in `squad-communication-protocol.md`.

## Dispatch Flow

1. Resolve anchor issue.
2. Run preflight and post results.
3. Dispatch Planner.
4. Validate plan quality:
   - every research issue has scope, expected output, slugs, order, artifact paths, diagram expectations when relevant, dependencies, and handoff formats;
   - dependencies form a DAG;
   - TW reserved issue exists and references all research issues.
5. Initialize ledger.
6. Dispatch up to 5 unblocked research issues.
7. For each issue:
   - outline generation;
   - adversarial outline review;
   - Orchestrator approval or revision;
   - deep draft generation;
   - adversarial draft review;
   - Orchestrator approval, revision, or accept-risk;
   - final promotion;
   - `_index.md` serialization;
   - TW handoff;
   - done gate.
8. Dispatch Technical Writer after all research issues are Done.
9. Verify final report and close the project.

## Dispatch Parameters

### Planner

Required: `project_id`, `project_description`, `github_repo`, `orchestrator_context`, `research_depth`, optional `project_slug`.

### Research Outline

Required: `multica_issue_id`, `topic`, `scope`, `expected_output`, `project_slug`, `topic_slug`, `report_issue_id`, `github_repo`, `round`.

### Outline Review

Required: `multica_issue_id`, `review_type=outline`, `artifact_path`, `artifact_commit`, `project_slug`, `topic_slug`, `github_repo`, `round`.

### Deep Draft

Required: `multica_issue_id`, `topic`, `project_slug`, `topic_slug`, `report_issue_id`, `github_repo`, `outline_path`, `round`.

### Draft Review

Required: `multica_issue_id`, `review_type=draft`, `artifact_path`, `artifact_commit`, `project_slug`, `topic_slug`, `github_repo`, `round`.

### Final Promotion (Composable — with `report_issue_id`)

Required: `multica_issue_id`, `promote=true`, `topic`, `project_slug`, `topic_slug`, `round`, `report_issue_id`, `github_repo`, `approved_draft_path`, `approved_draft_round`, `approved_draft_commit`, `approval_evidence`, `order`, `dependencies`.

### Final Promotion (Lightweight — no `report_issue_id`)

Required: `multica_issue_id`, `promote=true`, `topic`, `project_slug`, `topic_slug`, `round`, `github_repo`, `approved_draft_path`, `approved_draft_round`, `approved_draft_commit`, `approval_evidence`.

Not required: `order`, `dependencies`, `report_issue_id`. No Index Entry Proposal is produced.

### TW Handoff

Required: `multica_issue_id`, `project_slug`, `topic_slug`, `report_issue_id`, `github_repo`, `final_commit`, `sections_index_commit`, `approved_draft_path`, `approved_draft_commit`, `outline_rounds`, `deep_rounds`, `round`, `order`, `approval_evidence`.

Skipped entirely in lightweight single-issue mode (no `report_issue_id`).

### Technical Writer

Required: `project_id`, `report_issue_id`, `project_slug`, `github_repo`.

## `_index.md` Serialization

Only Orchestrator writes `{project_slug}/research-sections/_index.md`.

Validate each Index Entry Proposal against the ledger and Planner-assigned `order`. Rewrite the full table sorted by `order`, commit one issue entry per commit, record the commit in the ledger, then dispatch TW handoff.

## Done Gates

### Project Mode / Composable Single-Issue (with `report_issue_id`)

Research issue Done requires all 11 items:

1. Outline consensus reached.
2. At least one Phase B draft persisted before adversarial review.
3. Reviewed draft commit URL/SHA recorded.
4. Adversarial approve or Orchestrator accept-risk.
5. No unresolved critical finding.
6. Final section persisted at `{project_slug}/research-sections/{topic_slug}/final.md`.
7. `_index.md` committed with this issue's entry.
8. Research Complete posted to TW reserved issue (with `_index.md` commit).
9. Done Gate Request posted on research issue.
10. Orchestrator ACK'd TW handoff comment.
11. Orchestrator posted closing comment on research issue.

### Lightweight Single-Issue (no `report_issue_id`)

Research issue Done requires all 8 items:

1. Outline consensus reached.
2. At least one Phase B draft persisted before adversarial review.
3. Reviewed draft commit URL/SHA recorded.
4. Adversarial approve or Orchestrator accept-risk.
5. No unresolved critical finding.
6. Final section persisted at `{project_slug}/research-sections/{topic_slug}/final.md`.
7. Final Promotion Ready posted on research issue with final section path and commit; Index Entry Proposal is not required.
8. Orchestrator posted closing comment on research issue.

### TW Done

TW Done requires final report, source traceability, completion comment, review gate index, unresolved risk summary, and diagram assets when present.

## Risk Policy

Each review phase has max 3 rounds.

- Critical unresolved: block and escalate; never accept.
- Major unresolved: escalate or explicit `accept-risk`, mirrored to TW.
- Minor or known gap: may proceed with documented caveat.

Use `squad-communication-protocol.md` for exact comment templates.

## Single-Issue Dispatch Flow

When `single_issue_id` is present, follow this flow instead of the full project dispatch:

1. Read the research issue. Extract `topic`, `project_slug`, `topic_slug`, `scope`, `expected_output` from the issue title and description. If `project_slug` is passed as a parameter, use that. If information is insufficient, comment on the issue requesting clarification.
2. Check for existing `final.md` at `{project_slug}/research-sections/{topic_slug}/final.md`. If it exists and no active ledger with phase < `done`, refuse and comment. If active ledger exists, resume.
3. Set anchor issue to `anchor_issue_id` if provided, otherwise to `single_issue_id`.
4. Run simplified preflight: verify dispatch, comments, parameter passing, GitHub artifact read/write. If `report_issue_id` is present, also verify `_index.md` write capability.
5. Initialize single-row ledger with `mode: single-issue` on the anchor issue.
6. Dispatch research outline (single issue, not batch).
7. Route through the standard adversarial loop: outline review → approval → deep draft → draft review → approval.
8. Dispatch final promotion.

### Lightweight Path (no `report_issue_id`)

9. After Final Promotion Ready, run 8-item Done Gate.
10. Post closing comment on research issue. This is a terminal action — no @-mention of next agent required.
11. Mark issue Done.

### Composable Path (with `report_issue_id`)

9. After Final Promotion Ready, validate Index Entry Proposal. Determine `order` by reading existing `_index.md` and taking max(order) + 1.
10. Serialize `_index.md` commit.
11. Dispatch TW handoff — Research Agent posts Research Complete on TW reserved issue.
12. Run 11-item Done Gate.
13. Post closing comment on research issue. This is a terminal action — no @-mention required unless user requests TW aggregation.
14. Mark issue Done. TW dispatch is not triggered — user may dispatch TW manually later.

### Handoff Rules

- **Continuous tasks** (handoff required): completion messages must explicitly @-mention the next agent in both `Target agent` and `Next action` fields.
- **Terminal tasks** (stoppable): closing comments, BLOCKED messages, and awaiting-human-input states do not require @-mentioning a next agent. Use `Target agent: none` / `Next action: none` or `Next action: awaiting human input`.

### Issue Information Extraction

In single-issue mode, extract from the issue (not from Planner output):

| Field | Source |
|---|---|
| `topic` | Issue title or description |
| `project_slug` | Parameter, issue description, or Orchestrator-generated |
| `topic_slug` | Issue description or Orchestrator-generated |
| `scope`, `expected_output` | Issue description |
| `github_repo` | Default `Whisker17/multica-research` |
| `order` | Only with `report_issue_id`: read `_index.md`, max(order) + 1 |
| `dependencies` | Only with `report_issue_id`: from issue description or default `-` |
