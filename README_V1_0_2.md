# MedSafe AI Intelligence V1.0.2-testing

Fixes annual reporting trend query (replaces `count=receivedate` with independent bounded yearly FAERS queries), improves HTTP handling and missing-data disclosure, updates version, and adds regression tests.

**Deploy:** Copy the files inside `medsafe_v1/` into the root of the existing `CRMP-25/medsafe-ai-intelligence` repository on a NEW branch `v1.0.2-testing` based on `v1.0.1-testing`. Deploy Streamlit from `v1.0.2-testing`, main file `app.py`, Python 3.11. Do not modify Kerendia.

**Limitations:** The openFDA endpoints have not been live-tested here. Reporting trends are report counts, not incidence; annual queries can fail independently. Medication-error screens are not comprehensive. ROR/PRR prefilled inputs are synthetic, never inferred from bar chart aggregates. Review and verify all four tabs and downloads before the conference.
