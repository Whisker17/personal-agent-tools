# Planning Workflow Reference

## Inputs

- `project_id`: Multica project ID.
- `project_description`: full project description.
- `github_repo`: optional target repo, default `Whisker17/multica-research`.
- `orchestrator_context`: origin issue/comment context.
- `research_depth`: `quick-scan`, `standard`, or `deep-dive`.
- `project_slug`: optional pre-defined slug.

## Access Checks

1. Fetch the project and existing issues.
2. Resolve target repo.
3. Verify GitHub write access before designing artifacts.
4. Do not substitute a different repo when access fails; post `BLOCKED`.

## Slugs

- `project_slug`: derived from project title, lowercase, hyphen-separated, stable, no Linear IDs.
- `topic_slug`: one per research issue, human-readable, stable, no Linear IDs.
- Slugs must match `^[a-z0-9][a-z0-9-]*[a-z0-9]$`; spaces, uppercase letters, underscores, slashes, and issue IDs are invalid because slugs become artifact paths and git branch segments.
- Record the project slug derivation in Planner Complete.

## Research Issue Template

Every research issue must include:

- Goal
- Research Scope
- Out of Scope
- Key Questions
- Expected Output
- Required Evidence / Sources
- Diagram Expectations
- Artifact Paths
- Artifact and Handoff Contract
- Dependencies
- Done Criteria
- Agent Assignment
- Final Promotion Ready Format
- TW Research Complete Format

Use `squad-communication-protocol.md` for exact message templates and `example-structures.md` for complete examples.

## Parallel Waves

- Max 5 research issues per wave.
- Only real artifact/data dependencies block later waves.
- Reading order is separate from execution order and is captured by deterministic `order` values for `_index.md`.
- Output wave assignments, block graph edges, and real-dependency explanations.

## Technical Writer Reserved Issue

Create exactly one TW reserved issue. It must include:

- Research Section Index
- GitHub repo and project slug
- sections index path
- final report path
- diagram assets path
- trigger condition
- Research Complete format
- Final Report Ready format
- Orchestrator-only dispatch note
- dependencies blocked by all research issues
- `agent:technical-writer-agent` label or `agent_role:` fallback

## Creation Order

1. Present plan for approval.
2. Create agent assignment labels.
3. Create research issues.
4. Create TW reserved issue.
5. Attach labels.
6. Backfill dependencies with actual issue IDs.
7. Post Planner Complete on the Orchestrator issue.

## Multica CLI Notes

- Use `--description-file` for multi-line markdown.
- Use `--output json` when capturing IDs.
- If label creation fails, use `agent_role:` fallback and document the limitation.

## Planner Complete

Include:

- project title, slug, slug derivation, repo;
- created issue IDs, topic slugs, order, wave;
- artifact paths;
- sections index, final report, assets path;
- parallel waves and block graph;
- TW reserved issue ID;
- risks and ambiguities;
- Orchestrator mention link from `multica agent list` (`[@Orchestrator](mention://agent/{id})`) in `Target agent`, with `Next action` naming Orchestrator in plain text.
