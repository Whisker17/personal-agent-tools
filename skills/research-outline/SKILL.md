---
name: research-outline
description: >
  Generate structured research outlines for systematic investigation. Breaks a research topic
  into researchable items, defines investigation fields, identifies diagram opportunities, and
  specifies source requirements. Output conforms to the shared outline schema used across the
  research squad workflow. Use this skill whenever you need to plan research, create a research
  outline, structure an investigation, or break a research topic into researchable components.
  Trigger on: 'outline this topic', 'plan the research', 'what should we investigate',
  'structure this research', 'create an outline', or any request to organize structured research.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - WebSearch
  - WebFetch
---

# /research-outline

Generate a structured research outline for a given topic. The outline breaks the topic into researchable items, defines investigation fields, identifies diagram opportunities, and specifies source requirements.

The outline conforms to the shared schema at `knowledge/shared/research-outline-schema.md` — read it before generating.

## Input

The invoking agent provides these parameters:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `topic` | yes | The research question or subject |
| `project_slug` | yes | Stable project identifier |
| `topic_slug` | yes | Stable topic identifier (never a Linear issue ID) |
| `github_repo` | no | GitHub repo for persistence. Default: `Whisker17/multica-research` |
| `artifact_paths` | no | Object with `outline`, `draft`, `final`, `index` paths. If provided by Orchestrator, use these verbatim. If omitted, compute from `project_slug` and `topic_slug` per the schema |
| `scope` | no | What aspects to cover. Infer from topic if not provided |
| `audience` | no | Who will read the output. Default: "technical researchers and decision-makers" |
| `expected_output` | no | What form the deliverable takes. Default: "structured research section with source attribution" |
| `source_requirements` | no | Specific source types needed |
| `diagram_expectations` | no | Specific diagrams needed |
| `codebase_path` | no | Local repo path for codebase analysis |

## Process

### Step 1: Understand the Topic Landscape

Before designing the outline structure, build a mental model of the topic:

1. **Web research** — run 3-5 targeted searches to understand:
   - What are the key components/aspects of this topic?
   - What are the major debates or open questions?
   - What data sources exist?
   - Who are the key players or projects?

2. **Codebase analysis** (if `codebase_path` provided) — scan the codebase to understand:
   - Architecture and module structure
   - Key abstractions and interfaces
   - Dependencies and integrations
   - What the code reveals that documentation might not

3. **Scope calibration** — based on research, decide:
   - Is the topic too broad? Narrow it to the most impactful slice.
   - Is the topic too narrow? Consider expanding to include necessary context.
   - What's the right depth vs breadth balance for this audience?

### Step 2: Design Items

Break the topic into 4-8 researchable items. Each item is a subtopic that can be independently investigated.

Design principles:
- **Comprehensive coverage**: together, items should cover the full scope of the research question. A reader who reads all items' findings should have a complete picture.
- **Minimal overlap**: each item should cover a distinct aspect. If two items overlap significantly, merge them or sharpen their boundaries.
- **Consistent granularity**: items should be at roughly the same abstraction level and require similar research effort.
- **Logical ordering**: items should flow in an order that builds understanding — foundational concepts before applied analysis, architecture before optimization.
- **Clear dependencies**: if item B requires understanding item A's findings, mark that dependency explicitly.

For each item, write a description that tells the deep researcher exactly what to investigate and why it matters for the overall research question.

### Step 3: Define Fields

Design 5-10 investigation fields — the dimensions or lenses applied to each item during deep research.

Design principles:
- **Answerable**: each field should produce concrete findings, not vague observations. "security_audit_status" is better than "security_thoughts".
- **Comparable**: fields that apply to multiple items should produce findings that can be compared across items. This enables cross-cutting analysis.
- **Domain-appropriate**: choose fields that match the topic's domain. Technical topics need architecture and implementation fields; market topics need metrics and competitive fields.
- **Balanced**: mix factual fields (what exists) with analytical fields (why it matters, what could go wrong).

Assign each field to either `all` items or specific item IDs. Fields applying to `all` are the core investigation dimensions; item-specific fields capture unique angles.

### Step 4: Specify Diagram Expectations

Identify 2-5 diagrams that would enhance the research output. Diagrams are especially valuable for:
- System architectures and component relationships
- Data flows and processing pipelines
- Comparison matrices across items
- Timelines and evolution
- Decision trees and governance flows

Use `mermaid` format for structured diagrams (flowcharts, sequence diagrams, class diagrams) and `ascii` for simpler visualizations.

