# MedSafe V1.0.11.1 testing — conference stabilization

This small update centralizes application version metadata. `version.py` supplies `APP_VERSION` and `EXPORT_TAG` to the Streamlit banner, complete ZIP filename and manifest. It also adds regression tests.

**Known issue:** V1.0.11 source code already declared 1.0.11 in its manifest, but a user-generated runtime ZIP declared 1.0.10. The cause has not been verified. This patch reduces the risk of future drift; validate the actual deployed runtime after merge.

**Expected ZIP:** `medsafe_buprenorphine_complete_v1111.zip`, with `manifest.json` application version `1.0.11.1-testing`.

Do not interpret FAERS co-reporting as causality, incidence or comparative risk. Retrieval remains incomplete.
