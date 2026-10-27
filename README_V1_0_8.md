# MedSafe V1.0.8 — Development automation

**Scope:** Development infrastructure only; V1.0.7 investigation UI and scientific behavior remain unchanged. The app banner remains V1.0.7 until a separate product release is made.

## Included
- `.github/workflows/medsafe-ci.yml`: automatic CI on version testing branches, stable `testing` branch, PRs and manual dispatch.
- `scripts/validate_export.py`: offline ZIP integrity, manifest, graph edge, GraphML and provenance checks; supports `--self-test` and a downloaded ZIP path.
- `scripts/promote_testing.sh`: optional safe fast-forward-only promotion of a published version branch to the stable `testing` branch. Requires Git CLI, a clean working tree and a pre-existing remote `testing` branch; asks for confirmation.
- `tests/test_v108.py`: tests the validator and detects missing provenance.

## First-time setup
1. Publish `v1.0.8-testing` with the files in this package. GitHub Actions will automatically run the CI workflow. Check GitHub **Actions** for a green run; do not assume tests pass just because a commit was published.
2. Create a remote branch named `testing` from `v1.0.8-testing` (once). Deploy a **new** Streamlit Community Cloud app with repository `CRMP-25/medsafe-ai-intelligence`, branch `testing`, main file `app.py`, desired URL `medsafe-ai-testing` (if available). Existing versioned deployments remain untouched.
3. For future releases, develop on a new versioned branch based on `testing`. CI runs on push. After tests pass and review, fast-forward `testing` with the optional promotion script or a reviewed GitHub PR. Streamlit should redeploy the stable testing app on branch updates.
4. Keep production on its own protected branch/app; no production changes are made here.

## Caveats
- CI validates synthetic deterministic evidence. It does **not** make live openFDA calls, test the Streamlit browser, or establish clinical accuracy.
- The promotion script intentionally refuses non-fast-forward histories; no force-push.
- No GitHub or Streamlit remote configuration is changed automatically by this package.
- For a real export: `python scripts/validate_export.py path/to/medsafe_complete.zip`.
