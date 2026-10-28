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

---
## Operational update — 2026-10-26/27 (V1.0.1–V1.0.4)

**Scope and evidence:** This update records user-reported Streamlit deployment observations and the downloaded `medsafe_buprenorphine_evidence.md` report. It does not imply direct access to Streamlit server logs, GitHub write access, or independently executed cloud acceptance tests. Earlier sections above are historical V1.0.0 status, not the current deployment state.

### Deployed versions and preservation

| Version | Testing branch | Streamlit URL | Observed status |
|---|---|---|---|
| V1.0.1 | `v1.0.1-testing` | https://medsafe-ai-intelligence.streamlit.app/ | Previously deployed; current health not rechecked |
| V1.0.2 | `v1.0.2-testing` | https://medsafe-ai-v102.streamlit.app/ | Previously deployed; current health not rechecked |
| V1.0.3 | `v1.0.3-testing` | https://medsafe-ai-v103.streamlit.app/ | User previously verified working |
| V1.0.4 | `v1.0.4-testing` | https://medsafe-ai-v104.streamlit.app/ | User confirmed page restored after reboot; stability remains unverified |

Repository: `CRMP-25/medsafe-ai-intelligence`; Streamlit Community Cloud workspace `crmp-25`. **Do not change Kerendia or previous MedSafe releases.** The original V1.0.0 deployment instructions above are historical and must not be treated as current instructions.

### V1.0.4 observed functionality

- User confirmed FDA Regulatory Evidence interface displayed 100/103 labels and 32/32 recalls; searchable table and label inspection worked.
- User previously verified V1.0.3 retrieval of 500/7,078 medication-error records, 100/103 labels and 32/32 recalls, with a functional evidence graph (overcrowded labels).
- V1.0.4 added a filtered evidence graph and downloadable Markdown investigation report. The user downloaded and supplied `medsafe_buprenorphine_evidence.md`, establishing that Markdown export worked at least once.
- Repeated changes to the Agentic Safety Investigator graph node-count control preceded a full-app error. Streamlit displayed a generic “Oh no. Error running app” message; the app page returned after the user selected **Reboot**. **Root cause is unknown without logs or reproduction.** Do not assert confirmed out-of-memory or a specific exception.

### Downloaded buprenorphine investigation — actual reported completeness

Generated UTC: `2026-10-27T00:50:04.949057+00:00`.

| Evidence type | Retrieved | API matching | Reported coverage |
|---|---:|---:|---:|
| Reaction-term event summary | 15 | Unknown | Unknown |
| Medication-error reports | 500 | 7,078 | 7.1% |
| FDA labels | 100 | 103 | 97.1% |
| Recalls | 32 | 32 | 100.0% |

These are records or aggregated terms, **not patient counts or clinical incidence**. Matching totals are query- and time-dependent. The report contains source query links and retrieval timestamps. Its partial error-report and label coverage must be visible in the user interface and exports; no claim of complete medication-error surveillance is justified.

### V1.0.4.1 proposed corrective scope — NOT IMPLEMENTED

1. Make graph node-count changes explicit via **Apply Graph Settings**; prevent unnecessary retrieval/reconstruction on each widget change.
2. Bound node and edge counts and graph-rendering workload; choose a conservative limit based on measured cloud behavior, not an arbitrary guarantee.
3. Isolate graph-rendering exceptions so the investigator and Markdown download can remain available where feasible.
4. Reuse cached evidence, avoid repeated openFDA calls, and retain query URLs/timestamps in reports.
5. Display retrieved-versus-matching counts and coverage limitations prominently, particularly medication errors (500/7,078).
6. Test repeated node-setting changes, reruns, download after graph failure, cloud reboot/recovery, and regression of all existing tabs.
7. Preserve V1.0.4 and older branches; create a separate V1.0.4.1 testing branch only after patch validation and explicit deployment authorization.

**Acceptance status:** V1.0.4.1 code, tests, and deployment are pending. V1.0.4 is restored but not yet stability-certified. October 30 conference demo readiness remains conditional on representative cloud acceptance tests.

### Collaboration and continuity protocol

