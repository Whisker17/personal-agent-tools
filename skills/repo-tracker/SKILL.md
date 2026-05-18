---
name: repo-tracker
description: "Use when generating competitive intelligence from GitHub repo PR activity, especially status-segmented PR summaries, key PR analysis, weekly/monthly engineering trend synthesis, or Multica autopilot repo-tracker reports."
---

# Repo Tracker

Generate repo intelligence from PR activity. Treat PRs as the primary signal; commits and releases are supporting evidence.

## References

Load only when needed:

- `references/pr-analysis-workflow.md` - PR status segmentation, key PR ranking, and trend synthesis.
- `references/report-templates.md` - daily, weekly, monthly report skeletons.

## Scripts

Deterministic work belongs to scripts. The agent prompt handles analysis and reporting only.

- `skills/repo-tracker/scripts/tracker-fetch.py`: GitHub API data collection, commit classification, module inference, and daily JSON generation.
- `skills/repo-tracker/scripts/tracker-persist.py`: JSON upsert into the tracker data repo, including `sha` handling and one retry after a `409` conflict.
- `skills/repo-tracker/scripts/tracker-aggregate.py`: weekly or monthly aggregation from persisted daily summary Markdown plus daily JSON snapshots, including coverage reporting.

## Time Window

Daily reports use a natural day in the configured `Timezone`, not a sliding 24 hour window. A normal 09:00 cron run for May 19 in `Asia/Shanghai` reports May 18:

- `since`: `2026-05-18T00:00:00+08:00`
- `until`: `2026-05-19T00:00:00+08:00`

Cron delay must not change the target natural day. Manual reruns of the same day overwrite the same path through `tracker-persist` upsert.

## GitHub API Scope

Use the data returned by scripts as the source of truth. The intended data scope is:

- PRs: opened by `created_at`, merged by `merged_at`, closed unmerged by `closed_at` with no `merged_at`.
- Commits: only commits on the repo default branch.
- Releases: non-draft releases with `published_at` inside the window.
- Contributors: unique authors found in commits and merged PRs.

PR event counts are independent. A PR opened and merged in the same natural day may appear in both opened and merged.

## Workflow

### Daily Flow

1. Parse input parameters.
2. Run `skills/repo-tracker/scripts/tracker-fetch.py --repos "<repos>" --timezone "<Timezone>"`.
3. If the script exits `2`, write a `[FAILED] Daily Competitive Intelligence` report with the stderr summary and stop.
4. Save stdout JSON to a temporary file.
5. Run `skills/repo-tracker/scripts/tracker-persist.py --data-repo "<Data repo>" --path "daily/{report_date}.json" --file "<tmpfile>"`.
6. Generate the daily Markdown report from the JSON, even if JSON persistence fails.
7. Persist the daily summary Markdown to GitHub using `skills/repo-tracker/scripts/tracker-persist.py --print-report-path --report-type daily --date "{report_date}" --project "{project}"`, then upsert that path.
8. Include `Data Notes` with `coverage`, errors, GitHub Markdown summary path, and JSON snapshot status.

### Weekly Flow

1. Parse input parameters.
2. Run `skills/repo-tracker/scripts/tracker-aggregate.py --data-repo "<Data repo>" --type weekly --end-date "<report_date>" --days 7 --repos "<repos>" --timezone "<Timezone>" --project "{project}" --gap-fill`.
3. Save stdout JSON to a temporary file.
4. Generate the weekly report primarily from `daily_summaries`, using aggregate JSON as supporting metrics.
5. Persist weekly Markdown to the GitHub path containing `weeks-summarys`, for example `2026/05/16-22/weeks-summarys/project-A/202605-week-summary.md`.
6. Emphasize Key PR themes, focus shifts, contributor changes, delivery velocity, releases, and anomalies.

### Monthly Flow

