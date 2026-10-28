# MedSafe V1.0.11 — conference-readiness patch

- Main tab is the first tab, retaining all 20 intelligence questions.
- Single complete investigation ZIP download is the final section of the Main tab; removed from Living Knowledge Graph.
- ZIP is generated from the active investigation, even before the Living Knowledge Graph tab is opened.
- Full semantic graph processes **all retrieved records** instead of silently truncating each source at 500. The on-screen graph remains a bounded visualization.
- A new investigation resets prior graph state; explicit portable graph import remains supported in Living Knowledge Graph.
- ZIP filename and manifest show V1.0.11.
- Retrieval remains partial and bounded by user-selected FDA caps. Graph counts are noncausal and not incidence.
- Validate 1,000-record run using a fresh investigation and compare ZIP evidence record distribution with retrieval audit.

## Deployment
Create `v1.0.11-testing` **based on** permanent `testing`; apply patch; commit and publish; wait for CI; merge into `testing` and push; verify stable Streamlit testing URL.