Before asking the user to repeat a step or re-upload an artifact, check existing conversation attachments, Project files, and available local files. Use the most recent validated artifact and retain version/branch specificity. Give exact one-step-at-a-time UI instructions, based on the UI actually shown; do not send the user to nonexistent Streamlit **Logs** menu options or Settings paths. Clearly separate **observed**, **tested**, **proposed**, and **not yet done**. Do not imply background execution or cloud changes without tool evidence.

### V1.0.4.1 local corrective build — 2026-10-26/27

Created a separate local candidate package based on the V1.0.4 ZIP. `app.py` now places Markdown/JSON/HTML downloads before the optional graph, wraps graph rendering in an exception boundary, uses an Apply Graph Settings form, and limits each of four evidence layers to 15 displayed records. GraphML export remains available only on successful graph construction. No evidence-retrieval algorithms or existing source data were changed. A regression test was added. **Local automated checks: 20 tests passed; Python compilation passed.** No Streamlit Cloud deployment, live API validation, or actual reproduction of the original crash was performed. The cause of the crash remains unconfirmed; process-level resource failures may not be caught by Python exceptions. Preserve V1.0.4 and all earlier deployments. Deploy to a separate `v1.0.4.1-testing` branch and new app only after user confirmation.

---
## Operational update — 2026-10-27 — V1.0.8 verified and V1.0.9 planned / local build

### Confirmed V1.0.8 automation milestone (user-observed)
- GitHub repository: `CRMP-25/medsafe-ai-intelligence`.
- `v1.0.8-testing` published with GitHub Actions CI; user observed a green `MedSafe CI` run and its `validate` job, including checkout, Python setup, dependencies, compilation, deterministic tests and deterministic report fixture validation. The green check does not independently establish clinical correctness or live FDA integration.
- Permanent GitHub branch `testing` created from `v1.0.8-testing`; existing versioned branches preserved.
- Permanent Streamlit app: `https://medsafe-ai-testing.streamlit.app`, repository branch `testing`, entry point `app.py`, Python 3.11; user verified app loaded.
- End-to-end redeployment test: banner changed to `AUTO-DEPLOY TEST` on `v1.0.8-testing`; CI passed; change merged into `testing`, pushed, and user observed the new banner on the same Streamlit URL. Thus automatic branch-following deployment was demonstrated.
- Automatic **promotion** is NOT implemented: review and merge are manual. Existing optional `scripts/promote_testing.sh` is fast-forward-only and may refuse merge-commit histories. Do not force push.
- The test banner is to be removed as part of V1.0.9, not as a separate cleanup release.

### Long-term objective
An expandable, evidence-grounded medication safety knowledge graph with explainable typed relationships, provenance and uncertainty. Current co-reporting is NOT causal evidence, comparative risk, incidence or a validated safety signal.

### Carried-forward improvement register (do not silently drop)
| ID | Capability | Priority | Status as of V1.0.9 planning |
|---|---|---|---|
| M01 | Semantic biomedical graph and typed relationships | Critical | Partial: evidence-derived types and co-mentions; clinical semantics pending |
| M02 | Entity normalization and synonyms | Critical | V1.0.9 initial conservative text-variant review; ontology synonyms pending |
| M03 | Complete evidence-backed relationships | Critical | V1.0.7 full provenance export; V1.0.9 relationship drilldown |
| M04 | Evidence strength and defensible association measures | Critical | Support counts only; denominators/statistical validation pending |
| M05 | Explainable interactive graph investigation | High | V1.0.9 selected co-reporting drilldown; full graph interaction pending |
| M06 | Persistent growth across sessions | High | Manual JSON export/import only; durable backend pending |
| M07 | Structured automated interpretation and reports | High | Existing deterministic HTML/Markdown/ZIP; richer research narrative pending |
| M08 | FDA pagination, deduplication, completeness and date filtering | High | Partial retrieval and coverage disclosure; strengthening pending |
| M09 | Medication error taxonomy and structured extraction | High | Narrow term search; validated taxonomy pending |
| M10 | Longitudinal safety reporting analysis | Medium | Historical partial functions; validated temporal aggregation pending |
| M11 | Validated signal/disproportionality analysis | High | Pending verified case-level contingency denominators |
| M12 | Development automation and release safety | High | CI and stable Streamlit deployment verified; automated promotion pending |

