# MedSafe AI Intelligence V1.0.4-testing

Built on V1.0.3. Preserves the existing live openFDA queries, transparent retrieval caps, annual trend, and safety caveats.

## Improvements

- FDA labeling: searchable/filterable table, boxed-warning filter, one selected label detail panel, and direct source link.
- Agentic Safety Investigator: evidence-layer controls, bounded node counts, hierarchical medication/category/record graph, record inspection with source query link.
- New Markdown export: retrieval completeness, source query/page provenance, summaries of **every retrieved** event aggregate, medication-error report, label, and recall; links to FDA record queries; limitations.
- JSON export remains the full retrieved investigation payload. GraphML and HTML exports remain available.

## Important constraints

- Markdown is complete only **for retrieved records**; retrieval may be capped. It does not claim to cover all matching FDA records.
- A graph edge indicates evidence membership or co-reporting, never clinical causality.
- Records in the graph are a selectable subset of the retrieved evidence. Markdown and JSON are not restricted by graph node limits.
- An openFDA record-specific search URL is a query, not a permanent immutable record permalink.
- Live FDA API retrieval and Streamlit browser behavior must be checked after deployment.

## Run

`streamlit run app.py`

## Test

`pytest -q`
