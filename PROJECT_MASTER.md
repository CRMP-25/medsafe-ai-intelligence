# MedSafe AI Intelligence — Permanent Project Record
Version: 1.0.0 | Date: 2026-10-26 | Conference: Temple University, October 30, 2026

## Architecture
Standalone Streamlit UI (`app.py`), openFDA client and analytical functions (`core.py`), pytest regression suite (`tests/`). Live data via openFDA; no paid API key or LLM. NetworkX evidence graph visualized with Plotly. Streamlit cache TTL 30 minutes.

## Source review status
Kerendia V7.7.11 source ZIP was NOT available in the current conversation or accessible Library search. No claim of code-level reuse or parity is made. This is a clean independent implementation following the supplied high-level patterns. Review actual Kerendia source before claiming architectural migration.

## Implemented
Four tabs; FAERS reaction term summaries; explicit user-supplied 2x2 ROR/PRR with ROR CI; narrow medication-error report search; FDA label and recall retrieval; deterministic investigator; NetworkX graph; JSON evidence export; GraphML export; tests.

## Critical limitations and next steps
- ROR/PRR calculator is synthetic until validated, deduplicated case-level 2x2 counts are constructed; no actual signal calculation is claimed.
- Monthly reporting trend visualization not yet implemented; `trend()` currently groups exact receivedate and needs validated date aggregation and pagination.
- Medication error classification is narrow; dosage, administration, and product-confusion taxonomies need validated MedDRA term sets and structured extraction.
- openFDA pagination, deduplication, API rate limiting, query coverage, date-range filtering, caching snapshots, and data completeness checks need strengthening.
- Label queries may return multiple manufacturers/versions; verify product-level matching and current labeling.
- Interactive graph is a Plotly visualization, not yet node-selectable with graph-driven investigation.
- Reports are JSON, not yet formatted PDF; optional LLM integration not implemented.
- Live API and deployed UI have not been verified in this environment; conference acceptance is pending.

## Scientific rules
Never infer incidence or comparative safety from FAERS report counts. Disproportionality is a reporting association, not a causal effect. Preserve URLs, retrieval timestamps, and errors in exports. No medical advice.

## Deployment
Create a NEW GitHub repository `medsafe-ai-intelligence` (do not reuse Kerendia). Add the extracted files at repository root. Streamlit Community Cloud: New app > select repository > branch `main` > main file `app.py` > deploy. Keep Kerendia deployment untouched. Run `python -m pytest -q` locally before pushing. Validate all four tabs and downloads on deployed URL. Exact GitHub Desktop screenshots/UI need user verification.

## Release history
1.0.0 initial independent prototype; no previous MedSafe functionality to regress.

## V1.0.1 — 2026-10-26 | Kerendia source-informed update
Reference reviewed: `Healthcare_Intelligence_V7_7_11_Clinical_Funnel_Release.zip`, especially `app/src/clinical_funnel.py`, `app/src/engine.py`, `app/PROJECT_MASTER.md`, and release practices. Source was inspected read-only and is not bundled or modified. Adopted the evidence-gating pattern (unsupported downstream inference explicitly BLOCKED), independent project records, and reproducible test discipline.

Added `investigator.py` deterministic evidence gates, medication-error term classification, annual aggregation of openFDA received-date counts, and downloadable HTML investigation report. Broadened medication-error search terms; still not comprehensive or validated. The trend endpoint is capped at 1000 distinct date buckets and may be truncated, so the chart must not be treated as a complete historical trend. ROR/PRR remains SYNTHETIC INPUT ONLY; live validated case-level disproportionality remains BLOCKED. No paid LLM required.

Conference verification gates: live openFDA endpoint smoke tests, Streamlit rendering, API query acceptance and pagination, deduplicated FAERS contingency analysis, medication-error recall/precision review, and browser/deployment testing remain outstanding. Do not promote to production without these checks.

## V1.0.2-testing — 2026-10-26
- Corrected annual trend method: the deployed `count=receivedate` query returned HTTP 403. Now independently queries each receipt year using bounded `receivedate` filters and the openFDA response metadata total. Failed years are explicitly missing, not zero. Each successful year's URL and retrieval timestamp are shown in the UI.
- Added retry for transient HTTP 429/5xx, preserved response totals, and avoided blank recall/error tables.
- Corrected displayed version and hardened 2x2 input validation for empty marginal totals.
- Local unit tests passed; live API responses and browser behavior require verification after deployment. This is a testing release, not a validated clinical safety signal.
