# MedSafe AI Intelligence V1.0.5.1-testing

Hotfix to V1.0.5: Living Knowledge Graph now provides a working **Run investigation and build knowledge graph** button when the browser session has no current investigation for the selected medication. Both tabs call the same investigation retrieval function and share the result through Streamlit session state. The graph tab also supports refreshing evidence. Existing evidence exports and bounded graph visualization remain unchanged.

**Important:** Streamlit session state is per browser session, not durable storage. A browser reconnect, new session, or app restart may require rerunning the investigation. This release does not add permanent graph storage or biomedical causal inference.
