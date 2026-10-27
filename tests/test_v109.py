import networkx as nx
from intelligence_v109 import canonical_label, canonical_groups, explain_association


def test_typography_normalization_only():
    assert canonical_label(' BUPRENORPHINE. ') == canonical_label('buprenorphine')
    assert canonical_label('buprenorphine hydrochloride') != canonical_label('buprenorphine')


def test_groups_do_not_cross_entity_types_or_mutate_graph():
    g = nx.DiGraph()
    g.add_node('a', kind='reported_medication', label='BUPRENORPHINE.')
    g.add_node('b', kind='reported_medication', label='buprenorphine')
    g.add_node('c', kind='drug', label='buprenorphine')
    before = g.number_of_nodes()
    groups = canonical_groups(g)
    assert len(groups) == 1 and groups[0]['node_count'] == 2
    assert g.number_of_nodes() == before


def test_explanation_only_counts_source_records_with_both_concepts():
    g = nx.DiGraph()
    g.add_node('a', kind='adverse_event', label='OVERDOSE')
    g.add_node('b', kind='serious_outcome', label='death')
    for idx, source_kind, both in [(1, 'errors', True), (2, 'errors', False), (3, 'labels', True)]:
        r = f'r{idx}'
        g.add_node(r, kind='record', source_kind=source_kind, source_id=str(idx), source_url=f'https://example.org/{idx}')
        g.add_edge(r, 'a')
        if both: g.add_edge(r, 'b')
    result = explain_association(g, 'OVERDOSE', 'adverse_event', 'death', 'serious_outcome')
    assert result['supporting_records'] == 1
    assert result['evidence_records'][0]['record_id'] == '1'
    assert 'not causality' in result['interpretation'].lower()


def test_no_evidence_is_not_invented():
    assert explain_association(nx.DiGraph(), 'x', 'drug', 'y', 'adverse_event')['supporting_records'] == 0
