# MedSafe AI Intelligence V1.0.6-testing

Builds on V1.0.5.1. Adds conservative semantic entity extraction from retrieved openFDA records, within-record co-mention analysis with report-specific source links, and JSON graph export/import for continued growth across sessions. No biological mechanisms or causality are inferred. Co-mention counts are limited to retrieved reports, may contain duplicates, and are not incidence or risk measures.

**Persistence:** graph is retained in Streamlit session state during the session. Streamlit Community Cloud ephemeral storage is not a durable graph database. For cross-session continuity, download and later re-upload the graph JSON. A durable multi-user database and scheduled ingestion remain future work.
