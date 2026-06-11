# Skill: code-complexity-analyzer

## Goal
Identify code that is too complex, too long, or too deeply nested.
Flag it before it becomes technical debt.

---

## Inputs
- {diff_file} 鈥?path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Focus only on added lines (lines starting with +).

2. For each file, analyse the new code for:

   ### Function length
   - Count lines per function/method in added code
   - Flag as WARNING if any new function exceeds 40 lines
   - Flag as SUGGESTION if any new function is between 25-40 lines

   ### Nesting depth
   - Count indentation levels in added code
   - Flag as WARNING if nesting exceeds 4 levels (if inside if inside for inside try...)
   - Flag as SUGGESTION at 3 levels

   ### Cognitive complexity indicators
   - More than 5 if/else branches in one function 鈫?WARNING
   - Ternary operators nested inside other ternaries 鈫?SUGGESTION
   - Boolean expressions with more than 4 conditions 鈫?SUGGESTION

   ### Code duplication
   - Identical or near-identical blocks appearing more than once in the diff 鈫?SUGGESTION
   - Consider extraction into a shared function

3. Skip test files 鈥?complexity rules are relaxed for tests.

4. Print summary: X functions analysed, Y flagged.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- Cannot determine function boundaries 鈫?note file as unanalysable
- Minified or generated code 鈫?skip