### Step 5: Define Source Requirements

Specify minimum source expectations to ensure research thoroughness. Consider:
- What types of sources are most authoritative for this topic?
- What minimum coverage ensures the research isn't single-source dependent?
- Are there specific source types that are essential (e.g., audit reports for security topics)?

### Step 6: Assemble and Persist

1. Read `knowledge/shared/research-outline-schema.md` to confirm the output format.

2. Resolve `artifact_paths`: if the invoking agent provided `artifact_paths`, use them verbatim. Otherwise compute from `project_slug` and `topic_slug`:
   - outline: `{project_slug}/outlines/{topic_slug}.md`
   - draft: `{project_slug}/research-sections/{topic_slug}/drafts/round-{n}.md`
   - final: `{project_slug}/research-sections/{topic_slug}/final.md`
   - index: `{project_slug}/research-sections/_index.md`

3. Assemble the outline document following the schema's frontmatter + body format.

4. Set initial values:
   - `round: 1`
   - `status: candidate`
   - `revision_metadata.created_by`: your agent identifier
   - `revision_metadata.created_at`: current ISO-8601 timestamp
   - Patch Log: empty

5. Persist to GitHub. Use the resolved `artifact_paths.outline` as the write path; do not recompute a different path at write time. Replace the `{assembled outline content}` placeholder with the actual outline before running the command.

```bash
REPO="<github_repo or Whisker17/multica-research>"
TOPIC_SLUG="<topic_slug>"
OUTLINE_PATH="<resolved artifact_paths.outline>"

REPO_DIR=$(mktemp -d)
gh repo clone "$REPO" "$REPO_DIR"
cd "$REPO_DIR"

mkdir -p "$(dirname "$OUTLINE_PATH")"

cat > "$OUTLINE_PATH" << 'OUTLINE_EOF'
{assembled outline content}
OUTLINE_EOF

git add .
git commit -m "research-outline: ${TOPIC_SLUG} (round 1)"
git push
COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_URL=$(gh api repos/${REPO}/commits/${COMMIT_SHA} --jq '.html_url')

cd -
rm -rf "$REPO_DIR"
```

6. Report back to the invoking agent with:
   - The outline content (for immediate use)
   - The commit URL and SHA (for audit trail)
   - `project_slug`, `topic_slug`, `github_repo`, and all `artifact_paths.*` values for downstream reference

## Output

The output is the persisted outline document conforming to `knowledge/shared/research-outline-schema.md`, plus a summary:

```
Outline created: {topic}
Path: {artifact_paths.outline}
Commit URL: {commit_url}
Commit SHA: {commit_sha}
Project slug: {project_slug}
Topic slug: {topic_slug}
GitHub repo: {github_repo}
Artifact paths:
- outline: {artifact_paths.outline}
- draft: {artifact_paths.draft}
- final: {artifact_paths.final}
- index: {artifact_paths.index}
Items: {count} ({high_priority_count} high, {medium_count} medium, {low_count} low)
Fields: {count} ({all_count} universal, {specific_count} item-specific)
Diagrams: {count}
Source requirements: {count} types, {total_min} minimum sources
Status: candidate (awaiting Orchestrator approval)
```

## Quality Checklist

Before persisting, verify:

- [ ] All frontmatter fields present (topic, project_slug, topic_slug, github_repo, round, status, artifact_paths, scope, audience, expected_output, revision_metadata)
- [ ] 4-8 items with clear descriptions, priorities, and dependencies
- [ ] 5-10 fields with descriptions and applies_to assignments
- [ ] At least 2 diagram expectations
- [ ] Source requirements defined
- [ ] Patch Log section present (empty for round 1)
- [ ] No Linear issue IDs used as topic_slug
- [ ] If `artifact_paths` was provided, the output uses those exact paths; if omitted, paths are computed correctly from project_slug and topic_slug
- [ ] Outline is reviewable — an adversarial agent reading it should understand what each item covers and be able to identify gaps

## Error Handling

- `gh` not available or not authenticated: **BLOCKED**. The outline must be persisted before adversarial review. Do not return the outline as a reviewable fallback.
- GitHub push fails: retry once. If it still fails, **BLOCKED** and report the intended outline path.
- Topic too vague (e.g., "blockchain"): ask the invoking agent to narrow the scope before generating.
- `project_slug` or `topic_slug` missing: these are required orchestration context. Report the error — do not invent slugs.
- `topic_slug` matches a Linear-style ID such as `WHI-123`: **BLOCKED**. Ask Orchestrator for the stable topic slug.
