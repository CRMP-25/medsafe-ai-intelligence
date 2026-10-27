"""V1.0.10 presentation-only labels and retrieval audit; preserve raw evidence."""
from intelligence_v109 import canonical_label

SEX_CODES = {'0': 'Unknown', '1': 'Male', '2': 'Female'}

def display_label(value, kind):
    raw = str(value)
    if kind == 'reported_sex_code':
        return f"Patient sex: {SEX_CODES.get(raw, 'Unrecognized code')} (code {raw})"
    if kind in ('reported_medication', 'label_medication'):
        return canonical_label(raw).upper()
    return raw

def display_association(row):
    result = dict(row)
    result['concept_a'] = display_label(row['concept_a'], row['type_a'])
    result['concept_b'] = display_label(row['concept_b'], row['type_b'])
    return result

def retrieval_audit(inv):
    out = {}
    for kind, payload in (inv.get('evidence') or {}).items():
        if not isinstance(payload, dict):
            continue
        total = payload.get('total')
        retrieved = len(payload.get('results') or [])
        out[kind] = {
            'retrieved': retrieved, 'provider_total': total,
            'coverage_percent': round(100 * retrieved / total, 2) if isinstance(total, int) and total > 0 else None,
            'complete': payload.get('complete'), 'error': payload.get('error'),
            'pages': len(payload.get('pages') or []), 'query': payload.get('query'),
            'retrieved_utc': payload.get('retrieved_utc'),
        }
    return out
