# PR Analysis Workflow

## Status Segmentation

Use these buckets:

- `draft`: PRs currently marked draft and created or updated in the period.
- `open`: non-draft open PRs created or updated in the period.
- `merged`: PRs merged in the period.
- `closed_unmerged`: PRs closed in the period without merge.

When the same PR has multiple events in a period, keep it in the event bucket and preserve `current_status`.

## Key PR Ranking

Rank PRs by:

1. Focus match in title, labels, body, changed files, or module.
2. Merged PRs and releases before open PRs, unless a draft/open PR is very large or strategic.
3. Size: additions + deletions, changed files, and touched modules.
4. Architectural signals: new modules, dependencies, protocol changes, security changes, migrations.
5. Team signals: new contributor, unusually long/short review time, many reviewers/comments.

Each Key PR should include:

- repo, number, title, current_status, event_types
- author, labels, additions, deletions, changed_files
- modules, focus_matches, importance_score
- `content_signals`: PR body excerpt, changed files, touched modules, commit subjects
- evidence summary suitable for weekly/monthly analysis

## PR Content Understanding

For every Key PR, write a short interpretation based on:

1. PR body: stated goal, migration notes, risks, or rollout plan.
2. Changed files: which product area or module is actually touched.
3. Commit subjects: implementation steps inside the PR.
4. Size and review time: whether this is a small fix, active feature work, or larger architecture change.

If body/files/commits are missing, say content was unavailable and lower confidence.

## Weekly and Monthly Synthesis

Use Key PRs as the spine of the report:

- Group Key PRs by product area or module.
- Compare this period with the previous period when aggregate data exists.
- Convert repeated PR evidence into engineering trend statements.
- Call out uncertainty when only draft/open PRs support a trend.

Avoid conclusions that are only based on commit count unless PR data is missing.
