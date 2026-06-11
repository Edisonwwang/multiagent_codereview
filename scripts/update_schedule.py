"""
update_schedule.py
Updates review_state.json and schedule.json after a review completes.

Usage:
  python scripts/update_schedule.py --repo owner/repo --pr 42 --status reviewed
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import date

SCHEDULE_PATH = "agents/schedule.json"
STATE_PATH    = "agents/review_state.json"

def atomic_write_json(path, data):
    directory = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp-", suffix=".json", dir=directory, text=True)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo",   required=True)
    parser.add_argument("--pr",     required=True, type=int)
    parser.add_argument("--status", required=True, choices=["reviewed", "skipped", "failed"])
    args = parser.parse_args()

    today = str(date.today())

    with open(SCHEDULE_PATH) as f:
        schedule = json.load(f)

    schedule_found = False
    for task in schedule["tasks"]:
        if task.get("repo") == args.repo:
            task["last_run"] = today
            schedule_found = True

    with open(STATE_PATH) as f:
        state = json.load(f)

    state_found = False
    for repo_entry in state["repos"]:
        if repo_entry["repo"] == args.repo:
            repo_entry["last_pr_reviewed"] = args.pr
            repo_entry["last_run"]         = today
            repo_entry["status"]           = args.status
            state_found = True

    if not schedule_found or not state_found:
        missing = []
        if not schedule_found:
            missing.append(SCHEDULE_PATH)
        if not state_found:
            missing.append(STATE_PATH)
        print(
            f"[ERROR] Repo '{args.repo}' not found in: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)

    state["review_history"].append({
        "repo":   args.repo,
        "pr":     args.pr,
        "date":   today,
        "status": args.status,
    })

    atomic_write_json(SCHEDULE_PATH, schedule)
    atomic_write_json(STATE_PATH, state)

    print(f"[OK] State updated - {args.repo} PR#{args.pr} marked as {args.status}")

if __name__ == "__main__":
    main()
