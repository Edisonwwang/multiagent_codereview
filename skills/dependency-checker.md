# Skill: dependency-checker

## Goal
Scan dependency files in a PR diff for outdated packages, known vulnerabilities,
and suspicious version changes.

---

## Inputs
- {diff_file} - path to the PR diff JSON from fetch-pr skill
- {output_file} - optional markdown output path, usually outputs/reviews/{repo_slug}_pr{pr_number}_dependency-checker.md

---

## Steps

1. Read the diff file. Look for any of these files in files_changed:
   - package.json / package-lock.json
   - requirements.txt / Pipfile / pyproject.toml
   - Gemfile / Cargo.toml / go.mod
   If none of these files were changed, write "No dependency files changed" to {output_file} when provided, print the same notice, and stop.

2. For each dependency file changed, extract:
   - Packages that were added (new dependencies)
   - Packages that were removed
   - Packages whose versions changed

3. Flag the following as WARNING:
   - Any package pinned to an exact old version (e.g. lodash@4.0.0 when latest is 4.17.x)
   - Any package added without a version pin (e.g. "requests" with no version)
   - Version downgrades (version went lower than before)

4. Flag the following as CRITICAL:
   - Any package known to have published malicious versions in the past
     (event-stream, ua-parser-js, colors, faker - check if version matches known bad versions)
   - Private package names that look like dependency confusion attacks
     (internal name with a public registry version suddenly appearing)

5. Flag the following as SUGGESTION:
   - More than 5 new dependencies added in one PR (suggest splitting)
   - Dev dependencies being added to production dependencies list

6. Save findings to {output_file} when provided, then print summary.

---

## Output
- Markdown findings in {output_file} when provided.
- Otherwise, findings in memory for report-writer skill.

---

## Error Handling
- No dependency files in PR - print notice and stop cleanly
- Cannot parse dependency file format - note it as unreadable and skip that file
