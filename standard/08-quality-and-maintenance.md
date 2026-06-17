# Quality And Maintenance

## Current Quality Baseline

Strengths:

- Simple script-per-task structure.
- Clear markdown skills.
- Local JSON state is easy to inspect.
- Shared path and GitHub helpers reduce duplication.
- GitHub file/commit fetching supports pagination.
- JSON state updates use atomic replace.
- Tests exist for risky mutation paths.
- Dependencies are declared.

Weaknesses:

- No packaged CLI command.
- No type checking.
- No lint/format configuration.
- Limited test coverage.
- JSON state is not concurrency-safe.
- Live GitHub behavior is not integration-tested.
- AI review quality depends on the host AI reading and following skills.

## Coding Standards

Use plain Python stdlib unless a dependency is clearly justified.

Keep scripts:

- small.
- command-line friendly.
- explicit about side effects.
- clear on stderr/stdout behavior.
- safe when run from outside repo root.

Use `common.py` for:

- repo paths.
- JSON loading/writing.
- artifact path formatting.

Use `github_client.py` for:

- GitHub headers.
- token loading.
- request/response handling.
- pagination.
- POST operations.

Avoid:

- hardcoded relative paths in scripts.
- duplicated GitHub API code.
- in-place JSON writes for state files.
- using pending skills.
- writing generated review outputs to tracked source paths.

## Testing Standards

Run before commit:

```bash
python -m unittest discover -s tests
```

Also run syntax checks:

```powershell
Get-ChildItem scripts -Filter *.py | ForEach-Object { python -m py_compile $_.FullName }
```

Add tests when changing:

- JSON state mutation.
- skill registry mutation.
- path resolution.
- GitHub request construction.
- Chroma indexing/search behavior where it can be isolated.

Prefer stdlib `unittest` unless the project intentionally adopts pytest.

## Dependency Standards

Runtime dependencies live in:

```text
requirements.txt
```

Current dependencies:

- `chromadb`
- `python-dotenv`

## State Safety

`atomic_write_json` protects against partially written JSON files for normal
single-process use.

It does not provide:

- locking.
- conflict detection.
- concurrent writer protection.
- multi-user coordination.

If production use requires concurrency, add file locks or move state into a
proper database.

## GitHub API Safety

Current API client:

- uses official GitHub REST API.
- sends token if present.
- prints API errors and exits.
- paginates list endpoints where called through `get_all_pages`.

Potential improvements:

- retry transient 5xx/429 failures.
- expose rate-limit details.
- validate token scopes.
- add dry-run support for posting comments.
- allow GitHub Enterprise API root configuration.

## Chroma Maintenance

Chroma is local, generated state. If search results look stale:

```bash
python scripts/index_skills.py
```

If necessary, delete `.chroma/` and rebuild.

Do not commit `.chroma/`.

## Future Hardening Roadmap

High-value next steps:

1. Add a real CLI entry point, for example:

   ```bash
   python -m reviewer review owner/repo --pr 42
   ```

2. Add lint/format tooling, likely Ruff.

3. Add tests for:

   - `github_client.get_all_pages`.
   - `approve_skill.py`.
   - `search_skills.py` fallback behavior.
   - `post_review_comment.py` missing-token and missing-report behavior.

4. Add schema validation for JSON files.

5. Add file locking around state writes if concurrent runs become possible.

6. Add an optional dry-run mode for posting comments.

## Known Local Artifacts

Generated files under `outputs/reviews/` and `.chroma/` are ignored by git.

Do not rely on their presence for a fresh clone. Recreate with:

```bash
python scripts/index_skills.py
python scripts/fetch_github.py --repo owner/repo --pr 42
```
