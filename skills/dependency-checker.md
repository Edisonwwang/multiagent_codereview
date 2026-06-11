# Skill: dependency-checker

## Goal
Scan dependency files in a PR diff for outdated packages, known vulnerabilities,
and suspicious version changes.

---

## Inputs
- {diff_file} 鈥?path to the PR diff JSON from fetch-pr skill

---

## Steps

1. Read the diff file. Look for any of these files in files_changed:
   - package.json / package-lock.json
   - requirements.txt / Pipfile / pyproject.toml
   - Gemfile / Cargo.toml / go.mod
   If none of these files were changed, print "No dependency files changed" and stop.

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
     (event-stream, ua-parser-js, colors, faker 鈥?check if version matches known bad versions)
   - Private package names that look like dependency confusion attacks
     (internal name with a public registry version suddenly appearing)

5. Flag the following as SUGGESTION:
   - More than 5 new dependencies added in one PR (suggest splitting)
   - Dev dependencies being added to production dependencies list

6. Print summary and store findings for report-writer.

---

## Output
Findings in memory for report-writer skill.

---

## Error Handling
- No dependency files in PR 鈫?print notice and stop cleanly
- Cannot parse dependency file format 鈫?note it as unreadable and skip that file
