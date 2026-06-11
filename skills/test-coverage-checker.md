# Skill: test-coverage-checker

## Goal
Check whether new code added in a PR has corresponding test coverage.
Flag untested functions, classes, and critical paths.

---

## Inputs
- {diff_file} 鈥?path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Separate files into two buckets:
   - Source files: .py, .js, .ts, .jsx, .tsx, .rb, .go, .java, .cs
   - Test files: any file with test, spec, __tests__ in the name or path

2. For each source file with additions:
   - Extract new function and class definitions from the patch
   - Check if a corresponding test file exists in files_changed
   - Check if the test file references the new function/class names

3. Flag as WARNING:
   - New public functions with no corresponding test file changed
   - New classes with no constructor test visible in the diff

4. Flag as SUGGESTION:
   - New private/internal helpers with no tests (lower priority)
   - Test file exists but new function name does not appear in it

5. Flag as CRITICAL:
   - New authentication, authorisation, or payment-related code with zero tests

6. If no source files were changed, print "No source files changed" and stop.

7. Print summary: X new functions found, Y have tests, Z are untested.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Binary files or minified files 鈫?skip, note as unanalysable
- No source files in diff 鈫?stop cleanly with notice
