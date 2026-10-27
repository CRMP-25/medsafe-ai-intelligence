from pathlib import Path
from reporting_v104 import build_evidence_graph


def test_graph_bound():
    inv={'drug':'testdrug','evidence':{kind:{'results':[{'term':str(i)} for i in range(200)]} for kind in ('events','errors','labels','recalls')}}
    graph=build_evidence_graph(inv,max_per_kind=15)
    assert graph.number_of_nodes() <= 65


def test_report_exports_before_graph_and_apply_form():
    source=Path(__file__).resolve().parents[1].joinpath('app.py').read_text()
    assert source.index('Download comprehensive Markdown evidence report') < source.index('g=render_investigation_graph(inv,')
    assert "st.form('graph_settings_form_v1041')" in source
    assert "st.form_submit_button('Apply Graph Settings')" in source
    assert "max_value=15" in source
    assert 'except Exception as graph_exc:' in source
