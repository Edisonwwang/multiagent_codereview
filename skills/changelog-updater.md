# Skill: changelog-updater

## Goal
Generate a CHANGELOG.md entry for a PR. Saves time and keeps the changelog
consistent across all contributors.

---

## Inputs
- {diff_file} 鈥?path to the PR diff JSON from fetch-pr skill
- {version} 鈥?optional. The version this change belongs to (e.g. 1.2.0)

---

## Steps

1. Read the diff file. Collect:
   - PR title, author, PR number, PR URL
   - All filenames changed
   - The nature of changes (additions, deletions, modifications)

2. Infer the change type:
   - New feature added 鈫?Added
   - Bug fixed 鈫?Fixed
   - Existing feature changed 鈫?Changed
   - Feature removed 鈫?Removed
   - Security fix 鈫?Security
   - Performance improvement 鈫?Performance
   - Documentation only 鈫?Docs

3. Write a CHANGELOG entry in Keep a Changelog format:

   ## [{version}] - {today}  (use "Unreleased" if no version given)

   ### {Change Type}
   - {one line description of what changed} ([#{pr_number}]({pr_url})) 鈥?@{pr_author}

   (one bullet per logical change 鈥?group related file changes into one bullet)

4. Check if CHANGELOG.md exists in the repo (look in diff for it):
   - If it was modified in the PR: append the new entry after the [Unreleased] header
   - If it was NOT modified: save the entry to outputs/reviews/{repo_slug}_pr{pr_number}_changelog.md
     and tell the user to manually add it

5. Print the generated entry.

---

## Output
- Changelog entry printed to screen
- outputs/reviews/{repo_slug}_pr{pr_number}_changelog.md (if not added to existing file)

---

## Error Handling
- No CHANGELOG.md in repo 鈫?save to outputs/ and notify
- Cannot determine version 鈫?use Unreleased
