#!/usr/bin/env python3
"""Upsert tracker JSON into a GitHub repo using the Contents API."""

import argparse
import base64
import json
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path


def run_gh(args):
    return subprocess.run(["gh", *args], text=True, capture_output=True)


def read_existing_sha(data_repo, path):
    result = run_gh(["api", f"repos/{data_repo}/contents/{path}"])
    if result.returncode != 0:
        output = (result.stderr or result.stdout).lower()
        if "not found" in output or "404" in output:
            return None
        raise RuntimeError((result.stderr or result.stdout).strip())
    data = json.loads(result.stdout)
    return data.get("sha")


def put_content(data_repo, path, payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(payload, handle)
        temp_path = handle.name
    try:
        return run_gh(
            [
                "api",
                f"repos/{data_repo}/contents/{path}",
                "--method",
                "PUT",
                "--input",
                temp_path,
            ]
        )
    finally:
        Path(temp_path).unlink(missing_ok=True)


def build_payload(path, file_path, sha):
    content = base64.b64encode(Path(file_path).read_bytes()).decode("ascii")
    operation = "update" if sha else "create"
    payload = {
        "message": f"{operation}: {path}",
        "content": content,
    }
    if sha:
        payload["sha"] = sha
    return operation, payload


def dry_run(path, file_path, existing_sha):
    sha = existing_sha or None
    operation, payload = build_payload(path, file_path, sha)
    output = {
        "operation": operation,
        "path": path,
        "sha": sha,
        "payload_keys": sorted(payload.keys()),
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


def week_range_for(day):
    days_since_saturday = (day.weekday() - 5) % 7
    start = day - timedelta(days=days_since_saturday)
    end = start + timedelta(days=6)
    return start, end


def validate_project(project):
    safe = project.strip().strip("/")
    if not safe or ".." in safe:
        raise ValueError("project must be a valid path (e.g. owner/repo)")
    parts = safe.split("/")
    if not all(parts):
        raise ValueError("project contains empty segments")
    return safe


def report_path(report_type, report_date, project):
    day = date.fromisoformat(report_date)
    week_start, week_end = week_range_for(day)
    year = f"{day.year:04d}"
    month = f"{day.month:02d}"
    week_dir = f"{week_start.day:02d}-{week_end.day:02d}"
    safe_project = validate_project(project)
    if report_type == "daily":
        return f"{year}/{month}/{week_dir}/{day.day:02d}/{safe_project}/{year}{month}{day.day:02d}-summary.md"
    if report_type == "weekly":
        return f"{year}/{month}/{week_dir}/weeks-summarys/{safe_project}/{year}{month}-week-summary.md"
    if report_type == "monthly":
        return f"{year}/{month}/months-summarys/{safe_project}/{year}{month}-month-summary.md"
    raise ValueError(f"unknown report type: {report_type}")


def main():
    parser = argparse.ArgumentParser(description="Upsert tracker JSON into GitHub")
    parser.add_argument("--data-repo", help="GitHub owner/repo")
    parser.add_argument("--path", help="Repo path to write")
    parser.add_argument("--file", help="Local file to upload")
    parser.add_argument(
        "--dry-run-existing-sha",
        help="Skip GitHub calls and pretend the remote file exists with this sha",
    )
    parser.add_argument("--print-report-path", action="store_true")
    parser.add_argument("--report-type", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--date", help="Report date YYYY-MM-DD")
    parser.add_argument("--project", help="Project path segment")
    args = parser.parse_args()

    if args.print_report_path:
        try:
            if not args.report_type or not args.date or not args.project:
                raise ValueError("--report-type, --date, and --project are required")
            print(report_path(args.report_type, args.date, args.project))
            return 0
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    if not args.data_repo or not args.path or not args.file:
        parser.error("--data-repo, --path, and --file are required unless --print-report-path is used")

    if args.dry_run_existing_sha is not None:
        return dry_run(args.path, args.file, args.dry_run_existing_sha)

    try:
        sha = read_existing_sha(args.data_repo, args.path)
        operation, payload = build_payload(args.path, args.file, sha)
        result = put_content(args.data_repo, args.path, payload)
        if result.returncode != 0 and "409" in (result.stderr + result.stdout):
            sha = read_existing_sha(args.data_repo, args.path)
            operation, payload = build_payload(args.path, args.file, sha)
            result = put_content(args.data_repo, args.path, payload)
        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            return 1
        response = json.loads(result.stdout)
        print(
            json.dumps(
                {
                    "operation": operation,
                    "path": args.path,
                    "commit": (response.get("commit") or {}).get("sha"),
                    "content_sha": (response.get("content") or {}).get("sha"),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