1. Parse input parameters.
2. Run `skills/repo-tracker/scripts/tracker-aggregate.py --data-repo "<Data repo>" --type monthly --end-date "<report_date>" --days 30 --repos "<repos>" --timezone "<Timezone>" --project "{project}" --gap-fill`.
3. Save stdout JSON to a temporary file.
4. Generate the monthly report primarily from `daily_summaries`, using aggregate JSON as supporting metrics.
5. Persist monthly Markdown to the GitHub path containing `months-summarys`, for example `2026/05/months-summarys/project-A/202605-month-summary.md`.
6. If `Self repo` is present, include a competitive comparison section.
7. Keep roadmap inference tied to evidence and include confidence levels.

## Script Exit Handling

For `skills/repo-tracker/scripts/tracker-fetch.py`:

- Exit `0`: generate a normal report.
- Exit `1`: generate a report from available data and mark `coverage` as partial in `Data Notes`.
- Exit `2`: write a failed report and stop.

For `skills/repo-tracker/scripts/tracker-persist.py`:

- Exit `0`: record JSON snapshot as committed.
- Exit `1`: still output the report and state `JSON snapshot: failed` in `Data Notes`.

For `skills/repo-tracker/scripts/tracker-aggregate.py`:

- Exit `0`: generate a normal aggregate report.
- Non-zero: write a failed report with the script stderr summary.

## Output Contract

The Multica issue title should be:

```text
[Daily/Weekly/Monthly] Competitive Intelligence - {report_date}
```

The issue body must be Markdown and include:

- Report heading.
- Window or period.
- Repos tracked.
- Overview table.
- Highlights or executive summary.
- Key PRs.
- PR status breakdown with draft, open, merged, and closed-unmerged sections.
- Per-PR content understanding for every Key PR: what changed, evidence from body/files/commits, and why it matters.
- Per-repo details for daily reports.
- Trend sections for weekly and monthly reports.
- `Data Notes`.

## Persistence Layout

Persist every report output into the configured GitHub `Data repo`.

Daily summary path:

```text
{YYYY}/{MM}/{week_start_day}-{week_end_day}/{DD}/{project}/{YYYYMMDD}-summary.md
```

Weekly summary path:

```text
{YYYY}/{MM}/{week_start_day}-{week_end_day}/weeks-summarys/{project}/{YYYYMM}-week-summary.md
```

Monthly summary path:

```text
{YYYY}/{MM}/months-summarys/{project}/{YYYYMM}-month-summary.md
```

Weekly and monthly reports must depend on persisted daily summary Markdown. Use raw daily JSON only as supporting structured evidence.

Add a metadata comment:

```markdown
---
**Autopilot Run Metadata**
- Run ID: {MULTICA_AUTOPILOT_RUN_ID}
- Report type: daily/weekly/monthly
- Report date: {report_date}
- Timezone: {timezone}
- Repos tracked: {success}/{total}
- Data coverage: {actual_days}/{expected_days} days
- JSON snapshot: committed/failed/skipped
- Errors: {error_summary or "None"}
- Duration: {elapsed}
---
```

## Security

Prefer `gh auth login` in the Multica runtime. If that is unavailable, use a fine-grained Personal Access Token with the minimum required repo permissions. Avoid `custom_env` for high-value secrets because `custom_env` values are stored as plaintext. If `custom_env.GITHUB_TOKEN` is the only available path, use a fine-grained token scoped to tracked repos and the tracker data repo, set an expiration, and mention the risk in setup notes.

## Rules

- Do not treat raw commit volume as the main conclusion when PR evidence exists.
- Do not merge draft/open/closed/merged PRs into one undifferentiated list.
- For weekly/monthly reports, every trend claim should cite at least one Key PR and the PR content evidence behind it.
- Do not claim understanding of a PR from the title alone when `content_signals` are available.
- Do not build weekly/monthly reports directly from raw PR JSON when daily summaries are available; treat daily summaries as the narrative source of truth.
- If data is partial, use cautious wording and list missing repos or dates.
- Use the requested `Language`. For `zh`, write clear Simplified Chinese. Keep claims evidence-bound.
