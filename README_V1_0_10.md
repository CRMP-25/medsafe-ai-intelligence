# MedSafe V1.0.10-testing — candidate

Changes: display-only decoding of patient sex codes (0 Unknown, 1 Male, 2 Female); presentation-only conservative medication-label formatting; user-selectable bounded medication-error retrieval caps (500/1000/2000/5000); explicit retrieval audit in the living graph; synchronized comprehensive ZIP filename, manifest application version, and included normalization review. Original graph nodes, report IDs, and raw association exports remain unchanged.

Scientific cautions: openFDA FAERS co-mentions do not establish causality, incidence, comparative risk, or a safety signal. Larger retrieval caps are not complete coverage guarantees; FDA API restrictions and latency apply. These changes do not implement validated clinical synonym mapping, deduplication across all reporting versions, or durable graph storage.

Release gate: run deterministic tests and CI; test at 500 records first; inspect provenance, memory use, and API errors before testing larger caps. Merge into permanent testing only after review.