### V1.0.9 local candidate scope (not yet GitHub-published or cloud-tested)
- `intelligence_v109.py`: conservative same-kind text normalization (case, whitespace, terminal period), **review only**; no source-graph rewriting or biomedical synonym assertion.
- Evidence drilldown reconstructs supporting medication-error record IDs and URLs for a selected co-reporting pair, with counts checked against existing association output.
- New UI for relationship explanation and normalization candidates; JSON downloads for each; existing comprehensive V1.0.7 ZIP unchanged.
- Banner updated to `V1.0.9-testing` and temporary AUTO-DEPLOY TEST removed.
- `tests/test_v109.py` added; CI module compilation updated. Local test results must be recorded separately after execution.

### Version promotion plan and release gates
1. Base new `v1.0.9-testing` branch on **permanent `testing`** (not `main` or a stale version branch).
2. Apply only intended V1.0.9 files and documentation; preserve all working V1.0.8 features.
3. Require passing deterministic CI and manual UI inspection; verify record-count parity, no fabricated evidence and complete source URLs.
4. Merge approved candidate into permanent `testing`; verify same Streamlit URL updates; keep older deployments intact.
5. Record observed results and unresolved defects in this file on every release.

### Scientific / engineering nonclaims
No live FDA integration test, external API freshness check, clinical terminology validation, causal inference, durable server-side storage or cloud deployment of V1.0.9 has been performed at the time this entry was drafted.


### V1.0.9 acceptance observations and V1.0.10 candidate (2026-10-27)
- User confirmed stable testing deployment, CI green, evidence explorer, and normalization review.
- Relationship export for `OVERDOSE` (adverse_event) and `death` (serious_outcome) declared 143 supporting retrieved medication-error reports with report IDs and FDA source URLs; this is co-reporting only, not causation or patient incidence.
- Numeric concept `1` in `OVERDOSE` associations is typed `reported_sex_code`, so it is not necessarily an extraction error. Its display is ambiguous; FDA sex code 1 denotes male. Preserve raw code and provenance.
- Normalization review reported 45 candidate groups; seven user-reviewed `reported_medication` examples were terminal-period variants, not clinical synonym equivalence. No graph mutation.
- User provided comprehensive investigation ZIP named `complete_v107`; earlier assistant reported 2,063 nodes, 7,666 edges, 29,771 associations, and 647 evidence records, with 500/7,078 medication-error records retrieved (about 7.1%). These figures are historical snapshot findings and require re-validation for new investigations.
- V1.0.10 candidate adds display-only sex-code decoding, medication label presentation, bounded selectable medication-error retrieval caps, retrieval coverage audit, corrected complete ZIP version label, normalization review in ZIP, and deterministic tests. No claim of deployed V1.0.10 or live FDA API validation.
- Outstanding: inspect all 45 candidate groups; verify all FDA source links and report semantics independently; investigate scalability at larger retrieval caps; controlled clinical ontology mapping, meaningful relationship categorization, durable graph persistence, validated case-level deduplication and signal analysis.


### V1.0.11 conference-readiness candidate (2026-10-27)
- User requests one complete investigation ZIP download at the absolute bottom of the **Main** tab, which also retains the 20 intelligence questions; no duplicate ZIP button in Living Knowledge Graph.
- Source inspection confirmed `semantic_graph(inv, limit_per_kind=500)` silently truncated each evidence source to 500 records even when 1,000 medication-error reports were retrieved. The V1.0.11 candidate removes this internal truncation. This explains the V1.0.10 500-vs-1,000 graph discrepancy, subject to fresh live validation.
- Graph now uses active investigation snapshot, resets after a new retrieval, and Main tab can create its ZIP without visiting Living Knowledge Graph.
- Export version manifest and filename updated to V1.0.11. Existing semantic graph persistence remains session-only; external JSON merge supported.
- Scientific safeguards: retrieval coverage remains partial; co-reporting is not causal or incidence; graph count can grow substantially and requires performance evaluation at higher retrieval caps.
- Status: local candidate only; GitHub CI, Streamlit deployment, and live FDA acceptance pending.
