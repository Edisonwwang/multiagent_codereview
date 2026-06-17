# Skill: code-reviewer

## Goal
Read a fetched PR diff and produce a structured code review - identifying bugs,
security issues, style violations, and improvement suggestions.

---

## Inputs
- {diff_file} - path to the JSON diff file from the fetch-pr skill
  e.g. outputs/reviews/facebook_react_pr1234_diff.json
- {output_file} - optional markdown output path, usually outputs/reviews/{repo_slug}_pr{pr_number}_code-reviewer.md

---

## Steps

1. Read the diff file. It contains:
   - pr_title - title of the pull request
   - pr_author - GitHub username of the author
   - files_changed - list of files with their before/after content

2. For each file changed, review the diff against these criteria:

   ### Bugs & Logic Errors
   - Off-by-one errors, null/undefined not handled, wrong conditionals
   - Flag with severity: critical / warning

   ### Security
   - Hardcoded secrets, unsanitised inputs, SQL injection patterns, exposed keys
   - Flag with severity: critical

   ### Code Quality
   - Functions longer than 40 lines without clear separation
   - Deeply nested logic (more than 3 levels)
   - Repeated code that should be extracted
   - Flag with severity: suggestion

   ### Style
   - Inconsistent naming conventions within the same file
   - Missing or misleading comments on complex logic
   - Flag with severity: suggestion

3. Do NOT flag things that are:
   - Just personal preference with no functional impact
   - Already covered by a comment in the diff
   - Outside the scope of the changed lines

4. Save findings to {output_file} when provided. Otherwise, store your findings
   as a structured list in memory for the report-writer skill.

5. Print a summary to the user:
   "Review complete. Found {n_critical} critical, {n_warning} warnings,
   {n_suggestions} suggestions. Run report-writer to save the full report."

---

## Output
- Markdown findings in {output_file} when provided.
- Otherwise, structured findings in memory (passed to report-writer skill).

## Notes
- Prioritise critical findings over style suggestions
- Always include line numbers where possible
