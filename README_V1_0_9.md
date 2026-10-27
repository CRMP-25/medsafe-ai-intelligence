# MedSafe V1.0.9 — Explainable evidence relationships (initial increment)

## Implemented
- New `intelligence_v109.py`: conservative, non-destructive text normalization review within each graph entity type; explicit co-report evidence drilldown for a selected association.
- Living Knowledge Graph: top-100 association selector, evidence-record IDs and source URLs, evidence JSON export, normalization-review table and JSON export.
- CI compilation includes the new module; deterministic regression tests cover normalization and explanation.
- Banner updated to V1.0.9-testing; the temporary AUTO-DEPLOY TEST marker is absent.

## Deliberately not claimed
- No clinical ontology linking, synonyms, causal biomedical edges, causal inference, signal validation, durable server-side graph persistence, or new API retrieval completeness.
- Existing V1.0.7 full ZIP remains intact and retains its original v107 filename. The new relationship and normalization exports are separate.
- Existing source graph is not rewritten by normalization; candidate groups are for investigator review only.

## Deployment
Create `v1.0.9-testing` **based on** the permanent `testing` branch, copy this release's changed files, run CI, then merge into `testing` only after successful validation. The permanent Streamlit URL is `https://medsafe-ai-testing.streamlit.app`. Do not create a versioned Streamlit app.
