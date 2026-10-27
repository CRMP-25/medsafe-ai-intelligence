# MedSafe AI Intelligence V1.0.3-testing

## Changes
- Bounded multi-page openFDA retrieval for medication errors (500 max), FDA labels (100 max), and recalls (500 max).
- Display provider matching total separately from retrieved records and flag incomplete results.
- Show page-level provenance, retrieval errors, and report-ID deduplication (with latest version preference).
- Add readable recall dates and recall status filter.
- Add typed evidence-source and record nodes to investigation graph; no causal relationships implied.
- Include provider totals and completeness in printable report.

## Limitations
FAERS is spontaneous reporting and does not establish incidence, causality or comparative risk. Query terms are not exhaustive. Provider totals are query matches, not deduplicated patients. Retrieval caps remain and are disclosed. 2026 is a partial year. No clinical recommendations.

## Deployment
Upload source files to a new `v1.0.3-testing` GitHub branch **based on `v1.0.2-testing`**. Deploy a separate Streamlit app from `app.py`, Python 3.11. Keep V1.0.2 live until V1.0.3 passes UI tests.
