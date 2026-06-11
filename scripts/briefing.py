"""
briefing.py
Reads schedule.json and review_state.json, prints a daily briefing.
Run automatically by Claude Code on startup via CLAUDE.md.
"""

import json
import os
from datetime import datetime, date

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SCHEDULE_PATH = "agents/schedule.json"
STATE_PATH    = "agents/review_state.json"

def days_since(date_str):
    if not date_str:
        return 999
    last = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (date.today() - last).days

def main():
    if not os.getenv("GITHUB_TOKEN"):
        print("  WARNING: GITHUB_TOKEN not set in .env  fetching private repos will fail")

    with open(SCHEDULE_PATH) as f:
        schedule = json.load(f)
    with open(STATE_PATH) as f:
        state = json.load(f)

    print("\n========================================")
    print(f"  CODE REVIEWER - Daily Briefing")
    print(f"  {date.today().strftime('%A, %d %B %Y')}")
    print("========================================\n")

    due     = []
    not_due = []

    for task in schedule["tasks"]:
        age = days_since(task["last_run"])
        if age >= task["cadence_days"]:
            due.append((task, age))
        else:
            not_due.append((task, age))

    if due:
        print("DUE TODAY:")
        for task, age in due:
            overdue = f"  WARNING: {age} days overdue" if age > task["cadence_days"] else ""
            print(f"  -> {task['name']} ({task['repo']}){overdue}")
    else:
        print("Nothing due today.")

    if not_due:
        print("\nUPCOMING:")
        for task, age in not_due:
            remaining = task["cadence_days"] - age
            print(f"  -> {task['name']} - due in {remaining} day(s)")

    print("\nRECENT REVIEWS:")
    history = state.get("review_history", [])
    if history:
        for entry in history[-5:]:
            print(f"  [{entry['date']}] {entry['repo']} PR#{entry['pr']} - {entry['status']}")
    else:
        print("  No reviews yet.")

    print("\n========================================")
    print("  Type a command to get started.")
    print("  e.g. 'run full review on owner/repo'")
    print("========================================\n")

if __name__ == "__main__":
    main()
