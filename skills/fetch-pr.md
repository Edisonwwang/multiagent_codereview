# Skill: fetch-pr

## Goal
Fetch the latest open pull request (or recent commits if no PR exists) from
a target GitHub repository and save the diff to disk for the review-code skill.

---

## Inputs
- {repo} 鈥?GitHub repo in the format owner/repo-name (e.g. facebook/react)
- {pr_number} 鈥?optional. If not provided, fetch the most recent open PR.

---

## Steps

1. Read agents/review_state.json to check if this PR has already been reviewed.
   If status is "reviewed" for this PR, tell the user and stop.

2. Run the fetch script:
   python scripts/fetch_github.py --repo {repo} --pr {pr_number}
   This will output a JSON file to outputs/reviews/{repo_slug}_pr{pr_number}_diff.json

3. Confirm the file was created. If the script returned an error, report it and stop.

4. Tell the user: "Fetched PR #{pr_number} from {repo}. Ready to run review-code."

---

## Output
- outputs/reviews/{repo_slug}_pr{pr_number}_diff.json

---

## Error Handling
- 401 Unauthorized -> remind user to set GITHUB_TOKEN in .env
- 404 Not Found -> repo is private or does not exist, check repo name
- No open PRs -> fall back to fetching the last 5 commits instead
