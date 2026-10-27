"""MedSafe V1.0.9: conservative normalization and explainable co-reporting.

No medical causality, incidence, risk, or ontology-equivalence inference.
"""
import re
from collections import defaultdict


def canonical_label(value):
    """Only typography normalization: whitespace, case, and terminal punctuation."""
    text = re.sub(r'\s+', ' ', str(value or '').strip()).casefold()
    return re.sub(r'[.\s]+$', '', text)


def canonical_groups(graph):
    """Group same-kind graph concepts by a conservative text key.

    Different entity kinds are never merged, and graph itself is unchanged.
    """
    groups = defaultdict(list)
    for node, attrs in graph.nodes(data=True):
        kind = attrs.get('kind', '')
        if kind in ('record', 'reported_age', 'reported_sex_code', 'label_section'):
            continue
        label = attrs.get('label', '')
        norm = canonical_label(label)
        if norm:
            groups[(kind, norm)].append({'node_id': node, 'original_label': label})
    return [
        {'entity_type': kind, 'canonical_label': norm,
         'variants': sorted({x['original_label'] for x in members}),
         'node_ids': [x['node_id'] for x in members], 'node_count': len(members),
         'normalization': 'case, whitespace, terminal-period only'}
        for (kind, norm), members in sorted(groups.items())
        if len(members) > 1
    ]


def explain_association(graph, concept_a, type_a, concept_b, type_b):
    """Reconstruct supporting source records directly from record_mentions edges.

    Only medication-error records are included, consistent with V1.0.7 associations.
    """
    ids_a = {n for n, d in graph.nodes(data=True)
             if d.get('kind') == type_a and d.get('label') == concept_a}
    ids_b = {n for n, d in graph.nodes(data=True)
             if d.get('kind') == type_b and d.get('label') == concept_b}
    matches = []
    for n, d in graph.nodes(data=True):
        if d.get('kind') != 'record' or d.get('source_kind') != 'errors':
            continue
        successors = set(graph.successors(n))
        if successors.intersection(ids_a) and successors.intersection(ids_b):
            matches.append({'record_id': d.get('source_id', ''),
                            'source_url': d.get('source_url', ''),
                            'record_node': n})
    matches.sort(key=lambda x: (str(x['record_id']), x['record_node']))
    return {
        'concept_a': concept_a, 'type_a': type_a,
        'concept_b': concept_b, 'type_b': type_b,
        'relationship': 'co_reported_in_retrieved_medication_error_record',
        'supporting_records': len(matches), 'evidence_records': matches,
        'interpretation': 'Co-reporting only; not causality, incidence, relative risk, or a validated safety signal.',
        'scope': 'Only medication-error records retrieved in this investigation; incomplete coverage possible.',
    }
