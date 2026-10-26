# MedSafe AI Intelligence V1.0.1

Independent Streamlit app, inspired by verified architectural patterns in Kerendia V7.7.11. No Kerendia files are modified or copied into this release.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Test

```bash
python -m pytest -q
```

## Changes

- Annual FAERS receipt-date visualization with explicit incomplete-data warning.
- Expanded selected medication-error MedDRA search and deterministic categorization.
- Evidence-gated deterministic investigator, no LLM API needed.
- Downloadable printable HTML report with clickable provenance URLs.
- New regression tests and updated `PROJECT_MASTER.md`.

## Known limitations

Live API requests are not validated in this offline build. FAERS trends may truncate after 1000 date buckets. Counts are reports, not rates. ROR/PRR example cells are synthetic and must not be described as observed signals. FDA labeling and recalls require review of current source documents. Never use this demo for clinical decisions.
