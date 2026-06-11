# Skill: commit-message-reviewer

## Goal
Review all commit messages in a PR against conventional commits format.
Good commit messages make the git history useful 鈥?bad ones make it useless.

---

## Inputs
- {repo} 鈥?GitHub repo in owner/repo format
- {pr_number} 鈥?PR number

---

## Steps

1. Fetch the commit list for the PR:
   python scripts/fetch_github.py --repo {repo} --pr {pr_number}
   Read the diff JSON 鈥?extract the pr_title and note it.
   For full commit messages, they are visible in the patch context.

2. Evaluate each commit message against conventional commits format:

   Good format:  type(scope): short description
   Types:        feat, fix, docs, style, refactor, test, chore, perf, ci
   Rules:
   - Subject line under 72 characters
   - Type prefix required
   - No capital letter after the colon
   - No full stop at the end of subject line
   - If body exists, blank line between subject and body

3. Flag as WARNING:
   - No type prefix (e.g. just "updated things")
   - Subject line over 72 characters
   - Vague messages: "fix", "update", "changes", "wip", "temp", "test"
   - All caps messages

4. Flag as SUGGESTION:
   - Missing scope (type: desc instead of type(scope): desc)
   - Could be more descriptive

5. Flag as CRITICAL:
   - Commit messages containing profanity or offensive content
   - Messages that contain passwords, tokens, or secrets

6. Print pass/fail per commit and overall score.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot fetch commits 鈫?use PR title as the only data point
