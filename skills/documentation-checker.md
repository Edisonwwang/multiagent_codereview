# Skill: documentation-checker

## Goal
Check that new functions, classes, and modules added in a PR have adequate
documentation - docstrings, JSDoc, inline comments for complex logic.

---

## Inputs
- {diff_file} - path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Look at added lines only.

2. For each new function or class definition found in added lines:

   ### Docstrings / JSDoc
   - Python: check if def is followed by a """ docstring
   - JavaScript/TypeScript: check if function is preceded by /** JSDoc block
   - Other languages: check for equivalent doc comment conventions
   - Flag as SUGGESTION if a public function has no doc comment
   - Flag as WARNING if a public function over 20 lines has no doc comment

   ### Inline comments
   - Flag as SUGGESTION if a block of 10+ lines of logic has no comments at all
   - Flag as WARNING if code uses a non-obvious algorithm with no explanation

   ### README / docs updates
   - If new public API endpoints, CLI flags, or config options are added:
     check if any .md or docs/ files were also modified in the PR
   - Flag as SUGGESTION if they were not

3. Skip test files.
4. Skip one-liner functions.

5. Print summary.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot parse file type - skip with note
