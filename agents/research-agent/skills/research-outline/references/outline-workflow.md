# Outline Workflow Reference

## Inputs

- `topic`
- `project_slug`
- `topic_slug`
- `github_repo`, default `Whisker17/multica-research`
- `branch_name`, default `research/{project_slug}/{topic_slug}`
- optional `artifact_paths`, `scope`, `audience`, `expected_output`, `source_requirements`, `diagram_expectations`, `codebase_path`

## Topic Landscape

Before designing the outline:

1. Run 3-5 targeted searches.
2. Inspect codebase when `codebase_path` is provided.
3. Calibrate scope, breadth, and depth.

Use `research-methodology.md` when choosing source expectations.

## Items

Create 4-8 researchable items.

Good items are:

- collectively comprehensive;
- minimally overlapping;
- similar granularity;
- logically ordered;
- explicit about dependencies.

Each item needs a title, description, priority, and dependencies.

## Fields

Create 5-10 fields.

Fields should be answerable, comparable, domain-appropriate, and balanced between factual and analytical dimensions. Use snake_case field names.

Assign each field to `all` or specific item IDs.

## Diagrams

Plan 2-5 diagrams when useful. Prefer diagrams for architecture, flows, comparison matrices, timelines, decision trees, and governance structures.

Research-stage diagrams use Mermaid or ASCII only.

## Source Requirements

Define minimum source types and counts. Prefer primary sources and include special requirements such as audits, code analysis, on-chain data, or governance proposals when relevant.

## Persistence

Before writing, fetch the target repo and switch to `branch_name`. If the branch does not exist, create it from latest `origin/main` and push it. If the runtime starts on a random agent branch, do not write artifacts there; switch to `branch_name` first.

Read `research-outline-schema.md`, assemble frontmatter and body, then persist to:

`{project_slug}/outlines/{topic_slug}.md`

Set:

- `round: 1`
- `status: candidate`
- creation metadata
- empty Patch Log

Commit and push to `branch_name`. Return outline content, work branch commit URL/SHA, slugs, repo, branch name, and artifact paths.

## Quality Checklist

- required frontmatter present;
- 4-8 clear items;
- 5-10 useful fields;
- at least 2 diagram expectations unless not useful and explicitly justified;
- source requirements defined;
- Patch Log present;
- `topic_slug` is not a Linear issue ID;
- artifact paths match provided or computed paths.
- current git branch matches `branch_name`.

## Error Handling

- Missing GitHub auth or failed push: BLOCKED.
- Topic too vague: ask for narrower scope.
- Missing `project_slug` or `topic_slug`: BLOCKED.
- Linear-style `topic_slug`: BLOCKED.
