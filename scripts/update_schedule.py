"""
update_schedule.py
Updates review_state.json and schedule.json after a review completes.

Usage:
  python scripts/update_schedule.py --repo owner/repo --pr 42 --status reviewed
"""

import argparse
import sys
from datetime import date

from common import SCHEDULE_PATH, STATE_PATH, atomic_write_json, display_path, load_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo",   required=True)
    parser.add_argument("--pr",     required=True, type=int)
    parser.add_argument("--status", required=True, choices=["reviewed", "skipped", "failed"])
    args = parser.parse_args()

    today = str(date.today())

    schedule = load_json(SCHEDULE_PATH)

    schedule_found = False
    for task in schedule["tasks"]:
        if task.get("repo") == args.repo:
            task["last_run"] = today
            schedule_found = True

    state = load_json(STATE_PATH)

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
            missing.append(display_path(SCHEDULE_PATH))
        if not state_found:
            missing.append(display_path(STATE_PATH))
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
