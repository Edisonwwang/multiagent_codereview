# Skill: pr-summary-writer

## Goal
Write a plain English summary of what a PR does - what changed, why it matters,
and whether it looks ready to merge. Useful for non-technical reviewers and
for auto-generating PR descriptions.

---

## Inputs
- {diff_file} - path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Collect:
   - PR title and author
   - All filenames changed and their status (added/modified/removed)
   - The patch content of each file

2. Infer the purpose of the PR from the changes:
   - What problem does this solve?
   - What is the main change?
   - Are there side effects or related changes?

3. Write a summary using this structure:

   ## What this PR does
   [2-3 sentences explaining the change in plain English.
    No jargon. Write as if explaining to a product manager.]

   ## Files changed
   - {filename} - [one line: what changed and why]
   (one line per file, max 10 files, group similar ones)

   ## Risk level
   [Low / Medium / High]
   [One sentence explaining the risk assessment]

   ## Ready to merge?
   [Yes / Needs work / Needs review]
   [One sentence explaining why]

4. Save the summary to:
   outputs/reviews/{repo_slug}_pr{pr_number}_summary.md

---

## Output
- outputs/reviews/{repo_slug}_pr{pr_number}_summary.md

---

## Error Handling
- Empty diff - note PR has no file changes and stop
