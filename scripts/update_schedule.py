"""
update_schedule.py
Updates review_state.json and schedule.json after a review completes.

Usage:
  python scripts/update_schedule.py --repo owner/repo --pr 42 --status reviewed
"""

import argparse
import json
from datetime import date

SCHEDULE_PATH = "agents/schedule.json"
STATE_PATH    = "agents/review_state.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo",   required=True)
    parser.add_argument("--pr",     required=True, type=int)
    parser.add_argument("--status", required=True, choices=["reviewed", "skipped", "failed"])
    args = parser.parse_args()

    today = str(date.today())

    with open(SCHEDULE_PATH) as f:
        schedule = json.load(f)

    for task in schedule["tasks"]:
        if task.get("repo") == args.repo:
            task["last_run"] = today

    with open(SCHEDULE_PATH, "w") as f:
        json.dump(schedule, f, indent=2)

    with open(STATE_PATH) as f:
        state = json.load(f)

    for repo_entry in state["repos"]:
        if repo_entry["repo"] == args.repo:
            repo_entry["last_pr_reviewed"] = args.pr
            repo_entry["last_run"]         = today
            repo_entry["status"]           = args.status

    state["review_history"].append({
        "repo":   args.repo,
        "pr":     args.pr,
        "date":   today,
        "status": args.status,
    })

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    print(f"[OK] State updated - {args.repo} PR#{args.pr} marked as {args.status}")

if __name__ == "__main__":
    main()
