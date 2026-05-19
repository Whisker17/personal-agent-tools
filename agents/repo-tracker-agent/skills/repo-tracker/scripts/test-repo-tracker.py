#!/usr/bin/env python3
"""Regression checks for repo-tracker-agent support files."""

import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
AGENT_DIR = "agents/repo-tracker-agent"
SKILL_DIR = f"{AGENT_DIR}/skills/repo-tracker"
SCRIPT_DIR = f"{SKILL_DIR}/scripts"
FIXTURE_DIR = f"{SKILL_DIR}/fixtures/tracker"
AUTOPILOT_DIR = "autocopilots/repo-tracker"
VALIDATE = "systems/validate/validate"


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def assert_file(path):
    full = REPO_ROOT / path
    if not full.is_file():
        fail(f"missing file: {path}")
    return full


def assert_executable(path):
    full = assert_file(path)
    if not (full.stat().st_mode & stat.S_IXUSR):
        fail(f"not executable: {path}")
    return full


def run(args, **kwargs):
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        **kwargs,
    )


def check_required_files():
    for path in [
        f"{AGENT_DIR}/repo-tracker-agent.yaml",
        f"{AGENT_DIR}/instructions.md",
        f"{SKILL_DIR}/SKILL.md",
        f"{SKILL_DIR}/references/pr-analysis-workflow.md",
        f"{SKILL_DIR}/references/report-templates.md",
        f"{AUTOPILOT_DIR}/RUNBOOK.md",
        f"{AUTOPILOT_DIR}/autopilot.yaml",
        f"{FIXTURE_DIR}/autopilot-prompt-daily.txt",
        f"{FIXTURE_DIR}/autopilot-prompt-weekly.txt",
        f"{FIXTURE_DIR}/daily-snapshot.json",
        f"{FIXTURE_DIR}/weekly-aggregate.json",
        f"{FIXTURE_DIR}/daily-report.md",
    ]:
        assert_file(path)

    for path in [
        f"{SCRIPT_DIR}/tracker-fetch.py",
        f"{SCRIPT_DIR}/tracker-persist.py",
        f"{SCRIPT_DIR}/tracker-aggregate.py",
    ]:
        assert_executable(path)


def check_agent_validation():
    result = run([f"./{VALIDATE}", "--agent", "repo-tracker-agent"])
    if result.returncode != 0:
        fail(result.stdout + result.stderr)
    config = assert_file(f"{AGENT_DIR}/repo-tracker-agent.yaml").read_text()
    if SKILL_DIR not in config:
        fail(f"repo-tracker-agent does not reference {SKILL_DIR}")


def check_prompt_contract():
    prompt = assert_file(f"{AGENT_DIR}/instructions.md").read_text()
    prompt_required = [
        "Track repos",
        "Report type",
        "Data repo",
        "Timezone",
        "repo-tracker",
    ]
    missing = [item for item in prompt_required if item not in prompt]
    if missing:
        fail(f"prompt missing required terms: {', '.join(missing)}")

    skill = assert_file(f"{SKILL_DIR}/SKILL.md").read_text()
    skill_required = [
        f"{SCRIPT_DIR}/tracker-fetch.py",
        f"{SCRIPT_DIR}/tracker-persist.py",
        f"{SCRIPT_DIR}/tracker-aggregate.py",
        "natural day",
        "default branch",
        "sha",
        "409",
        "fine-grained Personal Access Token",
        "custom_env",
        "coverage",
        "Data Notes",
        "daily summary",
        "weeks-summarys",
        "months-summarys",
        "draft",
        "open",
        "closed",
        "merged",
        "Key PRs",
        "content_signals",
        "body/files/commits",
    ]
    missing = [item for item in skill_required if item not in skill]
    if missing:
        fail(f"skill missing required terms: {', '.join(missing)}")


def check_fetch_fixture_mode():
    result = run(
        [
            f"./{SCRIPT_DIR}/tracker-fetch.py",
            "--repos",
            "owner/repo",
            "--since",
            "2026-05-18T00:00:00+08:00",
            "--until",
            "2026-05-19T00:00:00+08:00",
            "--fixture",
            f"{FIXTURE_DIR}/daily-snapshot.json",
        ]
    )
    if result.returncode != 0:
        fail(result.stdout + result.stderr)
    data = json.loads(result.stdout)
    if data["window"]["since"] != "2026-05-18T00:00:00+08:00":
        fail("tracker-fetch did not preserve requested since")
    if "owner/repo" not in data["repos"]:
        fail("tracker-fetch fixture output missing requested repo")
    pr_status = data["repos"]["owner/repo"].get("pr_status") or {}
    for key in ["draft", "open", "closed_unmerged", "merged"]:
        if key not in pr_status:
            fail(f"tracker-fetch output missing PR status segment: {key}")
    if not pr_status["draft"]:
        fail("tracker-fetch did not include updated draft PRs in status segments")
    sample_pr = pr_status["merged"][0]
    content_signals = sample_pr.get("content_signals") or {}
    for key in ["body_excerpt", "changed_files", "modules", "commit_subjects", "summary_basis"]:
        if key not in content_signals:
            fail(f"tracker-fetch PR missing content signal: {key}")
    if not data["repos"]["owner/repo"].get("key_prs"):
        fail("tracker-fetch output missing key_prs")
    key_pr = data["repos"]["owner/repo"]["key_prs"][0]
    if "content_signals" not in key_pr:
        fail("key_prs missing content_signals")


