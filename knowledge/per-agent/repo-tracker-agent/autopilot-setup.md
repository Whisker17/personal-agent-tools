# Repo Tracker Agent Autopilot Setup

last_updated: 2026-05-18

This guide documents the three Multica autopilot schedules for `repo-tracker-agent`.

## Agent Assets

- Agent config: `agents/repo-tracker-agent.yaml`
- System prompt: `prompts/system/repo-tracker-agent.md`
- Required skill: `skills/repo-tracker`
- Runbook: `knowledge/per-agent/repo-tracker-agent/autopilot-runbook.md`

## Prerequisites

- The Multica runtime has `gh` installed.
- Preferred authentication: run `gh auth login` in the runtime environment.
- If `gh auth login` is unavailable, use a fine-grained Personal Access Token. Scope it only to the tracked repos and the tracker data repo. Avoid `custom_env` for high-value secrets because Multica stores `custom_env` values as plaintext.
- Use `Whisker17/counterparty-daily-summary` as the tracker data repo.

## Tracker Data Repo

Recommended layout:

```text
2026/
  05/
    16-22/
      18/
        project-A/
          20260518-summary.md
      weeks-summarys/
        project-A/
          202605-week-summary.md
    months-summarys/
      project-A/
        202605-month-summary.md
```

Daily Markdown summaries are the source for weekly and monthly analysis. JSON snapshots may still be written as supporting structured data, but the weekly/monthly narrative should read the persisted daily summaries first.

## Daily Autopilot

```bash
multica autopilot create \
  --title "Daily Competitive Intelligence" \
  --description "Track repos: org1/repo1,org2/repo2
Report type: daily
Focus: security,bridge
Language: zh
Data repo: Whisker17/counterparty-daily-summary
Timezone: Asia/Shanghai" \
  --agent "repo-tracker-agent" \
  --mode create_issue

multica autopilot trigger-add <daily-id> --cron "0 9 * * *" --timezone "Asia/Shanghai"
```

## Weekly Autopilot

```bash
multica autopilot create \
  --title "Weekly Competitive Intelligence" \
  --description "Track repos: org1/repo1,org2/repo2
Report type: weekly
Focus: security,bridge
Language: zh
Data repo: Whisker17/counterparty-daily-summary
Timezone: Asia/Shanghai" \
  --agent "repo-tracker-agent" \
  --mode create_issue

multica autopilot trigger-add <weekly-id> --cron "0 10 * * 1" --timezone "Asia/Shanghai"
```

## Monthly Autopilot

```bash
multica autopilot create \
  --title "Monthly Competitive Intelligence" \
  --description "Track repos: org1/repo1,org2/repo2
Report type: monthly
Self repo: our/repo
Focus: security,bridge
Language: zh
Data repo: Whisker17/counterparty-daily-summary
Timezone: Asia/Shanghai" \
  --agent "repo-tracker-agent" \
  --mode create_issue

multica autopilot trigger-add <monthly-id> --cron "0 10 1 * *" --timezone "Asia/Shanghai"
```

## Smoke Checks

Run these locally before creating autopilots:

```bash
./scripts/validate --agent repo-tracker-agent
./skills/repo-tracker/scripts/test-repo-tracker.py
./skills/repo-tracker/scripts/tracker-fetch.py --repos "owner/repo" --since "2026-05-18T00:00:00+08:00" --until "2026-05-19T00:00:00+08:00" --fixture fixtures/tracker/daily-snapshot.json
./skills/repo-tracker/scripts/tracker-aggregate.py --type weekly --end-date "2026-05-24" --days 7 --fixture-dir fixtures/tracker/history
./skills/repo-tracker/scripts/tracker-aggregate.py --type weekly --end-date "2026-05-20" --days 3 --fixture-dir fixtures/tracker/history --repos "owner/repo" --timezone "Asia/Shanghai" --gap-fill --gap-fill-fixture fixtures/tracker/daily-snapshot.json
./skills/repo-tracker/scripts/tracker-persist.py --print-report-path --report-type daily --date "2026-05-18" --project "project-A"
```
