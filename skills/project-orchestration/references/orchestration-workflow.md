# Orchestration Workflow Reference

## Inputs

- `project_id`: Multica project ID or name.
- `anchor_issue_id`: optional issue used for preflight, run ledger, and orchestration comments.
- Default GitHub repo: `Whisker17/multica-research`.

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

Store the ledger as JSON on the anchor issue. Read it before decisions and update it before dispatches or state changes.

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

### Final Promotion

Required: `multica_issue_id`, `promote=true`, `topic`, `project_slug`, `topic_slug`, `round`, `report_issue_id`, `github_repo`, `approved_draft_path`, `approved_draft_round`, `approved_draft_commit`, `approval_evidence`, `order`, `dependencies`.

### TW Handoff

Required: `multica_issue_id`, `project_slug`, `topic_slug`, `report_issue_id`, `github_repo`, `final_commit`, `sections_index_commit`, `approved_draft_path`, `approved_draft_commit`, `outline_rounds`, `deep_rounds`, `round`, `order`, `approval_evidence`.

### Technical Writer

Required: `project_id`, `report_issue_id`, `project_slug`, `github_repo`.

## `_index.md` Serialization

Only Orchestrator writes `{project_slug}/research-sections/_index.md`.

Validate each Index Entry Proposal against the ledger and Planner-assigned `order`. Rewrite the full table sorted by `order`, commit one issue entry per commit, record the commit in the ledger, then dispatch TW handoff.

## Done Gates

Research issue Done requires:

1. approved outline persisted;
2. reviewed draft persisted;
3. adversarial approve or Orchestrator accept-risk;
4. no unresolved critical finding;
5. final section persisted;
6. Final Promotion Ready posted;
7. `_index.md` committed;
8. Research Complete posted to TW issue;
9. Done Gate Request posted on research issue.

TW Done requires final report, source traceability, completion comment, review gate index, unresolved risk summary, and diagram assets when present.

## Risk Policy

Each review phase has max 3 rounds.

- Critical unresolved: block and escalate; never accept.
- Major unresolved: escalate or explicit `accept-risk`, mirrored to TW.
- Minor or known gap: may proceed with documented caveat.

Use `squad-communication-protocol.md` for exact comment templates.