def check_aggregate_fixture_mode():
    result = run(
        [
            f"./{SCRIPT_DIR}/tracker-aggregate.py",
            "--type",
            "weekly",
            "--end-date",
            "2026-05-24",
            "--days",
            "7",
            "--fixture-dir",
            f"{FIXTURE_DIR}/history",
        ]
    )
    if result.returncode != 0:
        fail(result.stdout + result.stderr)
    data = json.loads(result.stdout)
    if data["type"] != "weekly":
        fail("tracker-aggregate output type mismatch")
    if data["coverage"]["actual_days"] != 2:
        fail("tracker-aggregate did not count fixture coverage")
    if data["repos"]["owner/repo"]["prs"]["merged_count"] != 3:
        fail("tracker-aggregate merged PR count mismatch")
    status_counts = data["repos"]["owner/repo"].get("pr_status_counts") or {}
    if status_counts.get("merged") != 3:
        fail("tracker-aggregate merged PR status count mismatch")
    if status_counts.get("open") != 1:
        fail("tracker-aggregate open PR status count mismatch")
    if not data["repos"]["owner/repo"].get("key_prs"):
        fail("tracker-aggregate missing key_prs")


def check_runbook_shape():
    runbook = assert_file(f"{AUTOPILOT_DIR}/RUNBOOK.md").read_text()
    for heading in ["# Goal", "# Context", "# Steps"]:
        if heading not in runbook:
            fail(f"runbook missing heading: {heading}")


def check_aggregate_gap_fill_fixture_mode():
    result = run(
        [
            f"./{SCRIPT_DIR}/tracker-aggregate.py",
            "--type",
            "weekly",
            "--end-date",
            "2026-05-20",
            "--days",
            "3",
            "--fixture-dir",
            f"{FIXTURE_DIR}/history",
            "--repos",
            "owner/repo",
            "--timezone",
            "Asia/Shanghai",
            "--gap-fill",
            "--gap-fill-fixture",
            f"{FIXTURE_DIR}/daily-snapshot.json",
        ]
    )
    if result.returncode != 0:
        fail(result.stdout + result.stderr)
    data = json.loads(result.stdout)
    if data["coverage"]["actual_days"] != 3:
        fail("tracker-aggregate gap fill did not improve coverage")
    if data["coverage"]["gap_filled_dates"] != ["2026-05-20"]:
        fail("tracker-aggregate gap fill dates mismatch")


def check_aggregate_daily_summary_dependency():
    result = run(
        [
            f"./{SCRIPT_DIR}/tracker-aggregate.py",
            "--type",
            "weekly",
            "--end-date",
            "2026-05-20",
            "--days",
            "3",
            "--summary-fixture-dir",
            f"{FIXTURE_DIR}/summary-repo",
            "--project",
            "owner/repo",
        ]
    )
    if result.returncode != 0:
        fail(result.stdout + result.stderr)
    data = json.loads(result.stdout)
    summaries = data.get("daily_summaries") or []
    if len(summaries) != 2:
        fail("tracker-aggregate did not load daily summaries")
    if "bridge validation" not in summaries[0].get("content", ""):
        fail("tracker-aggregate loaded wrong daily summary content")
    if data["coverage"]["summary_days"] != 2:
        fail("tracker-aggregate summary coverage mismatch")


def check_persist_upsert_dry_run():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump({"ok": True}, handle)
        temp_path = handle.name

    try:
        result = run(
            [
                f"./{SCRIPT_DIR}/tracker-persist.py",
                "--data-repo",
                "owner/data",
                "--path",
                "daily/2026-05-18.json",
                "--file",
                temp_path,
                "--dry-run-existing-sha",
                "abc123",
            ]
        )
    finally:
        os.unlink(temp_path)

    if result.returncode != 0:
        fail(result.stdout + result.stderr)
    data = json.loads(result.stdout)
    if data["operation"] != "update":
        fail("tracker-persist dry-run did not choose update")
    if data.get("sha") != "abc123":
        fail("tracker-persist dry-run did not include existing sha")


def check_report_path_generation():
    cases = [
        (
            ["--report-type", "daily", "--date", "2026-05-18", "--project", "owner/repo"],
            "2026/05/16-22/18/owner/repo/20260518-summary.md",
        ),
        (
            ["--report-type", "weekly", "--date", "2026-05-18", "--project", "owner/repo"],
            "2026/05/16-22/weeks-summarys/owner/repo/202605-week-summary.md",
        ),
        (
            ["--report-type", "monthly", "--date", "2026-05-18", "--project", "owner/repo"],
            "2026/05/months-summarys/owner/repo/202605-month-summary.md",
        ),
    ]
    for args, expected in cases:
        result = run([f"./{SCRIPT_DIR}/tracker-persist.py", "--print-report-path", *args])
        if result.returncode != 0:
            fail(result.stdout + result.stderr)
        actual = result.stdout.strip()
        if actual != expected:
            fail(f"report path mismatch: expected {expected}, got {actual}")


def main():
    check_required_files()
    check_agent_validation()
    check_prompt_contract()
    check_fetch_fixture_mode()
    check_aggregate_fixture_mode()
    check_aggregate_gap_fill_fixture_mode()
    check_aggregate_daily_summary_dependency()
    check_persist_upsert_dry_run()
    check_report_path_generation()
    check_runbook_shape()
    print("repo-tracker checks PASS")


if __name__ == "__main__":
    main()
