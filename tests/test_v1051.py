from pathlib import Path

def test_living_graph_has_actionable_button():
    source=Path(__file__).resolve().parents[1].joinpath('app.py').read_text()
    assert "st.button('Run investigation and build knowledge graph'" in source
    assert 'run_shared_investigation(drug)' in source
    assert "st.session_state['investigation']" in source

def test_shared_retrieval_uses_all_four_layers():
    source=Path(__file__).resolve().parents[1].joinpath('app.py').read_text()
    assert "for kind in ['events','errors','labels','recalls']" in source
