# Skill: code-reviewer

## Goal
Read a fetched PR diff and produce a structured code review 鈥?identifying bugs,
security issues, style violations, and improvement suggestions.

---

## Inputs
- {diff_file} 鈥?path to the JSON diff file from the fetch-pr skill
  e.g. outputs/reviews/facebook_react_pr1234_diff.json

---

## Steps

1. Read the diff file. It contains:
   - pr_title 鈥?title of the pull request
   - pr_author 鈥?GitHub username of the author
   - files_changed 鈥?list of files with their before/after content

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

4. Store your findings as a structured list in memory 鈥?the report-writer skill
   will use them next.

5. Print a summary to the user:
   "Review complete. Found {n_critical} critical, {n_warning} warnings,
   {n_suggestions} suggestions. Run write-report to save the full report."

---

## Output
Structured findings in memory (passed to write-report skill)
