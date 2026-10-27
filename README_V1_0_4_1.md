# MedSafe V1.0.4.1 — graph stability patch (testing only)

Based on the original V1.0.4 package. Keeps retrieval, evidence, and reports unchanged.

- Graph controls now live inside an explicit Apply Graph Settings form.
- Maximum records per layer reduced to 15 (60 record nodes maximum across four layers).
- Graph rendering is isolated in a try/except so report downloads are shown first and remain available after a graph error.
- Markdown, JSON, and HTML exports are not dependent on graph construction.
- GraphML export is available only when graph construction succeeds.

This is a defensive stability improvement, **not** proof of the original crash cause or a guarantee against process-level out-of-memory termination. No live cloud test has been run.

Deployment: create `v1.0.4.1-testing` based on `v1.0.4-testing`, copy only the changed/new files, and deploy to a NEW Streamlit app; do not modify V1.0.4 or older deployments.
