"""Prevent app/banner/export version drift."""
import ast, io, json, zipfile
from pathlib import Path
from version import APP_VERSION, EXPORT_TAG
from reporting_v107 import complete_report_zip
import networkx as nx

def test_manifest_matches_central_version():
    inv={"drug":"example","evidence":{}}
    with zipfile.ZipFile(io.BytesIO(complete_report_zip(inv,nx.DiGraph(),"example"))) as z:
        assert json.loads(z.read("manifest.json"))["application_version"] == APP_VERSION

def test_banner_and_filename_use_same_version_module():
    app=Path(__file__).resolve().parents[1].joinpath("app.py").read_text()
    ast.parse(app)
    assert "MedSafe AI Intelligence · V{APP_VERSION}" in app
    assert "complete_{EXPORT_TAG}.zip" in app
    assert EXPORT_TAG == "v1111"
