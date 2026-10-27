# MedSafe V1.0.5-testing

Based on supplied V1.0.4.1 source. Adds a first tab with 20 investigative questions and a separate evidence-linked concept graph with bounded neighborhood visualization, 1–6 hop path exploration, source-linked edges and full GraphML export. Graph derived from retrieved evidence is NOT persisted across app restarts; future persistent expansion, biomedical ontologies, PubMed, clinical trials, and hypothesis ranking are NOT implemented. Selected questions are stored in session state, but the existing deterministic investigation does not yet tailor its retrieval to a question. Do not interpret graph paths as causality. No changes were made to deployed apps.

Validation: Python compileall and 20 existing pytest tests passed locally. Cloud UI and live FDA retrieval not verified. Test in a new testing branch, preserving previous branches.
