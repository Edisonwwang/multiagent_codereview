# Workflows

## One-Time Setup

From repo root:

```bash
pip install -r requirements.txt
python scripts/index_skills.py
```

Create `.env`:

```env
GITHUB_TOKEN=your_github_token_here
DEFAULT_REPO=owner/repo
```

Configure scheduled repo in:

```text
agents/schedule.json
agents/review_state.json
```

The repo must appear in both files if `scripts/update_schedule.py` will be used.

## Start A Session

Recommended first command:

```bash
python scripts/briefing.py
```

Expected result:

- due tasks.
- upcoming tasks.
- recent review history.
- token warning if `GITHUB_TOKEN` is missing.

## Review Latest Open PR

User asks:

```text
run full review on owner/repo
```

AI should:

1. Run skill search:

   ```bash
   python scripts/search_skills.py --query "full review on owner/repo"
   ```

2. Read relevant skills, usually:

   - `skills/fetch-pr.md`
   - `skills/code-reviewer.md`
   - `skills/report-writer.md`

3. Fetch latest open PR:

   ```bash
   python scripts/fetch_github.py --repo owner/repo
   ```

4. Read generated diff JSON under `outputs/reviews/`.

5. Review patches using selected skills.

6. Write report:

   ```text
   outputs/reviews/{owner}_{repo}_pr{number}_review.md
   ```

7. Update state:

   ```bash
   python scripts/update_schedule.py --repo owner/repo --pr {number} --status reviewed
   ```

8. Ask user before posting the report to GitHub.

## Review Specific PR

Fetch command:

```bash
python scripts/fetch_github.py --repo owner/repo --pr 42
```

Everything else follows the normal review flow.

## Post Review To GitHub

Only after user confirms:

```bash
python scripts/post_review_comment.py --repo owner/repo --pr 42
```

Preconditions:

- `GITHUB_TOKEN` exists and has permission.
- report markdown exists at the expected output path.

## Search For Skills Manually

```bash
python scripts/search_skills.py --query "docker container security"
```

If Chroma is unavailable, the script automatically falls back to keyword search.

## Rebuild Skill Index

```bash
python scripts/index_skills.py
```

Use after active skill metadata changes.

## Draft A New Skill

```bash
python scripts/create_skill.py --name api-contract-reviewer --description "Reviews API contract changes for compatibility" --tags "api,contract,compatibility,review"
```

Then edit:

```text
skills/pending/api-contract-reviewer.md
```

Do not use this pending skill yet.

## Approve A Skill

```bash
python scripts/approve_skill.py --name api-contract-reviewer
```

Approval:

- moves the file from `skills/pending/` to `skills/`.
- updates registry.
- attempts Chroma indexing.

## Run Tests

```bash
python -m unittest discover -s tests
```

Current tests cover:

- atomic JSON write helper.
- update-schedule unknown repo failure without mutation.
- create-skill clean template and registry path behavior.

## Smoke Checks

Useful before committing:

```bash
Get-ChildItem scripts -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
python -m unittest discover -s tests
python scripts/search_skills.py --query "full code review of this repository"
python scripts/briefing.py
```

On Windows PowerShell, Python does not expand `scripts/*.py` for
`python -m py_compile`; use `Get-ChildItem` as shown.
