# Research Outline Schema

last_updated: 2026-05-16

This is the shared schema used by `/research-outline`, `/research-review`, and `/research-deep-output`. All three commands produce and consume outlines conforming to this schema. Fields marked **required** must always be present and must never be dropped during patching or revision.

## Outline Document Format

The outline is persisted as a markdown file with YAML frontmatter. The frontmatter contains machine-readable metadata; the body contains the human-readable outline content.

### Frontmatter Fields

```yaml
# --- Required Metadata ---
topic: string              # The research question or subject
project_slug: string       # Stable project identifier (provided by Planner/Orchestrator)
topic_slug: string         # Stable topic identifier (provided by Planner/Orchestrator, never a Linear issue ID)
github_repo: string        # GitHub repo (owner/name) for persistence. Default: Whisker17/multica-research
round: integer             # Current revision round (starts at 1, incremented by /research-review)
status: candidate | approved  # candidate until Orchestrator approves

# --- Artifact Paths (required, computed from project_slug and topic_slug) ---
artifact_paths:
  outline: "{project_slug}/outlines/{topic_slug}.md"
  draft: "{project_slug}/research-sections/{topic_slug}/drafts/round-{n}.md"
  final: "{project_slug}/research-sections/{topic_slug}/final.md"
  index: "{project_slug}/research-sections/_index.md"

# --- Research Scope (required) ---
scope: string              # What aspects to cover
audience: string           # Who will read the final output
expected_output: string    # What form the final deliverable takes

# --- Revision Metadata (required) ---
revision_metadata:
  created_by: string       # Agent that created this outline
  created_at: ISO-8601     # Creation timestamp
  last_modified_by: string # Agent that last modified this outline
  last_modified_at: ISO-8601
```

### Body Structure

The markdown body follows this exact section order. Sections may be empty but headers must be present so downstream tools can locate and parse them.

```markdown
# Research Outline: {topic}

## Items

### item-1: {Item Title}

{Description of what to investigate — 2-4 sentences explaining scope and why it matters}

- **Priority**: high | medium | low
- **Dependencies**: none | item-2, item-3

### item-2: {Item Title}
...

## Fields

| Field | Description | Applies To |
|-------|-------------|------------|
| {field_name} | {What this field captures for each item} | all | item-1, item-3 |

## Diagram Expectations

| ID | Type | Description | Format | Applies To |
|----|------|-------------|--------|------------|
| diag-1 | {architecture/flow/comparison/timeline/...} | {What the diagram should show} | mermaid / ascii | all / item-1, item-2 |

## Source Requirements

| ID | Type | Description | Min Count |
|----|------|-------------|-----------|
| src-1 | {official_docs/academic_papers/on_chain_data/audit_reports/...} | {What kind of sources} | {N} |

## Patch Log

| Round | Action | Target | Reason | Source |
|-------|--------|--------|--------|--------|
```

## Field Definitions

### Items

Items are the researchable subtopics that together cover the full research question. Each item should be independently investigable but may depend on other items for context.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | yes | Stable identifier, format: `item-{N}` |
| title | string | yes | Descriptive title |
| description | string | yes | 2-4 sentences: what to investigate and why |
| priority | enum | yes | `high` / `medium` / `low` — guides research depth allocation |
| dependencies | string[] | yes | IDs of items that should be researched first. `none` if independent |

Guidelines:
- 4-8 items for a typical topic. Under 4 means the topic may be too narrow; over 8 means it should be split.
- Items should be at roughly the same abstraction level — don't mix "Protocol Architecture" with "Logo Color Choice".
- Dependencies indicate research order, not strict blocking. An item can start before its dependency finishes, but the dependency's findings may inform it.

### Fields

Fields are the dimensions or lenses applied to each item during deep research. They define _what to find out_ about each item.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | yes | Snake_case field name |
| description | string | yes | What this field captures |
| applies_to | string | yes | `all` or comma-separated item IDs |

Guidelines:
- 5-10 fields for a typical outline. Fields that apply to `all` items are the core investigation dimensions.
- Item-specific fields are useful when certain items have unique angles not shared by others.
- Field names should be noun phrases: `security_model`, `competitive_landscape`, `governance_structure`.

### Diagram Expectations

Diagrams the deep research phase should produce.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | yes | Stable identifier, format: `diag-{N}` |
| type | string | yes | Category: architecture, flow, comparison, timeline, hierarchy, network |
| description | string | yes | What the diagram should convey |
| format | enum | yes | `mermaid` or `ascii` (research phase uses these; Technical Writer converts later) |
| applies_to | string | yes | `all` or comma-separated item IDs |

### Source Requirements

Minimum source expectations for the research to be considered thorough.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| id | string | yes | Stable identifier, format: `src-{N}` |
| type | string | yes | Source category |
| description | string | yes | What kind of sources are needed |
| min_count | integer | yes | Minimum number of sources of this type |

Common source types: `official_docs`, `academic_papers`, `on_chain_data`, `audit_reports`, `governance_proposals`, `industry_reports`, `expert_commentary`, `code_analysis`.

### Patch Log

Records every modification made to the outline after initial creation. Populated by `/research-review`, not by `/research-outline` (which creates round 1 with an empty log).

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| round | integer | yes | Which revision round |
| action | string | yes | What changed: `add_item`, `remove_item`, `modify_item`, `add_field`, `remove_field`, `modify_field`, `add_diagram`, `remove_diagram`, `modify_diagram`, `add_source_req`, `modify_source_req` |
| target | string | yes | ID or name of the changed element |
| reason | string | yes | Why the change was made |
| source | string | yes | Who made the change: agent identifier |

### Artifact Paths

These paths are **computed, not user-provided**. They are derived from `project_slug` and `topic_slug` and must be consistent across all three skills.

| Path | Template | Written By |
|------|----------|------------|
| outline | `{project_slug}/outlines/{topic_slug}.md` | `/research-outline` (create), `/research-review` (patch) |
| draft | `{project_slug}/research-sections/{topic_slug}/drafts/round-{n}.md` | `/research-deep-output` |
| final | `{project_slug}/research-sections/{topic_slug}/final.md` | `/research-deep-output` (after quality gate) |
| index | `{project_slug}/research-sections/_index.md` | Orchestrator only |

## Invariants

These rules must hold across all three skills:

1. `project_slug`, `topic_slug`, `github_repo`, and `artifact_paths.*` must never be dropped or modified during patching.
2. `topic_slug` must never be a Linear issue ID (e.g., `WHI-123`). It must be a stable, human-readable slug.
3. `round` starts at 1 and increments by 1 with each `/research-review` pass.
4. `status` starts as `candidate`. Only the Orchestrator sets it to `approved`.
5. The Patch Log is append-only. Previous entries must never be modified or removed.
6. Item IDs (`item-{N}`) are stable once assigned. Removing an item leaves a gap in numbering — do not renumber.
7. `github_repo` defaults to `Whisker17/multica-research` if not provided.
