# Skill: report-writer

## Goal
Take the findings from the code-reviewer skill and produce a clean, structured
markdown report. Optionally post it as a GitHub PR comment.

---

## Inputs
- Findings from code-reviewer skill (already in memory)
- {repo} 鈥?the repo that was reviewed
- {pr_number} 鈥?the PR number

---

## Steps

1. Generate a markdown report using this exact structure:

# Code Review 鈥?{repo} PR #{pr_number}

**Reviewed by:** Code Reviewer Agent
**Date:** {today}
**Author:** {pr_author}
**PR Title:** {pr_title}

---

## Summary
| Severity     | Count |
|--------------|-------|
| Critical     | {n}   |
| Warning      | {n}   |
| Suggestion   | {n}   |

---

## Findings

### {filename}

**[CRITICAL]** {description}
Line {line_number}: `{code_snippet}`
-> {recommended_fix}

...

---

## Overall Assessment
{1-2 sentence summary of the PR quality and whether it looks ready to merge}

2. Save the report to:
   outputs/reviews/{repo_slug}_pr{pr_number}_review.md

3. Run the state update script:
   python scripts/update_schedule.py --repo {repo} --pr {pr_number} --status reviewed

4. Ask the user: "Report saved. Would you like me to post this as a GitHub comment? (yes/no)"
   - If yes: run python scripts/post_review_comment.py --repo {repo} --pr {pr_number}
   - If no: tell them the report path and stop.

---

## Output
- outputs/reviews/{repo_slug}_pr{pr_number}_review.md
